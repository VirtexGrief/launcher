import hashlib
import os
import subprocess
import uuid
from pathlib import Path
from typing import Callable, Optional

import minecraft_launcher_lib

from virtex_launcher import config


class LauncherError(RuntimeError):
    pass


# ---------- Отдельная игра/инжектор ----------
def launch_game() -> None:
    if not config.GAME_EXE.exists():
        raise LauncherError(f"Файл не найден:\n{config.GAME_EXE}")
    try:
        subprocess.Popen([str(config.GAME_EXE)], cwd=str(config.BASE_DIR))
    except OSError as e:
        raise LauncherError(str(e)) from e


# ---------- Minecraft 1.16.5 ----------
def launch_minecraft(
    nickname: Optional[str] = None,
    version: Optional[str] = None,
    loader: Optional[str] = None,
    progress: Optional[Callable[[str, int], None]] = None,
) -> None:
    nickname = (nickname or config.NICKNAME).strip()
    version = version or config.MINECRAFT_VERSION
    loader = loader or config.MINECRAFT_LOADER

    if not nickname:
        raise LauncherError("Не указан ник.")

    mc_dir = str(config.MINECRAFT_DIR)
    config.MINECRAFT_DIR.mkdir(parents=True, exist_ok=True)

    # 1) убедиться, что Java есть
    java_path = _ensure_java(mc_dir, progress)

    # 2) установить версию (vanilla + fabric поверх)
    try:
        actual_version = _ensure_version(version, loader, mc_dir, progress)
    except Exception as e:  # noqa: BLE001
        raise LauncherError(f"Не удалось установить версию: {e}") from e

    # 3) опции запуска
    options = {
        "username": nickname,
        "uuid": _offline_uuid(nickname),
        "token": "",
        "executablePath": java_path,          # ← принудительно наш Java
        "jvmArguments": list(config.JVM_ARGS),
    }

    try:
        cmd = minecraft_launcher_lib.command.get_minecraft_command(
            actual_version, mc_dir, options
        )
    except Exception as e:  # noqa: BLE001
        raise LauncherError(f"Не удалось собрать команду запуска: {e}") from e

    if progress:
        progress("Запуск Minecraft 1.16.5...", 100)
    try:
        subprocess.Popen(cmd, cwd=mc_dir)
    except OSError as e:
        raise LauncherError(f"Не удалось запустить Minecraft: {e}") from e


# ---------- Java ----------
def _ensure_java(
    mc_dir: str,
    progress: Optional[Callable[[str, int], None]],
) -> str:
    """
    Возвращает путь до javaw.exe.
    1) Если в config.JAVA_PATH_OVERRIDE задан — используем его.
    2) Иначе — пробуем системный Java 16+ из PATH/JAVA_HOME.
    3) Иначе — ставим Java через minecraft_launcher_lib (runtime-gamma ≈ 17).
    """
    # 1) override
    if config.JAVA_PATH_OVERRIDE:
        p = Path(config.JAVA_PATH_OVERRIDE)
        if p.exists():
            return str(p)
        raise LauncherError(f"JAVA_PATH_OVERRIDE указан, но файл не найден: {p}")

    # 2) системный Java
    for cand in _candidate_java_paths():
        if cand:
            return cand

    # 3) автоматическая установка
    if progress:
        progress("Установка Java (нужна для 1.16.5)...", -1)
    try:
        cb = {
            "setStatus": lambda s: progress and progress(str(s), -1),
            "setProgress": lambda p: progress and progress("", int(p)),
            "setMax": lambda m: None,
        }
        minecraft_launcher_lib.java.install_jvm_runtime(
            config.JAVA_VERSION, mc_dir, callback=cb
        )
    except Exception as e:  # noqa: BLE001
        raise LauncherError(
            f"Не удалось установить Java автоматически: {e}\n\n"
            f"Скачай JDK 16 вручную (adoptium.net) и укажи путь в config.JAVA_PATH_OVERRIDE."
        ) from e

    # путь, куда MLL ставит JDK
    found = _find_javaw(mc_dir)
    if not found:
        raise LauncherError(
            "Java установлена, но javaw.exe не найден. "
            "Укажи путь вручную через config.JAVA_PATH_OVERRIDE."
        )
    return found


def _candidate_java_paths() -> list[str]:
    result: list[str] = []

    # JAVA_HOME
    jh = os.environ.get("JAVA_HOME")
    if jh:
        for name in ("javaw.exe", "java.exe"):
            p = Path(jh) / "bin" / name
            if p.exists():
                result.append(str(p))

    # стандартные пути Windows
    for base in (
        r"C:\Program Files\Java",
        r"C:\Program Files\Eclipse Adoptium",
        r"C:\Program Files\Microsoft",
        r"C:\Program Files\BellSoft",
    ):
        b = Path(base)
        if b.exists():
            for sub in b.iterdir():
                for name in ("javaw.exe", "java.exe"):
                    p = sub / "bin" / name
                    if p.exists():
                        result.append(str(p))

    return result


def _find_javaw(mc_dir: str) -> Optional[str]:
    root = Path(mc_dir) / "runtime"
    if not root.exists():
        return None
    for p in root.rglob("javaw.exe"):
        return str(p)
    for p in root.rglob("java.exe"):
        return str(p)
    return None


# ---------- Установка версии / Fabric ----------
def _ensure_version(
    version: str,
    loader: str,
    mc_dir: str,
    progress: Optional[Callable[[str, int], None]],
) -> str:
    cb = _make_callback(progress)

    if loader == "fabric":
        if progress:
            progress("Установка Fabric для 1.16.5...", -1)
        return minecraft_launcher_lib.fabric.install_fabric(
            version, mc_dir, callback=cb
        )
    else:
        if progress:
            progress("Установка Minecraft 1.16.5...", -1)
        minecraft_launcher_lib.install.install_minecraft_version(
            version, mc_dir, callback=cb
        )
        return version


def _make_callback(progress):
    if progress is None:
        return None
    return {
        "setStatus": lambda s: progress(str(s), -1),
        "setProgress": lambda p: progress("", int(p)),
        "setMax": lambda m: None,
    }


def _offline_uuid(username: str) -> str:
    md5 = hashlib.md5(f"OfflinePlayer:{username}".encode("utf-8")).digest()
    return str(uuid.UUID(bytes=md5, version=3))
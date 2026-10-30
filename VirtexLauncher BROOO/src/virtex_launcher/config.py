import sys
from pathlib import Path

APP_NAME = "VirtexLauncher"
APP_VERSION = "1.0.0"

if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parents[2]

# --- Папки ---
MINECRAFT_DIR = Path.home() / "AppData/Roaming/.minecraft"
MODS_DIR = MINECRAFT_DIR / "mods"
MODS_DIR.mkdir(parents=True, exist_ok=True)

RESOURCES_DIR = Path(__file__).resolve().parent / "resources"
MODS_CACHE = RESOURCES_DIR / "mods.json"

# --- Запуск Minecraft ---
MINECRAFT_VERSION = "1.16.5"
MINECRAFT_LOADER = "fabric"

# Ник по умолчанию (можно поменять в окне лаунчера)
NICKNAME = "VirtexVisualsPLAYER"

# Java 16 — скачивается автоматически при первом запуске
JAVA_VERSION = "java-runtime-gamma"   # в манифесте Mojang = Java 17
# Для чистой Java 16 используем локальный путь, если задан:
JAVA_PATH_OVERRIDE: str | None = None
# пример: r"C:\Program Files\Java\jdk-16.0.2\bin\javaw.exe"

# JVM-флаги для стабильной работы 1.16.5 на Java 16+
JVM_ARGS = [
    "-Xmx2G",
    "-Xms1G",
    "-XX:+UseG1GC",
    "-XX:+ParallelRefProcEnabled",
    "-XX:MaxGCPauseMillis=200",
    "-XX:+UnlockExperimentalVMOptions",
    "-XX:+DisableExplicitGC",
    "-XX:G1NewSizePercent=30",
    "-XX:G1MaxNewSizePercent=40",
    "-XX:G1HeapRegionSize=8M",
    "-XX:G1ReservePercent=20",
    "--add-opens", "java.base/java.lang=ALL-UNNAMED",
    "--add-opens", "java.base/java.util=ALL-UNNAMED",
    "--add-opens", "java.base/java.lang.reflect=ALL-UNNAMED",
]

# --- Своя игра/инжектор (доп. кнопка) ---
GAME_EXE = BASE_DIR / "VirtexVisuals.exe"

# --- Сеть ---
MODS_JSON_URL = "https://raw.githubusercontent.com/yourname/virtex/main/mods.json"
REQUEST_TIMEOUT = 30
CHUNK_SIZE = 64 * 1024
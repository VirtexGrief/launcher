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
NICKNAME = "VirtexVisualsPLAYER"

# Java 16
JAVA_VERSION = "java-runtime-gamma"
JAVA_PATH_OVERRIDE: str | None = None

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

# --- Своя игра/инжектор ---
GAME_EXE = BASE_DIR / "VirtexVisuals.exe"

# --- Сеть ---
# ВОТ ТУТ ТВОЯ ССЫЛКА (Raw-формат для GitHub)
MODS_JSON_URL = "https://raw.githubusercontent.com/VirtexGrief/launcher/launcher/src/virtex_launcher/resources/mods.json"

REQUEST_TIMEOUT = 30
CHUNK_SIZE = 64 * 1024

# Файл для сохранения ника
NICK_FILE = BASE_DIR / "nick.json"
import sys
from pathlib import Path

# Добавляем src/ в путь, чтобы работал импорт virtex_launcher
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from virtex_launcher.__main__ import main

if __name__ == "__main__":
    main()
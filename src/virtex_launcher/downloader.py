import shutil
import tempfile
import zipfile
from pathlib import Path

import requests
from PyQt6.QtCore import QThread, pyqtSignal

from virtex_launcher import config
from virtex_launcher.mods import Mod


class DownloadThread(QThread):
    progress = pyqtSignal(int)
    finished_ok = pyqtSignal(str)
    failed = pyqtSignal(str)

    def __init__(self, mod: Mod) -> None:
        super().__init__()
        self.mod = mod

    def run(self) -> None:
        try:
            target = config.MODS_DIR / self.mod.id
            if target.exists():
                shutil.rmtree(target)
            target.mkdir(parents=True, exist_ok=True)

            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                tmp_path = Path(tmp.name)

            try:
                self._download(self.mod.url, tmp_path)
                with zipfile.ZipFile(tmp_path) as z:
                    z.extractall(target)
            finally:
                tmp_path.unlink(missing_ok=True)

            self.finished_ok.emit(self.mod.name)
        except Exception as e:  # noqa: BLE001
            self.failed.emit(str(e))

    def _download(self, url: str, dest: Path) -> None:
        with requests.get(url, stream=True, timeout=config.REQUEST_TIMEOUT) as r:
            r.raise_for_status()
            total = int(r.headers.get("Content-Length", 0))
            done = 0
            with open(dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=config.CHUNK_SIZE):
                    if not chunk:
                        continue
                    f.write(chunk)
                    done += len(chunk)
                    if total:
                        self.progress.emit(int(done * 100 / total))
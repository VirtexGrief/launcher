import sys

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication, QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMainWindow, QMessageBox, QProgressBar,
    QPushButton, QVBoxLayout, QWidget,
)

from virtex_launcher import APP_NAME, APP_VERSION, config
from virtex_launcher.downloader import DownloadThread
from virtex_launcher.launcher import LauncherError, launch_game, launch_minecraft
from virtex_launcher.mods import Mod, fetch_mods, installed_ids, register_mods

STYLE = """
QWidget { background: #14161c; color: #e6e8ee; font-family: 'Segoe UI'; font-size: 13px; }
QListWidget { background: #1b1e26; border: 1px solid #2a2f3d; border-radius: 10px; padding: 6px; }
QListWidget::item { padding: 10px; border-radius: 8px; }
QListWidget::item:selected { background: #7c3aed; color: white; }
QLineEdit, QComboBox {
    background: #1b1e26; border: 1px solid #2a2f3d; border-radius: 8px;
    padding: 8px 10px; color: #e6e8ee;
}
QComboBox::drop-down { border: none; }
QPushButton { background: #7c3aed; color: white; border: none; border-radius: 8px; padding: 10px 18px; font-weight: 600; }
QPushButton:hover { background: #8b4bf0; }
QPushButton:disabled { background: #3a3f52; color: #888; }
QPushButton#secondary { background: #262a36; }
QPushButton#secondary:hover { background: #333848; }
QProgressBar { background: #1b1e26; border: 1px solid #2a2f3d; border-radius: 6px; text-align: center; height: 18px; }
QProgressBar::chunk { background: #7c3aed; border-radius: 6px; }
QFrame#card { background: #1b1e26; border: 1px solid #2a2f3d; border-radius: 12px; }
"""

POPULAR_VERSIONS = [
    "1.16.5", "1.16.4", "1.16.1", "1.15.2", "1.12.2",
]


class MinecraftLaunchThread(QThread):
    progress = pyqtSignal(str, int)
    finished_ok = pyqtSignal()
    failed = pyqtSignal(str)

    def __init__(self, nickname: str, version: str, loader: str) -> None:
        super().__init__()
        self.nickname = nickname
        self.version = version
        self.loader = loader

    def run(self) -> None:
        try:
            launch_minecraft(
                nickname=self.nickname,
                version=self.version,
                loader=self.loader,
                progress=lambda s, p: self.progress.emit(s, p),
            )
            self.finished_ok.emit()
        except Exception as e:  # noqa: BLE001
            self.failed.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.resize(820, 640)
        self.setStyleSheet(STYLE)

        self._dl_thread: DownloadThread | None = None
        self._mc_thread: MinecraftLaunchThread | None = None

        self._build_ui()
        self._reload_mods()

    # ---------- UI ----------
    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        title = QLabel(f"🔥 {APP_NAME}")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        root.addWidget(title)

        subtitle = QLabel("Лаунчер модов VirtexVisuals + запуск Minecraft 1.16.5")
        subtitle.setStyleSheet("color: #8a90a6;")
        root.addWidget(subtitle)

        # --- Карточка списка модов ---
        card = QFrame()
        card.setObjectName("card")
        card_l = QVBoxLayout(card)
        card_l.setContentsMargins(12, 12, 12, 12)

        self.list = QListWidget()
        card_l.addWidget(self.list)
        root.addWidget(card, stretch=1)

        # --- Прогресс ---
        self.progress = QProgressBar()
        self.progress.setValue(0)
        root.addWidget(self.progress)

        # --- Кнопки работы с модами ---
        mod_buttons = QHBoxLayout()
        self.btn_refresh = QPushButton("Обновить список")
        self.btn_refresh.setObjectName("secondary")
        self.btn_refresh.clicked.connect(self._reload_mods)

        self.btn_download = QPushButton("Скачать выбранный мод")
        self.btn_download.clicked.connect(self._download_selected)

        mod_buttons.addWidget(self.btn_refresh)
        mod_buttons.addWidget(self.btn_download)
        mod_buttons.addStretch()
        root.addLayout(mod_buttons)

        # --- Настройки Minecraft ---
        mc_card = QFrame()
        mc_card.setObjectName("card")
        mc_l = QHBoxLayout(mc_card)
        mc_l.setContentsMargins(12, 12, 12, 12)
        mc_l.setSpacing(10)

        self.nick_input = QLineEdit()
        self.nick_input.setPlaceholderText("Ник")
        self.nick_input.setText(config.NICKNAME)   # "VirtexVisualsPLAYER"
        self.nick_input.setFixedWidth(200)

        self.version_combo = QComboBox()
        self.version_combo.setEditable(True)
        self.version_combo.addItems(POPULAR_VERSIONS)
        self.version_combo.setCurrentText(config.MINECRAFT_VERSION)  # "1.16.5"
        self.version_combo.setFixedWidth(120)

        self.loader_combo = QComboBox()
        self.loader_combo.addItems(["fabric", "vanilla"])
        self.loader_combo.setCurrentText(config.MINECRAFT_LOADER)
        self.loader_combo.setFixedWidth(120)

        self.btn_launch_mc = QPushButton("🚀 Запустить Minecraft")
        self.btn_launch_mc.clicked.connect(self._launch_minecraft)

        mc_l.addWidget(QLabel("Ник:"))
        mc_l.addWidget(self.nick_input)
        mc_l.addWidget(QLabel("Версия:"))
        mc_l.addWidget(self.version_combo)
        mc_l.addWidget(QLabel("Лоадер:"))
        mc_l.addWidget(self.loader_combo)
        mc_l.addStretch()
        mc_l.addWidget(self.btn_launch_mc)
        root.addWidget(mc_card)

        # --- Статус ---
        self.status = QLabel("Готов.")
        self.status.setStyleSheet("color: #8a90a6; font-size: 12px;")
        root.addWidget(self.status)

    # ---------- Моды ----------
    def _reload_mods(self) -> None:
        self.status.setText("Загрузка списка модов...")
        self.list.clear()
        try:
            mods, source = fetch_mods()
        except Exception as e:  # noqa: BLE001
            self.status.setText(f"Не удалось загрузить список: {e}")
            return

        register_mods(mods)
        installed = installed_ids()

        for mod in mods:
            mark = "✅" if mod.id in installed else "⬇️"
            text = f"{mark}  {mod.name}  v{mod.version}\n{mod.description}"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, mod)
            self.list.addItem(item)

        label = {"online": "интернет", "cache": "локальный кэш"}[source]
        self.status.setText(f"Загружено {len(mods)} модов ({label}).")

    def _download_selected(self) -> None:
        item = self.list.currentItem()
        if not item:
            QMessageBox.information(self, "Мод не выбран", "Выбери мод в списке.")
            return

        mod: Mod = item.data(Qt.ItemDataRole.UserRole)
        self.btn_download.setEnabled(False)
        self.progress.setValue(0)
        self.status.setText(f"Скачивание {mod.name}...")

        self._dl_thread = DownloadThread(mod)
        self._dl_thread.progress.connect(self.progress.setValue)
        self._dl_thread.finished_ok.connect(self._on_dl_ok)
        self._dl_thread.failed.connect(self._on_dl_fail)
        self._dl_thread.start()

    def _on_dl_ok(self, name: str) -> None:
        self.btn_download.setEnabled(True)
        self.progress.setValue(100)
        self.status.setText(f"✅ {name} установлен в {config.MODS_DIR}")
        self._reload_mods()

    def _on_dl_fail(self, err: str) -> None:
        self.btn_download.setEnabled(True)
        self.progress.setValue(0)
        self.status.setText(f"❌ Ошибка: {err}")
        QMessageBox.critical(self, "Ошибка скачивания", err)

    # ---------- Запуск Minecraft ----------
    def _launch_minecraft(self) -> None:
        nickname = self.nick_input.text().strip()
        version = self.version_combo.currentText().strip()
        loader = self.loader_combo.currentText().strip()

        if not nickname:
            QMessageBox.warning(self, "Ник пустой", "Введи ник.")
            return
        if not version:
            QMessageBox.warning(self, "Версия пустая", "Введи версию Minecraft.")
            return

        self.btn_launch_mc.setEnabled(False)
        self.progress.setValue(0)

        # ← показываем ник при запуске
        self.status.setText(
            f"Запуск Minecraft | Ник: {nickname} | {version} / {loader}"
        )

        self._mc_thread = MinecraftLaunchThread(nickname, version, loader)
        self._mc_thread.progress.connect(self._on_mc_progress)
        self._mc_thread.finished_ok.connect(self._on_mc_ok)
        self._mc_thread.failed.connect(self._on_mc_fail)
        self._mc_thread.start()

    def _on_mc_progress(self, status: str, percent: int) -> None:
        nickname = self.nick_input.text().strip()
        if status:
            self.status.setText(f"Minecraft | Ник: {nickname} | {status}")
        if percent >= 0:
            self.progress.setValue(min(percent, 100))
        else:
            self.progress.setValue(0)

    def _on_mc_ok(self) -> None:
        self.btn_launch_mc.setEnabled(True)
        self.progress.setValue(100)
        self.status.setText(
            f"✅ Minecraft запущен | Ник: {self.nick_input.text().strip()}"
        )

    def _on_mc_fail(self, err: str) -> None:
        self.btn_launch_mc.setEnabled(True)
        self.progress.setValue(0)
        self.status.setText(f"❌ {err}")
        QMessageBox.critical(self, "Ошибка запуска Minecraft", err)


def run() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
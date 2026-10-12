import os
import sys
import json
import locale
import shutil
import subprocess
import urllib.request
import urllib.error
from pathlib import Path

APP_NAME        = "Clor"
APP_COMMENT     = "Clor — лёгкий браузер на Material Design 3"
DEVELOPER       = "MoonAtikDV"
REPO_RAW        = "https://raw.githubusercontent.com/MoonAtikDV/Clor-Browser/main"
URL_CLOR_PY     = f"{REPO_RAW}/clor.py"
URL_ICON        = f"{REPO_RAW}/icon.png"
URL_MSYMBOL     = ("https://github.com/google/material-design-icons/raw/master/"
                   "variablefont/MaterialSymbolsRounded%5BFILL%2CGRAD%2Copsz%2Cwght%5D.ttf")

HOME            = Path.home()
INSTALL_DIR     = HOME / ".local" / "share" / "clor"
INSTALL_FILE    = INSTALL_DIR / "clor.py"
BIN_DIR         = HOME / ".local" / "bin"
BIN_LINK        = BIN_DIR / "clor"
APPS_DIR        = HOME / ".local" / "share" / "applications"
DESKTOP_FILE    = APPS_DIR / "clor.desktop"
ICONS_DIR       = HOME / ".local" / "share" / "icons" / "hicolor" / "256x256" / "apps"
ICON_FILE       = ICONS_DIR / "clor.png"
FONTS_DIR       = HOME / ".local" / "share" / "fonts"
MSYMBOL_FILE    = FONTS_DIR / "MaterialSymbolsRounded.ttf"

def detect_lang() -> str:
    try:
        loc = (locale.getdefaultlocale()[0] or os.environ.get("LANG", "")).lower()
    except Exception:
        loc = os.environ.get("LANG", "").lower()
    return "ru" if loc.startswith("ru") else "en"

I18N = {
    "en": {
        "title": "Clor Installer",
        "subtitle": "Install and update the Clor browser",
        "btn_install": "Install",
        "btn_update": "Update",
        "btn_uninstall": "Uninstall",
        "btn_close": "Close",
        "status_ready": "Ready.",
        "status_installing": "Installing...",
        "status_updating": "Updating...",
        "status_uninstalling": "Uninstalling...",
        "status_done": "Done.",
        "status_failed": "Failed.",
        "checking_deps": "Checking dependencies...",
        "installing_deps": "Installing PySide6 + WebEngine (this may take a while)...",
        "downloading_clor": "Downloading clor.py from GitHub...",
        "downloading_icon": "Downloading icon...",
        "downloading_font": "Downloading Material Symbols font...",
        "creating_bin": "Creating launcher ~/.local/bin/clor...",
        "creating_desktop": "Creating .desktop entry...",
        "updating_desktop_db": "Updating desktop database...",
        "updating_font_cache": "Updating font cache...",
        "installed_ok": "Clor installed successfully! Run it with: clor",
        "updated_ok": "Clor updated successfully!",
        "uninstalled_ok": "Clor removed.",
        "not_installed": "Clor is not installed.",
        "already_installed": "Clor is already installed.",
        "confirm_uninstall": "Remove Clor, its launcher and .desktop entry?",
        "confirm_title": "Confirm",
        "yes": "Yes", "no": "No",
        "log": "Log",
        "requires_pyside": "PySide6 is required to run the installer GUI.",
        "install_pyside_hint": "Install it with: pip install --user PySide6 PySide6-Addons",
        "error_network": "Network error: ",
        "error_http": "HTTP error: ",
        "language": "Language",
    },
    "ru": {
        "title": "Установщик Clor",
        "subtitle": "Установка и обновление браузера Clor",
        "btn_install": "Установить",
        "btn_update": "Обновить",
        "btn_uninstall": "Удалить",
        "btn_close": "Закрыть",
        "status_ready": "Готово.",
        "status_installing": "Установка...",
        "status_updating": "Обновление...",
        "status_uninstalling": "Удаление...",
        "status_done": "Готово.",
        "status_failed": "Ошибка.",
        "checking_deps": "Проверка зависимостей...",
        "installing_deps": "Установка PySide6 + WebEngine (может занять время)...",
        "downloading_clor": "Скачивание clor.py с GitHub...",
        "downloading_icon": "Скачивание иконки...",
        "downloading_font": "Скачивание шрифта Material Symbols...",
        "creating_bin": "Создание ярлыка ~/.local/bin/clor...",
        "creating_desktop": "Создание .desktop-файла...",
        "updating_desktop_db": "Обновление базы .desktop...",
        "updating_font_cache": "Обновление кэша шрифтов...",
        "installed_ok": "Clor успешно установлен! Запустите командой: clor",
        "updated_ok": "Clor успешно обновлён!",
        "uninstalled_ok": "Clor удалён.",
        "not_installed": "Clor не установлен.",
        "already_installed": "Clor уже установлен.",
        "confirm_uninstall": "Удалить Clor, ярлык и .desktop-файл?",
        "confirm_title": "Подтверждение",
        "yes": "Да", "no": "Нет",
        "log": "Лог",
        "requires_pyside": "Для запуска графического установщика нужен PySide6.",
        "install_pyside_hint": "Установите его командой: pip install --user PySide6 PySide6-Addons",
        "error_network": "Ошибка сети: ",
        "error_http": "Ошибка HTTP: ",
        "language": "Язык",
    },
}

LANG = detect_lang()
def T(key: str) -> str:
    return I18N.get(LANG, I18N["en"]).get(key, key)

def _ensure_pyside():
    try:
        import PySide6  # noqa: F401
        from PySide6.QtWidgets import QApplication  # noqa: F401
    except ImportError:
        print(T("requires_pyside"))
        print(T("install_pyside_hint"))
        print("Auto-installing PySide6...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user",
                                   "PySide6", "PySide6-Addons"])
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception as e:
            print(f"Auto-install failed: {e}")
            sys.exit(1)

_ensure_pyside()

from PySide6.QtCore import Qt, QThread, Signal, QUrl  # noqa: E402
from PySide6.QtGui import QIcon, QFont, QDesktopServices  # noqa: E402
from PySide6.QtWidgets import (  # noqa: E402
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QPlainTextEdit, QProgressBar, QComboBox,
    QMessageBox, QFrame, QSizePolicy
)

def _download(url: str, dst: Path, log=print) -> bool:
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        log(f"→ {url}")
        with urllib.request.urlopen(url, timeout=30) as r, open(dst, "wb") as f:
            shutil.copyfileobj(r, f)
        return True
    except urllib.error.HTTPError as e:
        log(f"HTTP {e.code} for {url}")
    except urllib.error.URLError as e:
        log(f"Network error for {url}: {e.reason}")
    except Exception as e:
        log(f"Download failed for {url}: {e}")
    return False

def _is_installed() -> bool:
    return INSTALL_FILE.exists() and BIN_LINK.exists()

class Worker(QThread):
    log      = Signal(str)
    progress = Signal(int, str)   # 0..100, status
    finished = Signal(bool, str)  # ok, message

    def __init__(self, action: str, parent=None):
        super().__init__(parent)
        self.action = action

    def _step(self, pct: int, status_key: str):
        self.progress.emit(pct, T(status_key))
        self.log.emit(f"[{pct:3d}%] {T(status_key)}")

    def _ensure_dirs(self):
        for d in (INSTALL_DIR, BIN_DIR, APPS_DIR, ICONS_DIR, FONTS_DIR):
            d.mkdir(parents=True, exist_ok=True)

    def _check_pyside_runtime(self) -> bool:
        try:
            import PySide6  # noqa: F401
            from PySide6.QtWebEngineWidgets import QWebEngineView  # noqa: F401
            return True
        except ImportError:
            return False

    def _install_deps(self) -> bool:
        if self._check_pyside_runtime():
            self.log.emit("PySide6 + WebEngine already installed.")
            return True
        self._step(5, "installing_deps")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--user",
                 "PySide6", "PySide6-Addons"],
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            return True
        except subprocess.CalledProcessError as e:
            self.log.emit(f"pip failed: {e}")
            return False

    def _write_bin(self) -> bool:
        self._step(80, "creating_bin")
        try:
            BIN_LINK.parent.mkdir(parents=True, exist_ok=True)
            if BIN_LINK.exists() or BIN_LINK.is_symlink():
                BIN_LINK.unlink()
            BIN_LINK.symlink_to(INSTALL_FILE)
            BIN_LINK.chmod(0o755)
            return True
        except Exception as e:
            self.log.emit(f"bin link failed: {e}")
            return False

    def _write_desktop(self) -> bool:
        self._step(88, "creating_desktop")
        try:
            desktop = (
                "[Desktop Entry]\n"
                "Type=Application\n"
                "Version=1.0\n"
                f"Name={APP_NAME}\n"
                "GenericName=Web Browser\n"
                f"Comment={APP_COMMENT}\n"
                f"Exec={sys.executable} {INSTALL_FILE} %u\n"
                f"Icon={ICON_FILE}\n"
                "Terminal=false\n"
                "Categories=Network;WebBrowser;\n"
                "MimeType=text/html;text/xml;application/xhtml+xml;"
                "x-scheme-handler/http;x-scheme-handler/https;\n"
                "StartupNotify=true\n"
                "StartupWMClass=Clor\n"
            )
            DESKTOP_FILE.parent.mkdir(parents=True, exist_ok=True)
            DESKTOP_FILE.write_text(desktop, encoding="utf-8")
            return True
        except Exception as e:
            self.log.emit(f"desktop failed: {e}")
            return False

    def _update_desktop_db(self):
        self._step(94, "updating_desktop_db")
        try:
            subprocess.Popen(["update-desktop-database", str(APPS_DIR)],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def _update_font_cache(self):
        self._step(97, "updating_font_cache")
        try:
            subprocess.Popen(["fc-cache", "-f"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def run(self):
        try:
            if self.action == "install":
                self._do_install()
            elif self.action == "update":
                self._do_update()
            elif self.action == "uninstall":
                self._do_uninstall()
        except Exception as e:
            self.log.emit(f"Unexpected error: {e}")
            self.finished.emit(False, T("status_failed"))

    def _do_install(self):
        self.log.emit(T("checking_deps"))
        self._ensure_dirs()

        if not self._install_deps():
            self.finished.emit(False, T("status_failed"))
            return

        self._step(20, "downloading_clor")
        if not _download(URL_CLOR_PY, INSTALL_FILE, self.log.emit):
            self.finished.emit(False, T("status_failed"))
            return
        try:
            INSTALL_FILE.chmod(0o755)
        except Exception:
            pass

        self._step(45, "downloading_icon")
        _download(URL_ICON, ICON_FILE, self.log.emit)

        self._step(60, "downloading_font")
        if not MSYMBOL_FILE.exists():
            _download(URL_MSYMBOL, MSYMBOL_FILE, self.log.emit)

        if not self._write_bin():
            self.finished.emit(False, T("status_failed"))
            return
        if not self._write_desktop():
            self.finished.emit(False, T("status_failed"))
            return

        self._update_desktop_db()
        self._update_font_cache()
        self.progress.emit(100, T("status_done"))
        self.finished.emit(True, T("installed_ok"))

    def _do_update(self):
        self.log.emit(T("checking_deps"))
        self._ensure_dirs()

        if not self._install_deps():
            self.finished.emit(False, T("status_failed"))
            return

        self._step(30, "downloading_clor")
        tmp = INSTALL_FILE.with_suffix(".py.new")
        if not _download(URL_CLOR_PY, tmp, self.log.emit):
            self.finished.emit(False, T("status_failed"))
            return
        try:
            if INSTALL_FILE.exists():
                INSTALL_FILE.unlink()
            tmp.rename(INSTALL_FILE)
            INSTALL_FILE.chmod(0o755)
        except Exception as e:
            self.log.emit(f"replace failed: {e}")
            self.finished.emit(False, T("status_failed"))
            return

        self._step(60, "downloading_icon")
        _download(URL_ICON, ICON_FILE, self.log.emit)

        self._step(75, "downloading_font")
        if not MSYMBOL_FILE.exists():
            _download(URL_MSYMBOL, MSYMBOL_FILE, self.log.emit)

        self._write_bin()
        self._write_desktop()
        self._update_desktop_db()
        self._update_font_cache()
        self.progress.emit(100, T("status_done"))
        self.finished.emit(True, T("updated_ok"))

    def _do_uninstall(self):
        self._step(20, "status_uninstalling")
        for p in (INSTALL_FILE, BIN_LINK, DESKTOP_FILE, ICON_FILE):
            try:
                if p.is_symlink() or p.exists():
                    p.unlink()
                    self.log.emit(f"removed: {p}")
            except Exception as e:
                self.log.emit(f"remove {p} failed: {e}")
        try:
            if INSTALL_DIR.exists() and not any(INSTALL_DIR.iterdir()):
                INSTALL_DIR.rmdir()
        except Exception:
            pass
        self._update_desktop_db()
        self.progress.emit(100, T("status_done"))
        self.finished.emit(True, T("uninstalled_ok"))

class InstallerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(T("title"))
        self.setMinimumSize(640, 520)
        self.resize(720, 560)
        self._worker = None
        self._build()
        self._refresh_state()

    def _build(self):
        central = QWidget()
        self.setCentralWidget(central)
        v = QVBoxLayout(central)
        v.setContentsMargins(24, 20, 24, 20)
        v.setSpacing(12)

        title = QLabel(T("title"))
        f = QFont("Open Sans", 20)
        f.setBold(True)
        title.setFont(f)
        v.addWidget(title)

        sub = QLabel(T("subtitle"))
        sub.setStyleSheet("color: palette(mid);")
        v.addWidget(sub)

        lang_row = QHBoxLayout()
        lang_row.addWidget(QLabel(T("language") + ":"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("Русский", "ru")
        self.lang_combo.addItem("English", "en")
        self.lang_combo.setCurrentIndex(0 if LANG == "ru" else 1)
        self.lang_combo.currentIndexChanged.connect(self._change_lang)
        lang_row.addWidget(self.lang_combo)
        lang_row.addStretch(1)
        v.addLayout(lang_row)

        btn_row = QHBoxLayout()
        self.btn_install = QPushButton(T("btn_install"))
        self.btn_update = QPushButton(T("btn_update"))
        self.btn_uninstall = QPushButton(T("btn_uninstall"))
        self.btn_close = QPushButton(T("btn_close"))
        for b in (self.btn_install, self.btn_update, self.btn_uninstall):
            b.setMinimumHeight(38)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.btn_install.clicked.connect(lambda: self._run("install"))
        self.btn_update.clicked.connect(lambda: self._run("update"))
        self.btn_uninstall.clicked.connect(self._confirm_uninstall)
        self.btn_close.clicked.connect(self.close)
        btn_row.addWidget(self.btn_install)
        btn_row.addWidget(self.btn_update)
        btn_row.addWidget(self.btn_uninstall)
        v.addLayout(btn_row)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        v.addWidget(self.progress)

        self.status = QLabel(T("status_ready"))
        self.status.setStyleSheet("color: palette(mid);")
        v.addWidget(self.status)

        log_lbl = QLabel(T("log"))
        v.addWidget(log_lbl)
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("font-family: monospace;")
        v.addWidget(self.log, 1)

        bottom = QHBoxLayout()
        bottom.addStretch(1)
        bottom.addWidget(self.btn_close)
        v.addLayout(bottom)

    def _change_lang(self):
        global LANG
        LANG = self.lang_combo.currentData()
        QMessageBox.information(self, T("title"),
                                "Please restart the installer to apply the language.\n"
                                "Перезапустите установщик, чтобы применить язык.")

    def _refresh_state(self):
        installed = _is_installed()
        self.btn_install.setEnabled(not installed)
        self.btn_update.setEnabled(installed)
        self.btn_uninstall.setEnabled(installed)
        self.btn_install.setToolTip(T("already_installed") if installed else "")
        if installed:
            self.status.setText(T("already_installed"))

    def _set_busy(self, busy: bool):
        for b in (self.btn_install, self.btn_update, self.btn_uninstall):
            b.setEnabled(not busy)
        self.lang_combo.setEnabled(not busy)
        if not busy:
            self._refresh_state()

    def _append_log(self, line: str):
        self.log.appendPlainText(line)
        sb = self.log.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _run(self, action: str):
        if self._worker and self._worker.isRunning():
            return
        self._set_busy(True)
        self.log.clear()
        self.progress.setValue(0)
        self.status.setText(T("status_installing") if action == "install" else
                            T("status_updating") if action == "update" else
                            T("status_uninstalling"))
        self._worker = Worker(action)
        self._worker.log.connect(self._append_log)
        self._worker.progress.connect(lambda p, s: (self.progress.setValue(p), self.status.setText(s)))
        self._worker.finished.connect(self._on_finished)
        self._worker.start()

    def _on_finished(self, ok: bool, msg: str):
        self._set_busy(False)
        self.status.setText(msg)
        self._append_log(msg)
        self._refresh_state()
        QMessageBox.information(self, T("title"), msg) if ok else \
            QMessageBox.critical(self, T("title"), msg)

    def _confirm_uninstall(self):
        box = QMessageBox(self)
        box.setWindowTitle(T("confirm_title"))
        box.setText(T("confirm_uninstall"))
        box.setIcon(QMessageBox.Question)
        yes = box.addButton(T("yes"), QMessageBox.YesRole)
        box.addButton(T("no"), QMessageBox.NoRole)
        box.exec()
        if box.clickedButton() is yes:
            self._run("uninstall")

    def closeEvent(self, e):
        if self._worker and self._worker.isRunning():
            r = QMessageBox.question(self, T("title"),
                                     "Operation in progress. Quit anyway?",
                                     QMessageBox.Yes | QMessageBox.No)
            if r != QMessageBox.Yes:
                e.ignore()
                return
        e.accept()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Clor Installer")
    app.setOrganizationName(DEVELOPER)
    if ICON_FILE.exists():
        app.setWindowIcon(QIcon(str(ICON_FILE)))
    app.setFont(QFont("Open Sans", 10))
    w = InstallerWindow()
    w.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

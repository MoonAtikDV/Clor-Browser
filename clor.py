#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import json
import time
import random
import signal
import locale
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path

def _ensure_pyside():
    try:
        import PySide6
        from PySide6.QtWebEngineWidgets import QWebEngineView
    except ImportError:
        print("[Clor] Installing PySide6 + WebEngine...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user",
                               "PySide6", "PySide6-Addons"])
        os.execv(sys.executable, [sys.executable] + sys.argv)

_ensure_pyside()

from PySide6.QtCore import (
    Qt, Signal, QTimer, QPoint, QUrl, QByteArray, QBuffer, QRect,
    QPropertyAnimation, QEasingCurve, QAbstractAnimation, Property
)
from PySide6.QtGui import (
    QIcon, QFont, QFontDatabase, QColor, QKeySequence, QShortcut, QPixmap,
    QAction, QDesktopServices, QPainter, QBrush, QPainterPath
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QLabel, QPushButton, QListWidget, QListWidgetItem,
    QSlider, QCheckBox, QDialog, QToolButton, QMenu, QFrame,
    QStackedWidget, QScrollArea, QComboBox, QFileDialog, QSizePolicy,
    QGraphicsOpacityEffect, QButtonGroup, QWidgetAction
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import (
    QWebEngineProfile, QWebEnginePage, QWebEngineSettings,
    QWebEngineUrlRequestInterceptor
)

APP_NAME = "Clor"
APP_VERSION = "0.2.7"
ENGINE_NAME = "Clorium 0.3.5"
DEVELOPER = "MoonAtikDV"
HOME = Path.home()

CONFIG_DIR     = HOME / ".config" / "clor"
CONFIG_FILE    = CONFIG_DIR / "config.json"
BOOKMARKS_FILE = CONFIG_DIR / "bookmarks.json"
HISTORY_FILE   = CONFIG_DIR / "history.json"
DOWNLOADS_FILE = CONFIG_DIR / "downloads.json"
SESSION_FILE   = CONFIG_DIR / "session.json"
FAVICONS_FILE  = CONFIG_DIR / "favicons.json"
CACHE_DIR      = CONFIG_DIR / "cache"

BIN_DIR   = HOME / ".local" / "bin"
APPS_DIR  = HOME / ".local" / "share" / "applications"
ICONS_DIR = HOME / ".local" / "share" / "icons" / "hicolor" / "256x256" / "apps"
FONTS_DIR = HOME / ".local" / "share" / "fonts"

ICON_FILE    = ICONS_DIR / "clor.png"
DESKTOP_FILE = APPS_DIR / "clor.desktop"
BIN_LINK     = BIN_DIR / "clor"
MSYMBOL_FILE = FONTS_DIR / "MaterialSymbolsRounded.ttf"

SELF_PATH = Path(__file__).resolve()
ICON_URL = "https://raw.githubusercontent.com/MoonAtikDV/Clor-Browser/main/icon.png"
MSYMBOL_URL = ("https://github.com/google/material-design-icons/raw/master/"
               "variablefont/MaterialSymbolsRounded%5BFILL%2CGRAD%2Copsz%2Cwght%5D.ttf")

GOOGLE_HOME = "https://www.google.com/"
MOBILE_BREAKPOINT = 720
RESIZE_MARGIN = 12
TITLEBAR_HEIGHT = 36
CORNER_RADIUS = 10

ICON_FONT_FAMILY = "Material Symbols Rounded"

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Clor/0.2.7 Chrome/120.0.0.0 Safari/537.36 Clorium/0.3.5"
)

def detect_language():
    try:
        loc = locale.getdefaultlocale()[0] or os.environ.get("LANG", "")
        if loc.lower().startswith("ru"):
            return "ru"
    except Exception:
        pass
    if os.environ.get("LANG", "").lower().startswith("ru"):
        return "ru"
    return "en"

I18N = {
    "en": {"new_tab": "New tab", "search": "Search or type URL", "settings": "Settings",
           "history": "History", "bookmarks": "Bookmarks", "downloads": "Downloads",
           "find": "Find", "about": "About", "appearance": "Appearance",
           "privacy": "Privacy", "general": "General",
           "theme": "Theme", "accent": "Accent", "light": "Light", "dark": "Dark",
           "network": "Network", "search_eng": "Search",
           "offline_title": "No Internet Connection",
           "offline_msg": "You're offline. Play Minesweeper.",
           "menu": "Menu", "new_window": "New window",
           "close_tab": "Close tab", "reload": "Reload", "home": "Home",
           "zoom": "Zoom", "fullscreen": "Fullscreen", "print": "Print",
           "quit": "Quit", "clear": "Clear", "delete": "Delete",
           "open_folder": "Open folder"},
    "ru": {"new_tab": "Новая вкладка", "search": "Поиск или URL", "settings": "Настройки",
           "history": "История", "bookmarks": "Закладки", "downloads": "Загрузки",
           "find": "Найти", "about": "О браузере", "appearance": "Внешний вид",
           "privacy": "Приватность", "general": "Основное",
           "theme": "Тема", "accent": "Акцент", "light": "Светлая", "dark": "Тёмная",
           "network": "Сеть", "search_eng": "Поиск",
           "offline_title": "Нет подключения к интернету",
           "offline_msg": "Вы офлайн. Сыграйте в Сапёр.",
           "menu": "Меню", "new_window": "Новое окно",
           "close_tab": "Закрыть вкладку", "reload": "Обновить", "home": "Домой",
           "zoom": "Масштаб", "fullscreen": "Полный экран", "print": "Печать",
           "quit": "Выход", "clear": "Очистить", "delete": "Удалить",
           "open_folder": "Открыть папку"},
}

class L:
    def __init__(self, cfg):
        self.cfg = cfg
    def __call__(self, key):
        d = I18N.get(self.cfg["language"], I18N["en"])
        return d.get(key, I18N["en"].get(key, key))

ACCENTS = {
    "green":  "#00C853", "blue":   "#1A73E8", "purple": "#7C4DFF",
    "pink":   "#FF4081", "orange": "#FF6D00", "red":    "#E53935",
    "cyan":   "#00BCD4", "teal":   "#009688", "yellow": "#FFC107",
    "indigo": "#3F51B5", "lime":   "#8BC34A", "amber":  "#FFB300",
    "deep_orange": "#FF5722", "brown": "#795548", "blue_grey": "#607D8B",
}

SEARCH_ENGINES = [
    ("google",    "Google",     "https://www.google.com/search?q=%s"),
    ("ddg",       "DuckDuckGo", "https://duckduckgo.com/?q=%s"),
    ("bing",      "Bing",       "https://www.bing.com/search?q=%s"),
    ("yandex",    "Яндекс",     "https://yandex.ru/search/?text=%s"),
    ("brave",     "Brave",      "https://search.brave.com/search?q=%s"),
    ("startpage", "Startpage",  "https://www.startpage.com/sp/search?query=%s"),
]

def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def _rgb_to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(*[max(0, min(255, int(x))) for x in rgb])

def _mix(c1, c2, t):
    a = _hex_to_rgb(c1)
    b = _hex_to_rgb(c2)
    return _rgb_to_hex(tuple(a[i] * (1 - t) + b[i] * t for i in range(3)))

def _lum(h):
    r, g, b = _hex_to_rgb(h)
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255

def build_palette(mode, accent_key):
    accent = ACCENTS.get(accent_key, "#00C853")

    if mode == "light":
        bg          = "#FEF7FF"
        surface_low = "#F7F2FA"
        surface     = "#F3EDF7"
        surface_high= "#ECE6F0"
        surface_max = "#E6E0E9"
        fg          = "#1D1B20"
        fg_variant  = "#49454F"
        tabbar      = "#ECE6F0"
        tab_active  = "#FEF7FF"
        tab_hover   = "#E6E0E9"
        on_accent = "#FFFFFF"
        accent_container = _mix(accent, "#FFFFFF", 0.75)
        on_accent_container = _mix(accent, "#000000", 0.45)
        accent_soft = _mix(accent, "#FFFFFF", 0.88)
        toolbar_bg = "rgba(254,247,255,0.72)"
        overlay_bg = "#F3EDF7"
    else:
        bg          = "#141218"
        surface_low = "#1D1B20"
        surface     = "#211F26"
        surface_high= "#2B2930"
        surface_max = "#36343B"
        fg          = "#E6E1E5"
        fg_variant  = "#CAC4D0"
        tabbar      = "#1D1B20"
        tab_active  = "#2B2930"
        tab_hover   = "#25232A"
        if _lum(accent) < 0.4:
            on_accent = "#FFFFFF"
            accent_container = _mix(accent, "#FFFFFF", 0.25)
            on_accent_container = "#FFFFFF"
        else:
            on_accent = "#000000"
            accent_container = _mix(accent, "#000000", 0.55)
            on_accent_container = "#FFFFFF"
        accent_soft = _mix(accent, "#000000", 0.8)
        toolbar_bg = "rgba(20,18,24,0.72)"
        overlay_bg = "#211F26"

    return {
        "mode": mode, "accent_key": accent_key,
        "bg": bg, "surface_low": surface_low, "surface": surface,
        "surface_high": surface_high, "surface_max": surface_max,
        "fg": fg, "fg_variant": fg_variant,
        "tabbar": tabbar, "tab_active": tab_active, "tab_hover": tab_hover,
        "accent": accent, "on_accent": on_accent,
        "accent_container": accent_container, "on_accent_container": on_accent_container,
        "accent_soft": accent_soft,
        "toolbar_bg": toolbar_bg,
        "overlay_bg": overlay_bg,
        "error": "#B3261E" if mode == "light" else "#F2B8B5",
        "success": "#146C2E" if mode == "light" else "#6DD58C",
        "warning": "#7A5900" if mode == "light" else "#FFD8A8",
    }

DEFAULT_CONFIG = {
    "theme_mode": "dark",
    "accent": "green",
    "language": "",
    "ui_font_size": 10,
    "homepage": GOOGLE_HOME,
    "window_width": 1200, "window_height": 760,
    "downloads_dir": str(HOME / "Downloads"),
    "restore_session": True,
    "animations": True,
    "ask_download_location": True,
    "zoom_per_site": True,
    "javascript_enabled": True,
    "images_enabled": True,
    "block_ads": True,
    "smooth_scrolling": True,
    "search_engine": "google",
    "dns_mode": "system",
    "dns_primary": "1.1.1.1",
    "dns_secondary": "1.0.0.1",
    "proxy_mode": "none",
    "proxy_host": "127.0.0.1",
    "proxy_port": 8080,
    "proxy_type": "http",
    "proxy_user": "",
    "proxy_pass": "",
    "blur_toolbar": True,
    "custom_user_agent": USER_AGENT,
}

class Config:
    def __init__(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.data = json.loads(json.dumps(DEFAULT_CONFIG))
        if CONFIG_FILE.exists():
            try:
                old = json.loads(CONFIG_FILE.read_text())
                for k in ("ui_style", "panel_position", "animation_speed"):
                    old.pop(k, None)
                if old.get("theme_mode") == "oled":
                    old["theme_mode"] = "dark"
                if old.get("accent") == "material_you":
                    old["accent"] = "green"
                old.pop("language", None)
                self.data.update(old)
            except Exception:
                pass
        self.data["language"] = detect_language()
        self.data["homepage"] = GOOGLE_HOME
        self.data["custom_user_agent"] = USER_AGENT
        self.save()

    def save(self):
        CONFIG_FILE.write_text(json.dumps(self.data, indent=2, ensure_ascii=False))

    def __getitem__(self, k):
        return self.data.get(k, DEFAULT_CONFIG.get(k))

    def __setitem__(self, k, v):
        self.data[k] = v
        self.save()

    def get(self, k, default=None):
        return self.data.get(k, DEFAULT_CONFIG.get(k, default))

    def palette(self):
        return build_palette(self["theme_mode"], self["accent"])

class Store:
    def __init__(self, cfg):
        self.cfg = cfg
        self.history, self.bookmarks, self.downloads, self.favicons = [], [], [], {}
        for attr, path in (("history", HISTORY_FILE), ("bookmarks", BOOKMARKS_FILE),
                           ("downloads", DOWNLOADS_FILE), ("favicons", FAVICONS_FILE)):
            if path.exists():
                try:
                    setattr(self, attr, json.loads(path.read_text()))
                except Exception:
                    pass

    def _save(self, path, data):
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    def save_history(self):
        self._save(HISTORY_FILE, self.history[-10000:])

    def add_history(self, u, t):
        if not u or u.startswith("clor://"):
            return
        for h in self.history[-3:]:
            if h["url"] == u and time.time() - h["ts"] < 3:
                return
        self.history.append({"url": u, "title": t or u, "ts": time.time()})
        self.save_history()

    def clear_history(self):
        self.history = []
        self.save_history()

    def remove_history_url(self, url):
        self.history = [h for h in self.history if h["url"] != url]
        self.save_history()

    def add_bookmark(self, u, t):
        self.bookmarks.append({"url": u, "title": t or u, "ts": time.time()})
        self._save(BOOKMARKS_FILE, self.bookmarks)

    def remove_bookmark(self, i):
        if 0 <= i < len(self.bookmarks):
            self.bookmarks.pop(i)
            self._save(BOOKMARKS_FILE, self.bookmarks)

    def is_bookmarked(self, u):
        return any(b["url"] == u for b in self.bookmarks)

    def add_download(self, p, u):
        self.downloads.append({"path": str(p), "url": u, "ts": time.time()})
        self._save(DOWNLOADS_FILE, self.downloads)

    def clear_downloads(self):
        self.downloads = []
        self._save(DOWNLOADS_FILE, self.downloads)

    def set_favicon(self, host, h):
        self.favicons[host] = h
        if len(self.favicons) > 2000:
            self.favicons = dict(list(self.favicons.items())[-1000:])
        self._save(FAVICONS_FILE, self.favicons)

    def get_favicon(self, host):
        return self.favicons.get(host)

class AdBlockInterceptor(QWebEngineUrlRequestInterceptor):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.blocked = 0
        self.hosts = set([
            "doubleclick.net", "googlesyndication.com", "google-analytics.com",
            "googletagmanager.com", "adservice.google.com", "ads.yahoo.com",
            "adnxs.com", "criteo.com", "taboola.com", "outbrain.com",
            "scorecardresearch.com", "quantserve.com", "adsafeprotected.com",
        ])

    def interceptRequest(self, info):
        if not self.cfg["block_ads"]:
            return
        url = info.requestUrl().toString()
        host = info.requestUrl().host()
        for h in self.hosts:
            if h in host:
                info.block(True)
                self.blocked += 1
                return

_ICON_FAMILY = ""

MATERIAL_SYMBOLS = {
    "arrow_back":  "e5c4", "arrow_forward": "e5c8",
    "refresh":     "e5d5", "home":          "e88a",
    "close":       "e5cd", "add":           "e145",
    "more_vert":   "e5d4", "menu":          "e5d2",
    "search":      "e8b6", "settings":      "e8b8",
    "star":        "e838", "star_border":   "e83a",
    "bookmark":    "e866", "history":       "e889",
    "download":    "f090", "print":         "e8ad",
    "delete":      "e872", "save":          "e161",
    "lock":        "e897", "lock_open":     "e898",
    "public":      "e80b", "warning":       "e002",
    "info":        "e88e", "check":         "e5ca",
    "shield":      "e9e0", "person":        "e7fd",
    "incognito":   "f0be", "palette":       "e40a",
    "tune":        "e429", "translate":     "e8e2",
    "language":    "e894", "grid_view":     "e9b0",
    "minimize":    "e931", "crop_square":   "e3c6",
    "fullscreen":  "e5d0", "zoom_in":       "e8ff",
    "zoom_out":    "e900", "light_mode":    "e518",
    "dark_mode":   "e51c", "brightness_6":  "e3a8",
    "wifi":        "e63e", "wifi_off":      "e648",
    "dns":         "e875", "vpn_lock":      "e62f",
    "router":      "e328", "security":      "e32a",
    "tab":         "e8d8", "windows":       "e3c6",
}

def load_icon_font():
    global _ICON_FAMILY
    if _ICON_FAMILY:
        return _ICON_FAMILY
    if not MSYMBOL_FILE.exists():
        print(f"[Clor] Font not found: {MSYMBOL_FILE}")
        return ""
    try:
        fid = QFontDatabase.addApplicationFont(str(MSYMBOL_FILE))
        if fid < 0:
            print("[Clor] Failed to load Material Symbols")
            return ""
        fams = QFontDatabase.applicationFontFamilies(fid)
        if fams:
            _ICON_FAMILY = fams[0]
            print(f"[Clor] Material Symbols: {_ICON_FAMILY}")
            return _ICON_FAMILY
    except Exception as e:
        print(f"[Clor] Font error: {e}")
    return ""

def _icon_char(n):
    code = MATERIAL_SYMBOLS.get(n, "e5cc")
    return chr(int(code, 16))

def icon_font(px):
    f = QFont(ICON_FONT_FAMILY)
    f.setPixelSize(px)
    return f

class IconButton(QToolButton):
    def __init__(self, name, size=18, tooltip="", parent=None):
        super().__init__(parent)
        self.setText(_icon_char(name))
        self.setFont(icon_font(size))
        self.setToolTip(tooltip)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self.setAutoRaise(True)
        self.setObjectName("IconBtn")
        self.setFixedSize(size + 14, size + 14)

class IconLabel(QLabel):
    def __init__(self, name, size=16, parent=None):
        super().__init__(parent)
        self.setText(_icon_char(name))
        self.setFont(icon_font(size))
        self.setAlignment(Qt.AlignCenter)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

class MD3Switch(QCheckBox):
    WIDTH = 48
    HEIGHT = 28
    THUMB_OFF = 16
    THUMB_ON = 20
    TRACK_H = 24

    def __init__(self, checked=False, parent=None):
        super().__init__(parent)
        self.setObjectName("MD3Switch")
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet("QCheckBox#MD3Switch { background: transparent; border: none; }")
        self.setChecked(checked)
        self.setFixedSize(self.WIDTH, self.HEIGHT)
        self.setCursor(Qt.PointingHandCursor)
        self._progress = 1.0 if checked else 0.0
        self._hover = False
        self._anim = None
        self.toggled.connect(self._on_toggle)

    def _on_toggle(self, checked):
        if self._anim is not None:
            try:
                self._anim.stop()
            except Exception:
                pass
        anim = QPropertyAnimation(self, b"progress", self)
        anim.setDuration(200)
        anim.setStartValue(self._progress)
        anim.setEndValue(1.0 if checked else 0.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start(QAbstractAnimation.DeleteWhenStopped)
        self._anim = anim

    def get_progress(self):
        return self._progress

    def set_progress(self, v):
        self._progress = v
        self.update()

    progress = Property(float, get_progress, set_progress)

    def enterEvent(self, e):
        self._hover = True
        self.update()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._hover = False
        self.update()
        super().leaveEvent(e)

    def _palette(self):
        w = self
        while w is not None:
            if hasattr(w, "cfg") and hasattr(w.cfg, "palette"):
                try:
                    return w.cfg.palette()
                except Exception:
                    pass
            w = w.parent()
        return {"accent": "#00C853", "surface_max": "#CCCCCC",
                "fg": "#000", "on_accent": "#FFF", "surface": "#FFF",
                "fg_variant": "#888"}

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        pal = self._palette()
        checked = self.isChecked()
        t = self._progress

        track_color = QColor(pal["accent"]) if checked else QColor(pal["surface_max"])
        if self._hover:
            overlay = QColor(track_color)
            overlay.setAlpha(50)
            glow = QRect(-2, (self.HEIGHT - self.TRACK_H) // 2 - 2,
                         self.WIDTH + 4, self.TRACK_H + 4)
            p.setPen(Qt.NoPen)
            p.setBrush(overlay)
            p.drawRoundedRect(glow, (self.TRACK_H + 4) / 2, (self.TRACK_H + 4) / 2)

        track_y = (self.HEIGHT - self.TRACK_H) / 2
        p.setPen(Qt.NoPen)
        p.setBrush(track_color)
        p.drawRoundedRect(QRect(0, int(track_y), self.WIDTH, self.TRACK_H),
                          self.TRACK_H / 2, self.TRACK_H / 2)

        thumb_size = int(self.THUMB_OFF + (self.THUMB_ON - self.THUMB_OFF) * t)
        thumb_y = (self.HEIGHT - thumb_size) / 2
        margin = 4
        x_off = margin
        x_on = self.WIDTH - margin - thumb_size
        thumb_x = x_off + (x_on - x_off) * t

        thumb_color = QColor(pal.get("on_accent", "#FFFFFF")) if checked else QColor(pal.get("surface", "#FFFFFF"))
        p.setBrush(thumb_color)
        p.drawEllipse(int(thumb_x), int(thumb_y), thumb_size, thumb_size)

        if not checked and t < 0.5:
            p.setBrush(Qt.NoBrush)
            p.setPen(QColor(pal.get("fg_variant", "#888")))
            p.drawEllipse(int(thumb_x), int(thumb_y), thumb_size, thumb_size)

class OverlayDialog(QFrame):
    closed = Signal()

    def __init__(self, parent, title, content_widget, width=680, height=520):
        super().__init__(parent)
        self.setObjectName("OverlayBackdrop")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._closing = False

        self.inner = QFrame(self)
        self.inner.setObjectName("OverlayContent")
        self.inner.setFixedSize(width, height)
        self.inner.setAttribute(Qt.WA_StyledBackground, True)
        self.inner.setAutoFillBackground(True)

        v = QVBoxLayout(self.inner)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)

        head = QFrame()
        head.setObjectName("OverlayHead")
        head.setAttribute(Qt.WA_StyledBackground, True)
        h = QHBoxLayout(head)
        h.setContentsMargins(18, 12, 10, 12)
        self.title_lbl = QLabel(title)
        self.title_lbl.setObjectName("OverlayTitle")
        h.addWidget(self.title_lbl)
        h.addStretch(1)
        close_btn = IconButton("close", 16, "Close")
        close_btn.clicked.connect(self.close_with_anim)
        h.addWidget(close_btn)
        v.addWidget(head)

        v.addWidget(content_widget, 1)

        self._op = QGraphicsOpacityEffect(self)
        self._op.setOpacity(0.0)
        self.setGraphicsEffect(self._op)
        self.hide()

    def _center_inner(self):
        if not self.parent():
            return
        pw = self.parent().width()
        ph = self.parent().height()
        w = min(self.inner.width(), max(320, pw - 40))
        h = min(self.inner.height(), max(200, ph - 40))
        self.inner.setFixedSize(w, h)
        self.inner.move((pw - w) // 2, (ph - h) // 2)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            pos = e.position().toPoint() if hasattr(e, "position") else e.pos()
            if not self.inner.geometry().contains(pos):
                self.close_with_anim()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._center_inner()

    def show_with_anim(self):
        if self.parent():
            self.setGeometry(0, 0, self.parent().width(), self.parent().height())
        self.show()
        self.raise_()
        self._center_inner()

        anim = QPropertyAnimation(self._op, b"opacity", self)
        anim.setDuration(160)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start(QAbstractAnimation.DeleteWhenStopped)

    def close_with_anim(self):
        if self._closing:
            return
        self._closing = True
        anim = QPropertyAnimation(self._op, b"opacity", self)
        anim.setDuration(130)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.InCubic)
        anim.finished.connect(self._really_close)
        anim.start(QAbstractAnimation.DeleteWhenStopped)

    def _really_close(self):
        self.closed.emit()
        self.hide()
        self.deleteLater()

class MinesweeperWidget(QWidget):
    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self.rows, self.cols, self.mines = 9, 9, 10
        self.grid, self.revealed, self.flagged = [], [], []
        self.game_over = False
        self.won = False
        self._build_ui()
        self.new_game()

    def _build_ui(self):
        v = QVBoxLayout(self)
        v.setContentsMargins(20, 16, 20, 16)
        v.setSpacing(10)
        head = QHBoxLayout()
        self.title = QLabel("😢")
        self.title.setObjectName("MS_Title")
        head.addWidget(self.title)
        head.addStretch(1)
        self.status_lbl = QLabel("")
        self.status_lbl.setObjectName("MS_Status")
        head.addWidget(self.status_lbl)
        v.addLayout(head)

        grid_wrap = QFrame()
        grid_wrap.setObjectName("MS_Board")
        g = QGridLayout(grid_wrap)
        g.setSpacing(3)
        g.setContentsMargins(8, 8, 8, 8)
        self.buttons = []
        for r in range(self.rows):
            row = []
            for c in range(self.cols):
                b = QPushButton()
                b.setFixedSize(36, 36)
                b.setObjectName("MS_Cell")
                b.clicked.connect(lambda _=False, r=r, c=c: self.on_click(r, c))
                b.setContextMenuPolicy(Qt.CustomContextMenu)
                b.customContextMenuRequested.connect(lambda p, r=r, c=c: self.on_flag(r, c))
                g.addWidget(b, r, c)
                row.append(b)
            self.buttons.append(row)
        v.addWidget(grid_wrap, 0, Qt.AlignCenter)

        row = QHBoxLayout()
        row.addStretch(1)
        restart = QPushButton("New game")
        restart.setObjectName("MS_Restart")
        restart.clicked.connect(self.new_game)
        row.addWidget(restart)
        row.addStretch(1)
        v.addLayout(row)
        v.addStretch(1)

    def new_game(self):
        self.game_over = False
        self.won = False
        self.grid = [[0] * self.cols for _ in range(self.rows)]
        self.revealed = [[False] * self.cols for _ in range(self.rows)]
        self.flagged = [[False] * self.cols for _ in range(self.rows)]
        placed = 0
        while placed < self.mines:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)
            if self.grid[r][c] != -1:
                self.grid[r][c] = -1
                placed += 1
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == -1:
                    continue
                self.grid[r][c] = sum(
                    1 for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                    if (dr or dc) and 0 <= r+dr < self.rows and 0 <= c+dc < self.cols
                    and self.grid[r+dr][c+dc] == -1
                )
        self.title.setText("😢")
        self.status_lbl.setText("9×9 · 10 💣")
        for r in range(self.rows):
            for c in range(self.cols):
                b = self.buttons[r][c]
                b.setText("")
                b.setEnabled(True)
                b.setProperty("state", "hidden")
                b.style().unpolish(b)
                b.style().polish(b)

    def on_click(self, r, c):
        if self.game_over or self.revealed[r][c] or self.flagged[r][c]:
            return
        if self.grid[r][c] == -1:
            self._boom(r, c)
            return
        self._reveal(r, c)
        self._check_win()

    def _reveal(self, r, c):
        if not (0 <= r < self.rows and 0 <= c < self.cols):
            return
        if self.revealed[r][c] or self.flagged[r][c]:
            return
        self.revealed[r][c] = True
        b = self.buttons[r][c]
        b.setEnabled(False)
        v = self.grid[r][c]
        b.setText(str(v) if v > 0 else "")
        b.setProperty("state", f"r{v}")
        b.style().unpolish(b)
        b.style().polish(b)
        if v == 0:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr or dc:
                        self._reveal(r + dr, c + dc)

    def _boom(self, r, c):
        self.game_over = True
        self.title.setText("💥")
        self.status_lbl.setText("Boom!")
        for rr in range(self.rows):
            for cc in range(self.cols):
                if self.grid[rr][cc] == -1:
                    b = self.buttons[rr][cc]
                    b.setText("💣")
                    b.setEnabled(False)
                    b.setProperty("state", "mine")
                    b.style().unpolish(b)
                    b.style().polish(b)
        self.buttons[r][c].setProperty("state", "boom")
        self.buttons[r][c].style().unpolish(self.buttons[r][c])
        self.buttons[r][c].style().polish(self.buttons[r][c])

    def on_flag(self, r, c):
        if self.game_over or self.revealed[r][c]:
            return
        self.flagged[r][c] = not self.flagged[r][c]
        b = self.buttons[r][c]
        if self.flagged[r][c]:
            b.setText("🚩")
            b.setProperty("state", "flag")
        else:
            b.setText("")
            b.setProperty("state", "hidden")
        b.style().unpolish(b)
        b.style().polish(b)

    def _check_win(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] != -1 and not self.revealed[r][c]:
                    return
        self.won = True
        self.game_over = True
        self.title.setText("😎")
        self.status_lbl.setText("You won!")
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == -1:
                    b = self.buttons[r][c]
                    b.setText("🚩")
                    b.setEnabled(False)

class OfflinePage(QWidget):
    def __init__(self, cfg, l, parent=None):
        super().__init__(parent)
        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)
        head = QFrame()
        head.setObjectName("OfflineHead")
        h = QVBoxLayout(head)
        h.setContentsMargins(28, 22, 28, 14)
        h.setSpacing(3)
        title = QLabel(l("offline_title"))
        title.setObjectName("OfflineTitle")
        h.addWidget(title)
        sub = QLabel(l("offline_msg"))
        sub.setObjectName("OfflineSub")
        h.addWidget(sub)
        v.addWidget(head)
        v.addWidget(MinesweeperWidget(cfg), 1)

def is_online(timeout=1.5):
    try:
        urllib.request.urlopen("https://www.google.com/", timeout=timeout)
        return True
    except Exception:
        return False

class ClorWebPage(QWebEnginePage):
    def __init__(self, profile, parent=None, main_window=None):
        super().__init__(profile, parent)
        self.mw = main_window

    def createWindow(self, wtype):
        if not self.mw:
            return super().createWindow(wtype)
        if wtype in (QWebEnginePage.WebBrowserTab, QWebEnginePage.WebBrowserBackgroundTab):
            return self.mw.new_tab(background=(wtype == QWebEnginePage.WebBrowserBackgroundTab)).view.page()
        if wtype == QWebEnginePage.WebDialog:
            view = QWebEngineView(self.mw)
            view.setWindowTitle("Clor")
            view.resize(800, 600)
            view.show()
            return view.page()
        return super().createWindow(wtype)

    def acceptNavigationRequest(self, url, navtype, isMainFrame):
        scheme = url.scheme()
        if scheme in ("view-source", "chrome", "devtools"):
            return False
        return super().acceptNavigationRequest(url, navtype, isMainFrame)

    def createStandardContextMenu(self):
        return None

class BrowserTab(QWidget):
    title_changed = Signal(str)
    url_changed = Signal(str)
    icon_changed = Signal(QIcon)
    load_started = Signal()
    load_finished = Signal(bool)
    load_progress = Signal(int)

    def __init__(self, cfg, store, profile, main_window, url=None, private=False):
        super().__init__()
        self.cfg = cfg
        self.store = store
        self.profile = profile
        self.mw = main_window
        self.private = private
        self.zoom = 100

        v = QVBoxLayout(self)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(0)
        self.stack = QStackedWidget()
        v.addWidget(self.stack)

        self.view = QWebEngineView()
        self.page = ClorWebPage(profile, self, main_window)
        self.view.setPage(self.page)
        self.stack.addWidget(self.view)
        self.view.setContextMenuPolicy(Qt.NoContextMenu)

        try:
            self.page.setBackgroundColor(QColor(0, 0, 0, 0))
        except Exception:
            pass

        translator = self.mw.l if (self.mw is not None and hasattr(self.mw, "l")) else (lambda x: x)
        self.offline_page = OfflinePage(cfg, translator)
        self.stack.addWidget(self.offline_page)

        self._fade = QGraphicsOpacityEffect(self.view)
        self._fade.setOpacity(1.0)
        self.view.setGraphicsEffect(self._fade)

        self._apply_settings()
        self.view.titleChanged.connect(lambda t: self.title_changed.emit(t or "New tab"))
        self.view.urlChanged.connect(self._on_url)
        self.view.iconChanged.connect(self._on_icon)
        self.view.loadStarted.connect(self._on_load_started)
        self.view.loadFinished.connect(self._on_load_finished)
        self.view.loadProgress.connect(self.load_progress.emit)

        if url:
            self.navigate(url)

    def _apply_settings(self):
        s = self.page.settings()
        s.setAttribute(QWebEngineSettings.JavascriptEnabled, bool(self.cfg["javascript_enabled"]))
        s.setAttribute(QWebEngineSettings.AutoLoadImages, bool(self.cfg["images_enabled"]))
        s.setAttribute(QWebEngineSettings.PluginsEnabled, True)
        s.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        s.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        s.setAttribute(QWebEngineSettings.PdfViewerEnabled, True)
        s.setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, bool(self.cfg["smooth_scrolling"]))
        s.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)

    def navigate(self, url):
        if not url:
            return
        url = url.strip()
        if url == "clor://offline":
            self.stack.setCurrentWidget(self.offline_page)
            return
        if url.startswith("view-source:") or url.startswith("devtools:"):
            return
        if re.match(r"^[a-z]+://", url):
            scheme = url.split(":", 1)[0]
            if scheme not in ("http", "https", "file", "data", "about"):
                return
        elif re.match(r"^[\w.-]+\.[a-z]{2,}(/.*)?$", url, re.IGNORECASE):
            url = "https://" + url
        else:
            for eid, name, tmpl in SEARCH_ENGINES:
                if self.cfg["search_engine"] == eid:
                    url = tmpl.replace("%s", urllib.parse.quote_plus(url))
                    break
            else:
                url = f"https://www.google.com/search?q={urllib.parse.quote_plus(url)}"
        if not is_online():
            self.stack.setCurrentWidget(self.offline_page)
            self.url_changed.emit("clor://offline")
            title = self.mw.l("offline_title") if (self.mw and hasattr(self.mw, "l")) else "Offline"
            self.title_changed.emit(title)
            return
        self.stack.setCurrentWidget(self.view)
        self.view.setUrl(QUrl(url))

    def back(self):
        self.view.back()

    def forward(self):
        self.view.forward()

    def reload(self):
        self.view.reload()

    def stop(self):
        self.view.stop()

    def home(self):
        self.navigate(self.cfg["homepage"])

    def url(self):
        return self.view.url().toString()

    def title(self):
        return self.view.title() or self.url() or "New tab"

    def find(self, text, case=False, backward=False):
        flags = QWebEnginePage.FindFlags()
        if case:
            flags |= QWebEnginePage.FindCaseSensitively
        if backward:
            flags |= QWebEnginePage.FindBackward
        self.page.findText(text, flags)

    def _on_url(self, u):
        s = u.toString()
        if s == "about:blank":
            return
        self.url_changed.emit(s)
        if not s.startswith("clor://"):
            self.store.add_history(s, self.view.title())
        host = u.host()
        if host:
            h = self.store.get_favicon(host)
            if h:
                try:
                    pm = QPixmap()
                    pm.loadFromData(bytes.fromhex(h))
                    if not pm.isNull():
                        self.icon_changed.emit(QIcon(pm))
                except Exception:
                    pass

    def _on_icon(self, icon):
        self.icon_changed.emit(icon)
        host = self.view.url().host()
        if host and not icon.isNull():
            try:
                pm = icon.pixmap(32, 32)
                ba = QByteArray()
                buf = QBuffer(ba)
                buf.open(QBuffer.WriteOnly)
                pm.save(buf, "PNG")
                buf.close()
                self.store.set_favicon(host, bytes(ba.toHex()).decode())
            except Exception:
                pass

    def _on_load_started(self):
        self.load_started.emit()
        if self.cfg["animations"]:
            self._fade.setOpacity(0.9)
            a = QPropertyAnimation(self._fade, b"opacity", self)
            a.setDuration(180)
            a.setStartValue(0.9)
            a.setEndValue(1.0)
            a.start(QAbstractAnimation.DeleteWhenStopped)

    def _on_load_finished(self, ok):
        self.load_finished.emit(ok)

class ChromeTab(QFrame):
    clicked = Signal(object)
    close_requested = Signal(object)
    TAB_W = 170
    TAB_H = 30

    def __init__(self, tab, title="New tab", icon=None):
        super().__init__()
        self.tab = tab
        self.setObjectName("ChromeTab")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(self.TAB_W, self.TAB_H)

        h = QHBoxLayout(self)
        h.setContentsMargins(8, 0, 4, 0)
        h.setSpacing(6)

        self.fav = QLabel()
        self.fav.setFixedSize(14, 14)
        self.fav.setObjectName("Favicon")
        self.fav.setAlignment(Qt.AlignCenter)
        self.fav.setFont(icon_font(12))
        self._set_icon(icon)
        h.addWidget(self.fav)

        self.lbl = QLabel(title)
        self.lbl.setObjectName("TabTitle")
        self.lbl.setTextInteractionFlags(Qt.NoTextInteraction)
        h.addWidget(self.lbl, 1)

        self.close_btn = IconButton("close", 12, "Close")
        self.close_btn.setFixedSize(22, 22)
        self.close_btn.clicked.connect(lambda: self.close_requested.emit(self.tab))
        h.addWidget(self.close_btn)

    def _set_icon(self, icon):
        if icon and not icon.isNull():
            self.fav.setPixmap(icon.pixmap(14, 14))
            self.fav.setText("")
        else:
            self.fav.setPixmap(QPixmap())
            self.fav.setText(_icon_char("public"))

    def set_title(self, t):
        fm = self.lbl.fontMetrics()
        avail = self.TAB_W - 60
        self.lbl.setText(fm.elidedText(t, Qt.ElideRight, avail))
        self.setToolTip(t)

    def set_icon(self, icon):
        self._set_icon(icon)

    def set_active(self, a):
        self.setProperty("active", "true" if a else "false")
        self.style().unpolish(self)
        self.style().polish(self)
        for ch in self.findChildren(QLabel):
            ch.style().unpolish(ch)
            ch.style().polish(ch)

    def enterEvent(self, e):
        self.setProperty("hover", "true")
        self.style().unpolish(self)
        self.style().polish(self)
        super().enterEvent(e)

    def leaveEvent(self, e):
        self.setProperty("hover", "false")
        self.style().unpolish(self)
        self.style().polish(self)
        super().leaveEvent(e)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.clicked.emit(self.tab)
        super().mousePressEvent(e)

    def mouseDoubleClickEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.close_requested.emit(self.tab)

class TabStrip(QFrame):
    add_requested = Signal()
    tab_selected = Signal(object)
    tab_close_requested = Signal(object)

    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self.setObjectName("TabStrip")
        self.setFixedHeight(36)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        h = QHBoxLayout(self)
        h.setContentsMargins(6, 4, 4, 2)
        h.setSpacing(2)

        self._tabs_wrap = QWidget()
        self._inner = QHBoxLayout(self._tabs_wrap)
        self._inner.setContentsMargins(0, 0, 0, 0)
        self._inner.setSpacing(2)
        h.addWidget(self._tabs_wrap)
        h.addStretch(1)

        self.add_btn = IconButton("add", 18, "New tab (Ctrl+T)")
        self.add_btn.setObjectName("AddTabBtn")
        self.add_btn.setFixedSize(28, 26)
        self.add_btn.clicked.connect(self.add_requested.emit)
        self._inner.addWidget(self.add_btn)

        self._win_btns = QFrame()
        self._win_btns.setObjectName("WinBtns")
        wb = QHBoxLayout(self._win_btns)
        wb.setContentsMargins(0, 0, 0, 0)
        wb.setSpacing(0)
        h.addWidget(self._win_btns)

        self._chips = []

    def add_window_controls(self, minimize_cb, maximize_cb, close_cb):
        wb = self._win_btns.layout()
        for name, cb in (("minimize", minimize_cb), ("crop_square", maximize_cb), ("close", close_cb)):
            b = IconButton(name, 14, name)
            b.setObjectName("WinBtnClose" if name == "close" else "WinBtn")
            b.setFixedSize(34, 26)
            b.clicked.connect(cb)
            wb.addWidget(b)

    def add_chip(self, tab, title="New tab", icon=None):
        chip = ChromeTab(tab, title, icon)
        chip.clicked.connect(self.tab_selected.emit)
        chip.close_requested.connect(self.tab_close_requested.emit)
        idx = self._inner.count() - 1
        self._inner.insertWidget(idx, chip)
        self._chips.append(chip)
        return chip

    def remove_chip(self, tab):
        for chip in self._chips:
            if chip.tab is tab:
                op = QGraphicsOpacityEffect(chip)
                op.setOpacity(1.0)
                chip.setGraphicsEffect(op)
                a = QPropertyAnimation(op, b"opacity", chip)
                a.setDuration(130)
                a.setStartValue(1.0)
                a.setEndValue(0.0)
                a.setEasingCurve(QEasingCurve.InCubic)
                a.finished.connect(lambda c=chip: self._really_remove(c))
                a.start(QAbstractAnimation.DeleteWhenStopped)
                return

    def _really_remove(self, chip):
        try:
            self._inner.removeWidget(chip)
        except Exception:
            pass
        try:
            chip.deleteLater()
        except Exception:
            pass
        if chip in self._chips:
            self._chips.remove(chip)

    def set_active(self, tab):
        for c in self._chips:
            c.set_active(c.tab is tab)

    def set_title(self, tab, t):
        for c in self._chips:
            if c.tab is tab:
                c.set_title(t)
                return

    def set_icon(self, tab, i):
        for c in self._chips:
            if c.tab is tab:
                c.set_icon(i)
                return

class FirefoxMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FirefoxMenu")
        self.setSeparatorsCollapsible(False)

    def add_item(self, icon_name, text, callback, shortcut=""):
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(QKeySequence(shortcut))
        action.triggered.connect(callback)

        w = QWidget()
        w.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        w.setObjectName("MenuRow")
        h = QHBoxLayout(w)
        h.setContentsMargins(12, 8, 16, 8)
        h.setSpacing(12)

        icon = IconLabel(icon_name, 18)
        icon.setFixedSize(20, 20)
        icon.setObjectName("MenuIcon")
        h.addWidget(icon)

        lbl = QLabel(text)
        lbl.setObjectName("MenuLabel")
        h.addWidget(lbl, 1)

        if shortcut:
            sc = QLabel(shortcut)
            sc.setObjectName("MenuShortcut")
            h.addWidget(sc)

        wa = QWidgetAction(self)
        wa.setDefaultWidget(w)
        wa.triggered.connect(callback)
        self.addAction(wa)
        return action

    def add_separator_line(self):
        sep = QFrame()
        sep.setObjectName("MenuSeparator")
        sep.setFixedHeight(1)
        wa = QWidgetAction(self)
        wa.setDefaultWidget(sep)
        self.addAction(wa)

class AboutContent(QWidget):
    def __init__(self, cfg, l, parent=None):
        super().__init__(parent)
        p = cfg.palette()
        v = QVBoxLayout(self)
        v.setContentsMargins(32, 20, 32, 20)
        v.setSpacing(10)

        head = QFrame()
        head.setObjectName("AboutHead")
        hv = QVBoxLayout(head)
        hv.setContentsMargins(0, 0, 0, 0)
        hv.setSpacing(4)

        icon_lbl = QLabel()
        icon_lbl.setFixedSize(72, 72)
        icon_lbl.setAlignment(Qt.AlignCenter)
        if ICON_FILE.exists():
            pm = QPixmap(str(ICON_FILE)).scaled(72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_lbl.setPixmap(pm)
        else:
            icon_lbl.setText("C")
            f = QFont("Open Sans", 44)
            f.setBold(True)
            icon_lbl.setFont(f)
            icon_lbl.setStyleSheet(f"color:{p['accent']};")
        hv.addWidget(icon_lbl, 0, Qt.AlignHCenter)

        name = QLabel("Clor")
        name.setObjectName("AboutName")
        name.setAlignment(Qt.AlignCenter)
        hv.addWidget(name)
        tag = QLabel("Лёгкий, анонимный, быстрый, надёжный и простой браузер")
        tag.setObjectName("AboutTagline")
        tag.setAlignment(Qt.AlignCenter)
        tag.setWordWrap(True)
        hv.addWidget(tag)
        v.addWidget(head)
        v.addSpacing(4)

        info = QFrame()
        info.setObjectName("AboutInfo")
        fv = QVBoxLayout(info)
        fv.setContentsMargins(16, 12, 16, 12)
        fv.setSpacing(8)
        rows = [
            ("Разработчик", DEVELOPER), ("Браузер", "Clor"),
            ("WebView движок", ENGINE_NAME), ("Версия", APP_VERSION),
            ("Язык", "Авто (" + ("RU" if cfg["language"] == "ru" else "EN") + ")"),
        ]
        for k, val in rows:
            r = QHBoxLayout()
            key = QLabel(k)
            key.setObjectName("AboutKey")
            key.setFixedWidth(130)
            vv = QLabel(val)
            vv.setObjectName("AboutVal")
            vv.setWordWrap(True)
            r.addWidget(key)
            r.addWidget(vv, 1)
            fv.addLayout(r)
        v.addWidget(info)
        v.addSpacing(4)

        quote = QLabel("«Clor — браузер для тех, кто ценит скорость, приватность и стиль.»")
        quote.setObjectName("AboutQuote")
        quote.setAlignment(Qt.AlignCenter)
        quote.setWordWrap(True)
        v.addWidget(quote)
        v.addStretch(1)

class SettingsContent(QWidget):
    changed = Signal()

    def __init__(self, cfg, l, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self.l = l
        self.setObjectName("SettingsContent")
        self.setAttribute(Qt.WA_StyledBackground, True)

        h = QHBoxLayout(self)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        self.sidebar = QFrame()
        self.sidebar.setObjectName("SettingsSidebar")
        self.sidebar.setFixedWidth(200)
        self.sidebar.setAttribute(Qt.WA_StyledBackground, True)
        sv = QVBoxLayout(self.sidebar)
        sv.setContentsMargins(12, 16, 12, 16)
        sv.setSpacing(2)

        title = QLabel(self.l("settings"))
        title.setObjectName("SettingsTitle")
        sv.addWidget(title)
        sv.addSpacing(12)

        self.categories = [
            ("general",     "settings",   self.l("general")),
            ("appearance",  "palette",    self.l("appearance")),
            ("search_eng",  "search",     self.l("search_eng")),
            ("privacy",     "shield",     self.l("privacy")),
            ("network",     "dns",        self.l("network")),
            ("about",       "info",       self.l("about")),
        ]
        self.cat_group = QButtonGroup(self)
        self.cat_group.setExclusive(True)
        self.cat_btns = {}
        for key, icon, label in self.categories:
            b = QToolButton()
            b.setObjectName("SettingsCatBtn")
            b.setText(f"  {label}")
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.setAutoRaise(True)
            b.setFixedHeight(38)
            b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            b.clicked.connect(lambda _=False, k=key: self._show(k))
            self.cat_group.addButton(b)
            sv.addWidget(b)
            self.cat_btns[key] = b
        self.cat_btns["general"].setChecked(True)
        sv.addStretch(1)

        h.addWidget(self.sidebar)

        self.stack = QStackedWidget()
        self.stack.setObjectName("SettingsStack")
        self.stack.setAttribute(Qt.WA_StyledBackground, True)
        h.addWidget(self.stack, 1)
        self.stack.addWidget(self._page_general())
        self.stack.addWidget(self._page_appearance())
        self.stack.addWidget(self._page_search_eng())
        self.stack.addWidget(self._page_privacy())
        self.stack.addWidget(self._page_network())
        self.stack.addWidget(self._page_about())

    def _show(self, key):
        keys = [c[0] for c in self.categories]
        self.stack.setCurrentIndex(keys.index(key))

    def _scroll_page(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setObjectName("SettingsScroll")
        scroll.setAttribute(Qt.WA_StyledBackground, True)
        inner = QWidget()
        inner.setObjectName("SettingsInner")
        inner.setAttribute(Qt.WA_StyledBackground, True)
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(32, 24, 32, 32)
        lay.setSpacing(6)
        scroll.setWidget(inner)
        return scroll, lay

    def _section(self, lay, title, hint=""):
        row = QVBoxLayout()
        row.setSpacing(2)
        row.setContentsMargins(2, 16, 2, 6)
        t = QLabel(title)
        t.setObjectName("SectionTitle")
        row.addWidget(t)
        if hint:
            hh = QLabel(hint)
            hh.setObjectName("SectionHint")
            hh.setWordWrap(True)
            row.addWidget(hh)
        lay.addLayout(row)

    def _row_toggle(self, lay, label, key, hint=""):
        w = QFrame()
        w.setObjectName("SettingRow")
        w.setAttribute(Qt.WA_StyledBackground, True)
        h = QHBoxLayout(w)
        h.setContentsMargins(16, 12, 16, 12)
        col = QVBoxLayout()
        col.setSpacing(1)
        t = QLabel(label)
        t.setObjectName("SettingLabel")
        col.addWidget(t)
        if hint:
            hh = QLabel(hint)
            hh.setObjectName("SettingHint")
            hh.setWordWrap(True)
            col.addWidget(hh)
        h.addLayout(col, 1)
        sw = MD3Switch(bool(self.cfg[key]))
        sw.toggled.connect(lambda v, k=key: self._set(k, v))
        h.addWidget(sw, 0, Qt.AlignVCenter)
        lay.addWidget(w)

    def _row_combo(self, lay, label, key, items, hint=""):
        w = QFrame()
        w.setObjectName("SettingRow")
        w.setAttribute(Qt.WA_StyledBackground, True)
        h = QHBoxLayout(w)
        h.setContentsMargins(16, 12, 16, 12)
        col = QVBoxLayout()
        col.setSpacing(1)
        t = QLabel(label)
        t.setObjectName("SettingLabel")
        col.addWidget(t)
        if hint:
            hh = QLabel(hint)
            hh.setObjectName("SettingHint")
            hh.setWordWrap(True)
            col.addWidget(hh)
        h.addLayout(col, 1)
        c = QComboBox()
        for k, name in items:
            c.addItem(name, k)
        for i in range(c.count()):
            if c.itemData(i) == self.cfg[key]:
                c.setCurrentIndex(i)
                break
        c.currentIndexChanged.connect(lambda i: self._set(key, c.itemData(i)))
        c.setMinimumWidth(200)
        h.addWidget(c)
        lay.addWidget(w)

    def _row_slider(self, lay, label, key, lo, hi, hint=""):
        w = QFrame()
        w.setObjectName("SettingRow")
        w.setAttribute(Qt.WA_StyledBackground, True)
        h = QHBoxLayout(w)
        h.setContentsMargins(16, 12, 16, 12)
        col = QVBoxLayout()
        col.setSpacing(1)
        t = QLabel(label)
        t.setObjectName("SettingLabel")
        col.addWidget(t)
        if hint:
            hh = QLabel(hint)
            hh.setObjectName("SettingHint")
            hh.setWordWrap(True)
            col.addWidget(hh)
        h.addLayout(col, 1)
        s = QSlider(Qt.Horizontal)
        s.setRange(lo, hi)
        s.setValue(int(self.cfg[key]))
        s.setMinimumWidth(180)
        val = QLabel(str(s.value()))
        val.setObjectName("SliderVal")
        val.setFixedWidth(42)
        val.setAlignment(Qt.AlignRight)
        s.valueChanged.connect(lambda v: (val.setText(str(v)), self._set(key, v)))
        h.addWidget(s)
        h.addWidget(val)
        lay.addWidget(w)

    def _row_text(self, lay, label, key, hint="", placeholder=""):
        w = QFrame()
        w.setObjectName("SettingRow")
        w.setAttribute(Qt.WA_StyledBackground, True)
        h = QHBoxLayout(w)
        h.setContentsMargins(16, 12, 16, 12)
        col = QVBoxLayout()
        col.setSpacing(1)
        t = QLabel(label)
        t.setObjectName("SettingLabel")
        col.addWidget(t)
        if hint:
            hh = QLabel(hint)
            hh.setObjectName("SettingHint")
            hh.setWordWrap(True)
            col.addWidget(hh)
        h.addLayout(col, 1)
        le = QLineEdit(str(self.cfg[key]))
        le.setPlaceholderText(placeholder)
        le.setMinimumWidth(240)
        le.textChanged.connect(lambda v, k=key: self._set(k, v))
        h.addWidget(le)
        lay.addWidget(w)

    def _page_general(self):
        scroll, lay = self._scroll_page()
        self._section(lay, self.l("general"))
        self._row_text(lay, "Homepage", "homepage", "URL новой вкладки")
        self._row_text(lay, "Downloads folder", "downloads_dir")
        self._row_toggle(lay, "Ask where to save", "ask_download_location")
        self._row_toggle(lay, "Restore session", "restore_session")
        self._row_toggle(lay, "Per-site zoom", "zoom_per_site")
        self._section(lay, "Performance")
        self._row_slider(lay, "UI font size", "ui_font_size", 8, 18)
        self._row_toggle(lay, "Animations", "animations")
        self._row_toggle(lay, "Smooth scrolling", "smooth_scrolling")
        return scroll

    def _page_appearance(self):
        scroll, lay = self._scroll_page()
        self._section(lay, self.l("theme"))

        mode_row = QFrame()
        mode_row.setObjectName("SettingRow")
        mode_row.setAttribute(Qt.WA_StyledBackground, True)
        mh = QHBoxLayout(mode_row)
        mh.setContentsMargins(16, 12, 16, 12)
        mh.addWidget(QLabel(self.l("theme")), 1)
        self.mode_group = QButtonGroup(self)
        for mode_key, mode_lbl in (("light", self.l("light")), ("dark", self.l("dark"))):
            b = QToolButton()
            b.setObjectName("ModeBtn")
            b.setText(f"  {mode_lbl}")
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.setAutoRaise(True)
            b.setFixedHeight(32)
            b.setMinimumWidth(120)
            if self.cfg["theme_mode"] == mode_key:
                b.setChecked(True)
            b.clicked.connect(lambda _=False, k=mode_key: self._set("theme_mode", k))
            self.mode_group.addButton(b)
            mh.addWidget(b)
        lay.addWidget(mode_row)

        self._section(lay, self.l("accent"))
        acc_row = QFrame()
        acc_row.setObjectName("SettingRow")
        acc_row.setAttribute(Qt.WA_StyledBackground, True)
        ag = QGridLayout(acc_row)
        ag.setContentsMargins(16, 14, 16, 14)
        ag.setSpacing(10)
        self.acc_group = QButtonGroup(self)
        self.acc_group.setExclusive(True)
        for i, (key, color) in enumerate(ACCENTS.items()):
            b = QToolButton()
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            b.setFixedSize(34, 34)
            b.setObjectName("AccentDot")
            b.setAutoRaise(True)
            b.setStyleSheet(f"background:{color}; border-radius:17px; border: none;")
            b.setToolTip(key)
            if self.cfg["accent"] == key:
                b.setChecked(True)
            b.clicked.connect(lambda _=False, k=key: self._set("accent", k))
            self.acc_group.addButton(b)
            ag.addWidget(b, i // 8, i % 8)
        lay.addWidget(acc_row)
        return scroll

    def _page_search_eng(self):
        scroll, lay = self._scroll_page()
        self._section(lay, self.l("search_eng"), "Поисковая система по умолчанию")
        self._row_combo(lay, "Search engine", "search_engine",
                        [(eid, name) for eid, name, _ in SEARCH_ENGINES])
        return scroll

    def _page_privacy(self):
        scroll, lay = self._scroll_page()
        self._section(lay, "Privacy & Security")
        self._row_toggle(lay, "Block ads", "block_ads")
        self._row_toggle(lay, "JavaScript", "javascript_enabled")
        self._row_toggle(lay, "Images", "images_enabled")
        return scroll

    def _page_network(self):
        scroll, lay = self._scroll_page()
        self._section(lay, "DNS", "Настройка DNS-серверов")
        self._row_combo(lay, "DNS mode", "dns_mode",
                        [("system", "System"), ("custom", "Custom")])
        self._row_text(lay, "Primary DNS", "dns_primary", "", "1.1.1.1")
        self._row_text(lay, "Secondary DNS", "dns_secondary", "", "1.0.0.1")

        self._section(lay, "Proxy")
        self._row_combo(lay, "Proxy mode", "proxy_mode",
                        [("none", "Disabled"), ("system", "System"), ("manual", "Manual")])
        self._row_combo(lay, "Proxy type", "proxy_type",
                        [("http", "HTTP / HTTPS"), ("socks5", "SOCKS5")])
        self._row_text(lay, "Host", "proxy_host", "", "127.0.0.1")
        self._row_slider(lay, "Port", "proxy_port", 1, 65535)
        self._row_text(lay, "Username", "proxy_user")
        self._row_text(lay, "Password", "proxy_pass")

        self._section(lay, "User-Agent")
        self._row_text(lay, "User-Agent", "custom_user_agent", "",
                       USER_AGENT)
        return scroll

    def _page_about(self):
        scroll, lay = self._scroll_page()
        lay.addWidget(AboutContent(self.cfg, self.l))
        return scroll

    def _set(self, k, v):
        self.cfg[k] = v
        self.changed.emit()

class HistoryContent(QWidget):
    def __init__(self, store, on_navigate, parent=None):
        super().__init__(parent)
        self.store = store
        self.on_navigate = on_navigate
        self.setObjectName("HistoryContent")
        self.setAttribute(Qt.WA_StyledBackground, True)

        v = QVBoxLayout(self)
        v.setContentsMargins(16, 12, 16, 12)
        v.setSpacing(8)
        search = QLineEdit()
        search.setPlaceholderText("Search history...")
        v.addWidget(search)

        self.lst = QListWidget()
        self.lst.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lst.customContextMenuRequested.connect(self._context_menu)
        self.lst.itemDoubleClicked.connect(self._open)
        v.addWidget(self.lst, 1)

        row = QHBoxLayout()
        b_clear = QPushButton("Clear all")
        b_clear.clicked.connect(self._clear_all)
        row.addWidget(b_clear)
        row.addStretch(1)
        v.addLayout(row)

        search.textChanged.connect(self._fill)
        self._fill()

    def _fill(self, q=""):
        self.lst.clear()
        q = q.lower()
        seen = set()
        for h in reversed(self.store.history):
            if h["url"] in seen:
                continue
            seen.add(h["url"])
            if q and q not in h["url"].lower() and q not in h.get("title", "").lower():
                continue
            it = QListWidgetItem(f"{h.get('title', h['url'])[:80]}\n{h['url']}")
            it.setData(Qt.UserRole, h["url"])
            self.lst.addItem(it)

    def _context_menu(self, pos):
        it = self.lst.itemAt(pos)
        if not it:
            return
        m = QMenu(self)
        a_open = m.addAction("Open")
        a_del = m.addAction("Delete from history")
        act = m.exec(self.lst.mapToGlobal(pos))
        if act == a_open:
            self._open(it)
        elif act == a_del:
            url = it.data(Qt.UserRole)
            self.store.remove_history_url(url)
            self._fill()

    def _open(self, it):
        url = it.data(Qt.UserRole)
        if url:
            self.on_navigate(url)

    def _clear_all(self):
        self.store.clear_history()
        self._fill()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.cfg = Config()
        self.store = Store(self.cfg)
        self.l = L(self.cfg)
        self.tabs = []
        self.closed_tabs = []
        self._mobile = False
        self._shortcut_objects = []
        self._private = False
        self._overlay = None

        self._drag_pos = None
        self._pending_drag = False

        self.setWindowTitle(APP_NAME)
        if ICON_FILE.exists():
            self.setWindowIcon(QIcon(str(ICON_FILE)))
        self.resize(int(self.cfg["window_width"]), int(self.cfg["window_height"]))
        self.setMinimumSize(560, 400)
        self.setMouseTracking(True)

        self.interceptor = AdBlockInterceptor(self.cfg)
        self.normal_profile = QWebEngineProfile.defaultProfile()
        self.normal_profile.setUrlRequestInterceptor(self.interceptor)
        self.normal_profile.setHttpUserAgent(self.cfg["custom_user_agent"])

        self.private_profile = QWebEngineProfile("private", self)
        self.private_profile.setUrlRequestInterceptor(self.interceptor)
        self.private_profile.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)
        self.private_profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        self.private_profile.setHttpUserAgent(self.cfg["custom_user_agent"])

        self._build()
        self._apply_style()
        self._shortcuts()
        self._restore_session()
        if not self.tabs:
            self.new_tab(GOOGLE_HOME)

    def paintEvent(self, e):
        p = self.cfg.palette() if hasattr(self, "cfg") else {"bg": "#141218"}
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        rect = self.rect().adjusted(0, 0, -1, -1)
        path.addRoundedRect(rect, CORNER_RADIUS, CORNER_RADIUS)
        painter.fillPath(path, QColor(p["bg"]))
        super().paintEvent(e)

    def _edge_at(self, pos):
        m = RESIZE_MARGIN
        w, h = self.width(), self.height()
        x, y = pos.x(), pos.y()
        edges = Qt.Edges()
        if x < m:
            edges |= Qt.LeftEdge
        if x > w - m:
            edges |= Qt.RightEdge
        if y < m:
            edges |= Qt.TopEdge
        if y > h - m:
            edges |= Qt.BottomEdge
        return edges

    def _update_cursor_for_edges(self, edges):
        if edges in (Qt.LeftEdge | Qt.TopEdge, Qt.RightEdge | Qt.BottomEdge):
            self.setCursor(Qt.SizeFDiagCursor)
        elif edges in (Qt.RightEdge | Qt.TopEdge, Qt.LeftEdge | Qt.BottomEdge):
            self.setCursor(Qt.SizeBDiagCursor)
        elif edges & (Qt.LeftEdge | Qt.RightEdge):
            self.setCursor(Qt.SizeHorCursor)
        elif edges & (Qt.TopEdge | Qt.BottomEdge):
            self.setCursor(Qt.SizeVerCursor)
        else:
            self.unsetCursor()

    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton:
            return super().mousePressEvent(e)
        pos = e.position().toPoint() if hasattr(e, "position") else e.pos()

        edges = self._edge_at(pos)
        if edges:
            wh = self.windowHandle()
            if wh is not None:
                wh.startSystemResize(edges)
            return

        if pos.y() < TITLEBAR_HEIGHT + 42:
            self._pending_drag = True
            self._drag_pos = pos
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        pos = e.position().toPoint() if hasattr(e, "position") else e.pos()

        if self._pending_drag and (e.buttons() & Qt.LeftButton):
            moved = (abs(pos.x() - self._drag_pos.x()) > 3 or
                     abs(pos.y() - self._drag_pos.y()) > 3)
            if moved:
                wh = self.windowHandle()
                if wh is not None:
                    wh.startSystemMove()
                self._pending_drag = False
                self._drag_pos = None
            return

        edges = self._edge_at(pos)
        self._update_cursor_for_edges(edges)
        super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        self._pending_drag = False
        self._drag_pos = None
        super().mouseReleaseEvent(e)

    def leaveEvent(self, e):
        self.unsetCursor()
        super().leaveEvent(e)

    def _build(self):
        central = QWidget()
        central.setObjectName("CentralRoot")
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        self.container = QFrame()
        self.container.setObjectName("RootFrame")
        self.container.setAttribute(Qt.WA_StyledBackground, True)
        self.root = QVBoxLayout(self.container)
        self.root.setContentsMargins(0, 0, 0, 0)
        self.root.setSpacing(0)
        outer.addWidget(self.container)

        self.tab_strip = TabStrip(self.cfg)
        self.tab_strip.add_requested.connect(lambda: self.new_tab(GOOGLE_HOME))
        self.tab_strip.tab_selected.connect(self._select_tab)
        self.tab_strip.tab_close_requested.connect(self.close_tab)
        self.tab_strip.add_window_controls(self.showMinimized, self._toggle_max, self.close)
        self.root.addWidget(self.tab_strip)

        self.toolbar = QFrame()
        self.toolbar.setObjectName("Toolbar")
        self.toolbar.setFixedHeight(42)
        self.toolbar.setAttribute(Qt.WA_StyledBackground, True)
        self.toolbar.setAttribute(Qt.WA_TranslucentBackground, True)
        self.toolbar.setAutoFillBackground(False)

        th = QHBoxLayout(self.toolbar)
        th.setContentsMargins(8, 3, 8, 6)
        th.setSpacing(3)

        self.btn_back = IconButton("arrow_back", 18, "Back")
        self.btn_back.clicked.connect(self._nav_back)
        th.addWidget(self.btn_back)
        self.btn_fwd = IconButton("arrow_forward", 18, "Forward")
        self.btn_fwd.clicked.connect(self._nav_forward)
        th.addWidget(self.btn_fwd)
        self.btn_reload = IconButton("refresh", 18, "Reload")
        self.btn_reload.clicked.connect(self._nav_reload)
        th.addWidget(self.btn_reload)
        self.btn_home = IconButton("home", 18, "Home")
        self.btn_home.clicked.connect(self._nav_home)
        th.addWidget(self.btn_home)

        self.url_wrap = QFrame()
        self.url_wrap.setObjectName("UrlWrap")
        self.url_wrap.setFixedHeight(32)
        self.url_wrap.setAttribute(Qt.WA_StyledBackground, True)
        uw = QHBoxLayout(self.url_wrap)
        uw.setContentsMargins(12, 0, 4, 0)
        uw.setSpacing(4)
        self.url_icon = IconLabel("lock_open", 12)
        self.url_icon.setObjectName("UrlIcon")
        self.url_icon.setFixedSize(16, 16)
        uw.addWidget(self.url_icon)
        self.url = QLineEdit()
        self.url.setObjectName("UrlBar")
        self.url.setPlaceholderText(self.l("search"))
        self.url.returnPressed.connect(self._on_url_enter)
        self.url.textChanged.connect(self._on_url_text_changed)
        uw.addWidget(self.url, 1)
        self.btn_star = IconButton("star_border", 16, "Bookmark")
        self.btn_star.setFixedSize(24, 24)
        self.btn_star.clicked.connect(self.toggle_bookmark_current)
        uw.addWidget(self.btn_star)
        th.addWidget(self.url_wrap, 1)

        self.btn_adblock = IconButton("shield", 18, "Adblock")
        self.btn_adblock.clicked.connect(lambda: self.open_overlay("Adblock", self._adblock_content()))
        th.addWidget(self.btn_adblock)
        self.btn_downloads = IconButton("download", 18, "Downloads")
        self.btn_downloads.clicked.connect(lambda: self.open_overlay(self.l("downloads"), self._downloads_content()))
        th.addWidget(self.btn_downloads)
        self.btn_private = IconButton("person", 18, "Private mode")
        self.btn_private.clicked.connect(self._toggle_private)
        th.addWidget(self.btn_private)
        self.btn_menu = IconButton("more_vert", 18, "Menu")
        self.btn_menu.clicked.connect(self._app_menu)
        th.addWidget(self.btn_menu)

        self.root.addWidget(self.toolbar)
        self.stack = QStackedWidget()
        self.root.addWidget(self.stack, 1)

    def _toggle_max(self):
        self.showNormal() if self.isMaximized() else self.showMaximized()

    def open_overlay(self, title, widget, width=680, height=520):
        if self._overlay is not None:
            try:
                self._overlay.hide()
                self._overlay.deleteLater()
            except Exception:
                pass
            self._overlay = None
        ov = OverlayDialog(self.container, title, widget, width, height)
        ov.closed.connect(lambda: setattr(self, "_overlay", None))
        self._overlay = ov
        ov.show_with_anim()

    def _adblock_content(self):
        w = QWidget()
        w.setObjectName("OverlayBody")
        w.setAttribute(Qt.WA_StyledBackground, True)
        v = QVBoxLayout(w)
        v.setContentsMargins(24, 20, 24, 20)
        v.setSpacing(12)
        cnt = QLabel(f"{self.interceptor.blocked}")
        cnt.setObjectName("BigNumber")
        cnt.setAlignment(Qt.AlignCenter)
        v.addWidget(cnt)
        lbl = QLabel("blocked")
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setObjectName("BigNumberLabel")
        v.addWidget(lbl)
        tip = QLabel("Ad blocking is active.")
        tip.setWordWrap(True)
        tip.setAlignment(Qt.AlignCenter)
        v.addWidget(tip)
        v.addStretch(1)
        return w

    def _downloads_content(self):
        w = QWidget()
        w.setObjectName("OverlayBody")
        w.setAttribute(Qt.WA_StyledBackground, True)
        v = QVBoxLayout(w)
        v.setContentsMargins(16, 12, 16, 12)
        v.setSpacing(6)
        lst = QListWidget()
        for d in reversed(self.store.downloads[-50:]):
            it = QListWidgetItem(f"{Path(d['path']).name}\n{d['url'][:80]}")
            it.setData(Qt.UserRole, d["path"])
            lst.addItem(it)

        def _open(it):
            p = it.data(Qt.UserRole)
            if p and Path(p).exists():
                QDesktopServices.openUrl(QUrl.fromLocalFile(p))

        lst.itemDoubleClicked.connect(_open)
        v.addWidget(lst, 1)
        row = QHBoxLayout()
        b1 = QPushButton(self.l("open_folder"))
        b1.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(self.cfg["downloads_dir"])))
        b2 = QPushButton(self.l("clear"))
        b2.clicked.connect(lambda: (self.store.clear_downloads(), lst.clear()))
        row.addWidget(b1)
        row.addWidget(b2)
        row.addStretch(1)
        v.addLayout(row)
        return w

    def _history_content(self):
        return HistoryContent(self.store, self.navigate)

    def _bookmarks_content(self):
        w = QWidget()
        w.setObjectName("OverlayBody")
        w.setAttribute(Qt.WA_StyledBackground, True)
        v = QVBoxLayout(w)
        v.setContentsMargins(16, 12, 16, 12)
        v.setSpacing(6)
        lst = QListWidget()
        for i, b in enumerate(self.store.bookmarks):
            it = QListWidgetItem(f"{b.get('title', b['url'])[:80]}\n{b['url']}")
            it.setData(Qt.UserRole, (i, b["url"]))
            lst.addItem(it)

        def _open(it):
            d = it.data(Qt.UserRole)
            if d:
                self.navigate(d[1])
                self._close_overlay()

        lst.itemDoubleClicked.connect(_open)
        v.addWidget(lst, 1)
        return w

    def _find_content(self):
        w = QWidget()
        w.setObjectName("OverlayBody")
        w.setAttribute(Qt.WA_StyledBackground, True)
        v = QHBoxLayout(w)
        v.setContentsMargins(16, 12, 16, 12)
        le = QLineEdit()
        le.setPlaceholderText("Find on page...")
        v.addWidget(le, 1)
        case = QCheckBox("Aa")
        v.addWidget(case)

        def do(back=False):
            t = self._current_tab()
            if t:
                t.find(le.text(), case.isChecked(), back)

        le.returnPressed.connect(lambda: do(False))
        b1 = QPushButton("↑")
        b1.clicked.connect(lambda: do(True))
        b2 = QPushButton("↓")
        b2.clicked.connect(lambda: do(False))
        v.addWidget(b1)
        v.addWidget(b2)
        le.setFocus()
        return w

    def _about_content(self):
        return AboutContent(self.cfg, self.l)

    def _settings_content(self):
        sc = SettingsContent(self.cfg, self.l)
        sc.changed.connect(self._apply_style)
        return sc

    def _close_overlay(self):
        if self._overlay:
            self._overlay.close_with_anim()

    def _apply_style(self):
        self.setStyleSheet("")
        p = self.cfg.palette()
        ui = int(self.cfg["ui_font_size"])
        r = CORNER_RADIUS
        toolbar_bg = p["toolbar_bg"] if self.cfg["blur_toolbar"] else p["bg"]
        overlay_bg = p["overlay_bg"]

        css = f"""
        QWidget#CentralRoot {{ background: transparent; }}

        QFrame#RootFrame {{
            background: {p['bg']};
            border: none;
            border-radius: {r}px;
        }}

        * {{ font-family: "Open Sans", "Noto Sans", sans-serif; font-size: {ui}pt; color: {p['fg']}; }}

        QToolButton#IconBtn, QToolButton#AddTabBtn, QToolButton#WinBtn, QToolButton#WinBtnClose {{
            font-family: "Material Symbols Rounded";
        }}
        QLabel#Favicon, QLabel#MenuIcon, QLabel#SectionIcon, QLabel#UrlIcon {{
            font-family: "Material Symbols Rounded";
        }}

        QFrame#TabStrip {{
            background: {toolbar_bg};
            border-top-left-radius: {r}px;
            border-top-right-radius: {r}px;
            border: none;
        }}
        QFrame#Toolbar {{
            background: {toolbar_bg};
            border: none;
            border-top-left-radius: {r}px;
            border-top-right-radius: {r}px;
        }}
        QFrame#WinBtns {{ background: transparent; border: none; }}

        QToolButton#IconBtn, QToolButton#AddTabBtn, QToolButton#WinBtn, QToolButton#WinBtnClose {{
            background: transparent; border: none; color: {p['fg_variant']};
            border-radius: 12px;
        }}
        QToolButton#IconBtn:hover, QToolButton#AddTabBtn:hover, QToolButton#WinBtn:hover {{
            background: {p['surface_high']}; color: {p['fg']};
        }}
        QToolButton#IconBtn:pressed, QToolButton#AddTabBtn:pressed {{
            background: {p['accent_container']}; color: {p['on_accent_container']};
        }}
        QToolButton#WinBtnClose:hover {{ background: #C42B1C; color: #FFFFFF; }}

        QFrame#ChromeTab {{
            background: {p['tab_hover']}; border: none;
            border-top-left-radius: 8px; border-top-right-radius: 8px;
        }}
        QFrame#ChromeTab[hover="true"] {{ background: {p['surface_max']}; }}
        QFrame#ChromeTab[active="true"] {{ background: {p['tab_active']}; }}
        QLabel#TabTitle {{ color: {p['fg']}; font-size: {max(8, ui-1)}pt; background: transparent; }}
        QFrame#ChromeTab[active="true"] QLabel#TabTitle {{ color: {p['fg']}; font-weight: 700; }}
        QLabel#Favicon {{ background: transparent; color: {p['fg_variant']}; }}

        QFrame#UrlWrap {{ background: {p['surface']}; border: none; border-radius: 16px; }}
        QFrame#UrlWrap:hover {{ background: {p['surface_high']}; }}
        QLineEdit#UrlBar {{
            background: transparent; border: none;
            padding: 4px 2px; color: {p['fg']};
            selection-background-color: {p['accent']};
            selection-color: {p['on_accent']};
        }}
        QLabel#UrlIcon {{ color: {p['fg_variant']}; background: transparent; }}

        QLineEdit, QListWidget, QLabel, QPlainTextEdit {{
            selection-background-color: {p['accent']};
            selection-color: {p['on_accent']};
        }}

        QFrame#OverlayBackdrop {{ background: rgba(0,0,0,0.55); border-radius: {r}px; }}
        QFrame#OverlayContent {{
            background: {overlay_bg};
            border: none;
            border-radius: 20px;
        }}
        QFrame#OverlayHead {{
            background: {p['surface_high']};
            border-top-left-radius: 20px; border-top-right-radius: 20px;
            border: none;
        }}
        QLabel#OverlayTitle {{
            font-size: {ui+4}pt; font-weight: 700; color: {p['fg']};
            background: transparent;
        }}
        QWidget#OverlayBody {{ background: {overlay_bg}; }}

        QWidget#SettingsContent {{ background: {overlay_bg}; }}
        QFrame#SettingsSidebar {{
            background: {p['surface_low']};
            border: none;
            border-top-left-radius: 20px;
            border-bottom-left-radius: 20px;
        }}
        QStackedWidget#SettingsStack {{ background: {overlay_bg}; }}
        QScrollArea#SettingsScroll {{ background: {overlay_bg}; }}
        QWidget#SettingsInner {{ background: {overlay_bg}; }}

        QLabel#SettingsTitle {{
            font-size: {ui+6}pt; font-weight: 800; color: {p['fg']};
            background: transparent; padding: 6px 12px;
        }}
        QToolButton#SettingsCatBtn {{
            background: transparent; color: {p['fg_variant']};
            border: none; border-radius: 10px;
            padding: 0 12px; font-weight: 600; text-align: left;
        }}
        QToolButton#SettingsCatBtn:hover {{ background: {p['surface_high']}; color: {p['fg']}; }}
        QToolButton#SettingsCatBtn:checked {{
            background: {p['accent_container']}; color: {p['on_accent_container']}; font-weight: 700;
        }}

        QWidget#HistoryContent {{ background: {overlay_bg}; }}

        QListWidget {{
            background: {p['surface_low']}; color: {p['fg']};
            border: none; border-radius: 14px; padding: 6px; outline: none;
        }}
        QListWidget::item {{ padding: 10px 14px; border-radius: 10px; }}
        QListWidget::item:selected {{ background: {p['accent_container']}; color: {p['on_accent_container']}; }}
        QListWidget::item:hover {{ background: {p['surface_high']}; }}

        QLineEdit, QSpinBox, QComboBox {{
            background: {p['surface_high']}; color: {p['fg']};
            border: none; border-radius: 10px; padding: 6px 12px;
        }}
        QLineEdit:focus, QComboBox:focus {{ background: {p['surface_max']}; }}

        QPushButton {{
            background: {p['surface_high']}; color: {p['fg']};
            border: none; border-radius: 20px; padding: 8px 20px; font-weight: 600;
        }}
        QPushButton:hover {{ background: {p['surface_max']}; }}
        QPushButton:pressed {{ background: {p['accent_container']}; color: {p['on_accent_container']}; }}

        QMenu#FirefoxMenu {{
            background: {overlay_bg};
            border: none;
            border-radius: 14px;
            padding: 8px;
        }}
        QMenu {{
            background: {overlay_bg}; color: {p['fg']};
            border: none; border-radius: 12px; padding: 6px;
        }}
        QMenu::item {{ padding: 8px 24px 8px 14px; border-radius: 8px; }}
        QMenu::item:selected {{ background: {p['accent_container']}; color: {p['on_accent_container']}; }}
        QMenu::separator {{ height: 1px; background: {p['surface_max']}; margin: 4px 8px; }}

        QFrame#MenuSeparator {{ background: {p['surface_max']}; margin: 4px 10px; max-height: 1px; }}
        QWidget#MenuRow {{ background: transparent; }}
        QLabel#MenuLabel {{ color: {p['fg']}; font-size: {ui}pt; background: transparent; }}
        QLabel#MenuShortcut {{ color: {p['fg_variant']}; font-size: {max(8, ui-2)}pt; background: transparent; }}
        QLabel#MenuIcon {{ color: {p['fg_variant']}; background: transparent; }}

        QScrollBar:vertical {{ background: transparent; width: 8px; margin: 2px; }}
        QScrollBar::handle:vertical {{ background: {p['surface_max']}; border-radius: 4px; min-height: 30px; }}
        QScrollBar::handle:vertical:hover {{ background: {p['fg_variant']}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        QScrollBar:horizontal {{ background: transparent; height: 8px; margin: 2px; }}
        QScrollBar::handle:horizontal {{ background: {p['surface_max']}; border-radius: 4px; min-width: 30px; }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

        QFrame#SettingRow {{
            background: {p['surface_low']};
            border: none; border-radius: 12px;
        }}
        QFrame#SettingRow:hover {{ background: {p['surface']}; }}
        QLabel#SettingLabel {{ font-size: {ui+1}pt; color: {p['fg']}; background: transparent; }}
        QLabel#SettingHint {{ font-size: {max(8, ui-2)}pt; color: {p['fg_variant']}; background: transparent; }}
        QLabel#SectionTitle {{ font-size: {ui+3}pt; font-weight: 700; color: {p['fg']}; background: transparent; }}
        QLabel#SectionHint {{ font-size: {ui}pt; color: {p['fg_variant']}; background: transparent; }}
        QLabel#SliderVal {{ color: {p['accent']}; font-weight: 700; background: transparent; }}

        QToolButton#ModeBtn, QToolButton#LangBtn {{
            background: {p['surface_high']}; color: {p['fg']};
            border: none; border-radius: 16px; padding: 0 14px; font-weight: 600;
        }}
        QToolButton#ModeBtn:hover, QToolButton#LangBtn:hover {{ background: {p['surface_max']}; }}
        QToolButton#ModeBtn:checked, QToolButton#LangBtn:checked {{
            background: {p['accent_container']}; color: {p['on_accent_container']}; font-weight: 700;
        }}

        QToolButton#AccentDot {{ border: 3px solid transparent; border-radius: 17px; }}
        QToolButton#AccentDot:checked {{ border: 3px solid {p['fg']}; }}

        QSlider::groove:horizontal {{ height: 4px; background: {p['surface_max']}; border-radius: 2px; }}
        QSlider::sub-page:horizontal {{ background: {p['accent']}; border-radius: 2px; }}
        QSlider::handle:horizontal {{ background: {p['accent']}; width: 16px; height: 16px;
                                       margin: -6px 0; border-radius: 8px; }}

        QComboBox::drop-down {{ border: none; width: 22px; }}
        QComboBox QAbstractItemView {{
            background: {overlay_bg}; color: {p['fg']};
            border: none; border-radius: 12px; padding: 4px;
            selection-background-color: {p['accent_container']};
            selection-color: {p['on_accent_container']};
        }}

        QFrame#MS_Board {{ background: {p['surface']}; border: none; border-radius: 18px; }}
        QPushButton#MS_Cell {{
            background: {p['surface_high']}; border: none; border-radius: 8px;
            font-weight: 700; font-size: {ui+3}pt; color: {p['fg']};
        }}
        QPushButton#MS_Cell:hover {{ background: {p['accent_soft']}; }}
        QPushButton#MS_Cell[state="flag"] {{ background: {p['surface_max']}; }}
        QPushButton#MS_Cell[state="mine"] {{ background: {p['error']}; color: white; }}
        QPushButton#MS_Cell[state="boom"] {{ background: {p['error']}; color: white; }}
        QPushButton#MS_Cell[state^="r"] {{ background: {p['surface_max']}; }}
        QLabel#MS_Title {{ font-size: 24pt; background: transparent; }}
        QLabel#MS_Status {{ color: {p['fg_variant']}; font-size: {ui+2}pt; background: transparent; }}
        QPushButton#MS_Restart {{
            background: {p['accent']}; color: {p['on_accent']};
            border: none; border-radius: 20px; padding: 10px 24px; font-weight: 700;
        }}

        QFrame#OfflineHead {{ background: {p['bg']}; }}
        QLabel#OfflineTitle {{ font-size: {ui+16}pt; font-weight: 300; color: {p['fg']}; background: transparent; }}
        QLabel#OfflineSub {{ font-size: {ui+1}pt; color: {p['fg_variant']}; background: transparent; }}

        QLabel#AboutName {{ font-size: 30pt; font-weight: 800; color: {p['accent']}; background: transparent; }}
        QLabel#AboutTagline {{ font-size: {ui+1}pt; color: {p['fg_variant']}; background: transparent; }}
        QFrame#AboutInfo {{ background: {p['surface_low']}; border-radius: 18px; }}
        QLabel#AboutKey {{ color: {p['fg_variant']}; background: transparent; }}
        QLabel#AboutVal {{ color: {p['fg']}; font-weight: 700; background: transparent; }}
        QLabel#AboutQuote {{ font-style: italic; color: {p['fg_variant']};
                             font-size: {ui+1}pt; background: transparent; }}

        QLabel#BigNumber {{ color: {p['accent']}; font-size: 32pt; font-weight: 800; background: transparent; }}
        QLabel#BigNumberLabel {{ color: {p['fg_variant']}; background: transparent; }}
        QScrollArea {{ background: transparent; border: none; }}
        """
        self.setStyleSheet(css)
        self.url.setPlaceholderText(self.l("search"))
        if self._overlay:
            try:
                self._overlay.setGeometry(0, 0, self.container.width(), self.container.height())
            except Exception:
                pass

    def _apply_blur_hint(self):
        try:
            wh = self.windowHandle()
            if wh is not None:
                wh.setProperty("_KDE_NET_WM_BLUR_BEHIND_REGION", 1)
            if os.environ.get("XDG_SESSION_TYPE", "").lower() == "x11":
                try:
                    wid = int(self.winId())
                    subprocess.Popen(
                        ["xprop", "-id", str(wid),
                         "-f", "_KDE_NET_WM_BLUR_BEHIND_REGION", "32c",
                         "-set", "_KDE_NET_WM_BLUR_BEHIND_REGION", "0"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    pass
        except Exception:
            pass

    def new_tab(self, url=None, background=False, private=False):
        profile = self.private_profile if (private or self._private) else self.normal_profile
        tab = BrowserTab(self.cfg, self.store, profile, self, url or GOOGLE_HOME, private or self._private)
        tab.title_changed.connect(lambda t, tb=tab: self._on_tab_title(tb, t))
        tab.url_changed.connect(lambda u, tb=tab: self._on_tab_url(tb, u))
        tab.icon_changed.connect(lambda i, tb=tab: self.tab_strip.set_icon(tb, i))
        tab.load_started.connect(lambda tb=tab: self._on_tab_load_started(tb))
        tab.load_finished.connect(lambda ok, tb=tab: self._on_tab_load_finished(tb, ok))
        self.stack.addWidget(tab)
        self.tab_strip.add_chip(tab, self.l("new_tab"))
        self.tabs.append(tab)
        if not background:
            self._select_tab(tab)
        return tab

    def _select_tab(self, tab):
        self.stack.setCurrentWidget(tab)
        self.tab_strip.set_active(tab)
        self._sync_url_bar(tab)
        tab.view.setFocus()

    def _current_tab(self):
        w = self.stack.currentWidget()
        return w if isinstance(w, BrowserTab) else None

    def close_tab(self, tab=None):
        tab = tab or self._current_tab()
        if tab not in self.tabs:
            return
        if len(self.tabs) == 1:
            self.close()
            return
        self.closed_tabs.append(tab.url())
        self.tab_strip.remove_chip(tab)
        self.stack.removeWidget(tab)
        self.tabs.remove(tab)
        QTimer.singleShot(160, tab.deleteLater)
        self._select_tab(self.tabs[-1])

    def _on_tab_title(self, tab, t):
        self.tab_strip.set_title(tab, t or self.l("new_tab"))
        if tab is self._current_tab():
            self.setWindowTitle(f"{t} — {APP_NAME}")

    def _on_tab_url(self, tab, u):
        if tab is self._current_tab():
            self._sync_url_bar(tab)
            self._update_bookmark_icon()

    def _on_tab_load_started(self, tab):
        if tab is self._current_tab():
            self.btn_reload.setText(_icon_char("close"))

    def _on_tab_load_finished(self, tab, ok):
        if tab is self._current_tab():
            self.btn_reload.setText(_icon_char("refresh"))

    def _sync_url_bar(self, tab):
        u = tab.url()
        self.url.setText("" if u == "about:blank" else u)
        self._update_url_icon(u)

    def _update_url_icon(self, u):
        p = self.cfg.palette()
        if u.startswith("https://"):
            self.url_icon.setText(_icon_char("lock"))
            self.url_icon.setStyleSheet(f"color:{p['success']};")
        elif u.startswith("http://"):
            self.url_icon.setText(_icon_char("lock_open"))
            self.url_icon.setStyleSheet(f"color:{p['warning']};")
        else:
            self.url_icon.setText(_icon_char("public"))
            self.url_icon.setStyleSheet(f"color:{p['fg_variant']};")

    def _on_url_text_changed(self, t):
        self._update_url_icon(t)

    def _update_bookmark_icon(self):
        tab = self._current_tab()
        if not tab:
            return
        p = self.cfg.palette()
        if self.store.is_bookmarked(tab.url()):
            self.btn_star.setText(_icon_char("star"))
            self.btn_star.setStyleSheet(f"color:{p['accent']};")
        else:
            self.btn_star.setText(_icon_char("star_border"))
            self.btn_star.setStyleSheet("")

    def toggle_bookmark_current(self):
        tab = self._current_tab()
        if not tab:
            return
        u = tab.url()
        if not u or u.startswith("clor://"):
            return
        if self.store.is_bookmarked(u):
            self.store.bookmarks = [b for b in self.store.bookmarks if b["url"] != u]
            BOOKMARKS_FILE.write_text(json.dumps(self.store.bookmarks, indent=2))
        else:
            self.store.add_bookmark(u, tab.title())
        self._update_bookmark_icon()

    def navigate(self, u):
        t = self._current_tab()
        if t:
            t.navigate(u)
        else:
            self.new_tab(u)

    def _on_url_enter(self):
        t = self.url.text().strip()
        if t:
            self.navigate(t)

    def _nav_back(self):
        t = self._current_tab()
        t and t.back()

    def _nav_forward(self):
        t = self._current_tab()
        t and t.forward()

    def _nav_reload(self):
        t = self._current_tab()
        t and t.reload()

    def _nav_home(self):
        t = self._current_tab()
        t and t.home()

    def _toggle_private(self):
        self._private = not self._private
        p = self.cfg.palette()
        if self._private:
            self.btn_private.setText(_icon_char("incognito"))
            self.btn_private.setStyleSheet(
                f"color:{p['on_accent_container']}; background:{p['accent_container']}; border-radius:8px;")
            self.new_tab(GOOGLE_HOME, private=True)
        else:
            self.btn_private.setText(_icon_char("person"))
            self.btn_private.setStyleSheet("")

    def _restore_session(self):
        if not self.cfg["restore_session"] or not SESSION_FILE.exists():
            return
        try:
            data = json.loads(SESSION_FILE.read_text())
            for u in data.get("tabs", [])[:20]:
                self.new_tab(u, background=True)
        except Exception:
            pass

    def _save_session(self):
        if not self.cfg["restore_session"]:
            return
        try:
            urls = [t.url() for t in self.tabs if t.url() and not t.url().startswith("clor://")]
            SESSION_FILE.write_text(json.dumps({"tabs": urls}, indent=2))
        except Exception:
            pass

    def _app_menu(self):
        m = FirefoxMenu(self)
        m.setMinimumWidth(260)

        m.add_item("tab",       self.l("new_tab"),    lambda: self.new_tab(GOOGLE_HOME), "Ctrl+T")
        m.add_item("windows",   self.l("new_window"), lambda: MainWindow().show(), "Ctrl+N")
        m.add_item("close",     self.l("close_tab"),  lambda: self.close_tab(), "Ctrl+W")
        m.add_item("history",   self.l("history"),    lambda: self.open_overlay(self.l("history"), self._history_content()), "Ctrl+H")
        m.add_item("star",      self.l("bookmarks"),  lambda: self.open_overlay(self.l("bookmarks"), self._bookmarks_content()), "Ctrl+Shift+O")
        m.add_item("download",  self.l("downloads"),  lambda: self.open_overlay(self.l("downloads"), self._downloads_content()), "Ctrl+J")
        m.add_separator_line()
        m.add_item("fullscreen", self.l("fullscreen"), self._toggle_fullscreen, "F11")
        m.add_item("print",      self.l("print"),      self._print_page, "Ctrl+P")
        m.add_separator_line()
        m.add_item("settings",  self.l("settings"),   lambda: self.open_overlay(self.l("settings"), self._settings_content(), 900, 620), "Ctrl+,")
        m.add_item("info",      self.l("about"),      lambda: self.open_overlay(self.l("about"), self._about_content(), 560, 560))
        m.add_separator_line()
        m.add_item("close",     self.l("quit"),       self.close, "Ctrl+Q")

        m.exec(self.btn_menu.mapToGlobal(QPoint(0, self.btn_menu.height() + 4)))

    def _toggle_fullscreen(self):
        self.showNormal() if self.isFullScreen() else self.showFullScreen()

    def _print_page(self):
        t = self._current_tab()
        if not t:
            return
        path, _ = QFileDialog.getSaveFileName(self, "PDF", str(HOME / "page.pdf"), "PDF (*.pdf)")
        if path:
            t.view.page().printToPdf(path)

    def _shortcuts(self):
        for s in self._shortcut_objects:
            try:
                s.setEnabled(False)
                s.deleteLater()
            except Exception:
                pass
        self._shortcut_objects = []
        mapping = {
            "Ctrl+T": lambda: self.new_tab(GOOGLE_HOME),
            "Ctrl+N": lambda: MainWindow().show(),
            "Ctrl+W": lambda: self.close_tab(),
            "Ctrl+Shift+T": lambda: self.new_tab(self.closed_tabs.pop()) if self.closed_tabs else None,
            "Ctrl+Tab": lambda: self._cycle(+1),
            "Ctrl+Shift+Tab": lambda: self._cycle(-1),
            "Ctrl+L": lambda: (self.url.setFocus(), self.url.selectAll()),
            "Ctrl+F": lambda: self.open_overlay(self.l("find"), self._find_content(), 500, 80),
            "F5": self._nav_reload,
            "Alt+Left": self._nav_back,
            "Alt+Right": self._nav_forward,
            "Alt+Home": self._nav_home,
            "Ctrl+H": lambda: self.open_overlay(self.l("history"), self._history_content()),
            "Ctrl+Shift+O": lambda: self.open_overlay(self.l("bookmarks"), self._bookmarks_content()),
            "Ctrl+J": lambda: self.open_overlay(self.l("downloads"), self._downloads_content()),
            "Ctrl+,": lambda: self.open_overlay(self.l("settings"), self._settings_content(), 900, 620),
            "F11": self._toggle_fullscreen,
            "Ctrl+P": self._print_page,
            "Ctrl+Q": self.close,
        }
        for seq, cb in mapping.items():
            try:
                s = QShortcut(QKeySequence(seq), self)
                s.activated.connect(cb)
                self._shortcut_objects.append(s)
            except Exception:
                pass

    def _cycle(self, d):
        if not self.tabs:
            return
        cur = self._current_tab()
        if cur not in self.tabs:
            return
        i = self.tabs.index(cur)
        self._select_tab(self.tabs[(i + d) % len(self.tabs)])

    def _on_download_requested(self, d):
        if self.cfg["ask_download_location"]:
            path, _ = QFileDialog.getSaveFileName(
                self, "Save", str(Path(self.cfg["downloads_dir"]) / d.downloadFileName()))
            if not path:
                d.cancel()
                return
            d.setDownloadFileName(path)
        self.store.add_download(str(Path(d.downloadDirectory()) / d.downloadFileName()), d.url().toString())

    def resizeEvent(self, e):
        super().resizeEvent(e)
        m = self.width() < MOBILE_BREAKPOINT
        if m != self._mobile:
            self._mobile = m
            self._apply_mobile()
        if self._overlay:
            try:
                self._overlay.setGeometry(0, 0, self.container.width(), self.container.height())
            except Exception:
                pass

    def _apply_mobile(self):
        self.btn_home.setVisible(not self._mobile)
        self.btn_downloads.setVisible(not self._mobile)
        self.btn_adblock.setVisible(not self._mobile)

    def closeEvent(self, e):
        self.cfg["window_width"] = self.width()
        self.cfg["window_height"] = self.height()
        self.cfg.save()
        self._save_session()
        super().closeEvent(e)

def _download(url, dst):
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, dst)
        return True
    except Exception as e:
        print(f"[Clor] download failed {url}: {e}")
        return False

def first_time_setup():
    for d in (CONFIG_DIR, CACHE_DIR, BIN_DIR, APPS_DIR, ICONS_DIR, FONTS_DIR):
        d.mkdir(parents=True, exist_ok=True)
    if not ICON_FILE.exists():
        _download(ICON_URL, ICON_FILE)
    if not MSYMBOL_FILE.exists() and _download(MSYMBOL_URL, MSYMBOL_FILE):
        try:
            subprocess.Popen(["fc-cache", "-f"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
    try:
        if BIN_LINK.exists() or BIN_LINK.is_symlink():
            BIN_LINK.unlink()
        BIN_LINK.symlink_to(SELF_PATH)
        BIN_LINK.chmod(0o755)
    except Exception:
        pass
    desktop = (
        "[Desktop Entry]\nType=Application\nVersion=1.0\n"
        f"Name={APP_NAME}\nGenericName=Web Browser\nComment=Material Design 3 Browser\n"
        f"Exec={sys.executable} {SELF_PATH} %u\nIcon={ICON_FILE}\n"
        "Terminal=false\nCategories=Network;WebBrowser;\n"
        "MimeType=text/html;text/xml;application/xhtml+xml;x-scheme-handler/http;x-scheme-handler/https;\n"
        "StartupNotify=true\nStartupWMClass=Clor\n"
    )
    DESKTOP_FILE.write_text(desktop)
    try:
        subprocess.Popen(["update-desktop-database", str(APPS_DIR)],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def main():
    marker = CONFIG_DIR / ".installed_v027"
    if not marker.exists():
        first_time_setup()
        marker.write_text("ok")

    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_NAME)
    app.setOrganizationName(DEVELOPER)
    app.setDesktopFileName("clor")
    if ICON_FILE.exists():
        app.setWindowIcon(QIcon(str(ICON_FILE)))
    app.setFont(QFont("Open Sans"))
    load_icon_font()
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    w = MainWindow()
    w.normal_profile.downloadRequested.connect(w._on_download_requested)
    w.private_profile.downloadRequested.connect(w._on_download_requested)
    w.show()
    QTimer.singleShot(300, w._apply_blur_hint)
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
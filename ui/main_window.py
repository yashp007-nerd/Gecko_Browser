"""
ui/main_window.py
-----------------
MainWindow — assembles all browser chrome:
  - Navigation toolbar (Back, Forward, Refresh, Stop, Home, New-Tab button)
  - Smart URL bar
  - Thin gradient progress bar (sits between toolbar and tab content)
  - QTabWidget (closeable tabs)
  - Status bar (shows hovered link URL)
  - Keyboard shortcuts
"""

from __future__ import annotations

import os
from typing import Optional

from PyQt5.QtCore import QUrl, Qt, QSize
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap, QPainter, QColor
from PyQt5.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QToolBar,
    QAction,
    QProgressBar,
    QStatusBar,
    QWidget,
    QVBoxLayout,
    QShortcut,
    QLabel,
    QSizePolicy,
    QApplication,
)

from ui.url_bar import URLBar
from ui.browser_tab import BrowserTab

HOME_URL = "https://www.google.com"
APP_TITLE = "NovaBrowser"


# ── Icon helpers ──────────────────────────────────────────────────────────────

def _svg_icon(svg_text: str, size: int = 20) -> QIcon:
    """Render an inline SVG string to a QIcon."""
    try:
        from PyQt5.QtSvg import QSvgRenderer
        from PyQt5.QtCore import QByteArray
        renderer = QSvgRenderer(QByteArray(svg_text.encode()))
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return QIcon(pixmap)
    except Exception:
        return QIcon()


# Minimal inline SVG icons (monochrome, stroked)
_ICONS = {
    "back": '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">'
            '<path d="M15 18l-6-6 6-6" stroke="#e8eaf0" stroke-width="2.2" '
            'stroke-linecap="round" stroke-linejoin="round"/></svg>',

    "forward": '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">'
               '<path d="M9 18l6-6-6-6" stroke="#e8eaf0" stroke-width="2.2" '
               'stroke-linecap="round" stroke-linejoin="round"/></svg>',

    "refresh": '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">'
               '<path d="M1 4v6h6" stroke="#e8eaf0" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'
               '<path d="M3.51 15a9 9 0 1 0 .49-4.5" stroke="#e8eaf0" stroke-width="2.2" '
               'stroke-linecap="round" stroke-linejoin="round"/></svg>',

    "stop": '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">'
            '<line x1="18" y1="6" x2="6" y2="18" stroke="#e05555" stroke-width="2.2" stroke-linecap="round"/>'
            '<line x1="6" y1="6" x2="18" y2="18" stroke="#e05555" stroke-width="2.2" stroke-linecap="round"/></svg>',

    "home": '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">'
            '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" stroke="#e8eaf0" '
            'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'
            '<polyline points="9 22 9 12 15 12 15 22" stroke="#e8eaf0" stroke-width="2.2" '
            'stroke-linecap="round" stroke-linejoin="round"/></svg>',

    "new_tab": '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">'
               '<line x1="12" y1="5" x2="12" y2="19" stroke="#4d8ef0" stroke-width="2.2" stroke-linecap="round"/>'
               '<line x1="5" y1="12" x2="19" y2="12" stroke="#4d8ef0" stroke-width="2.2" stroke-linecap="round"/></svg>',
}


# ── MainWindow ────────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    """Root window — assembles all browser chrome and mediates signals."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1280, 800)
        self.setMinimumSize(800, 500)

        self._build_toolbar()
        self._build_progress_bar()
        self._build_tabs()
        self._build_status_bar()
        self._build_shortcuts()

        # Open the first tab
        self.add_new_tab(HOME_URL, "New Tab")

    # ── Build helpers ─────────────────────────────────────────────────────

    def _build_toolbar(self) -> None:
        tb = QToolBar("Navigation")
        tb.setObjectName("navToolbar")
        tb.setMovable(False)
        tb.setIconSize(QSize(20, 20))
        tb.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.addToolBar(tb)

        # Back
        self._act_back = QAction(_svg_icon(_ICONS["back"]), "Back", self)
        self._act_back.setToolTip("Back  (Alt+Left)")
        self._act_back.triggered.connect(lambda: self._current_tab() and self._current_tab().safe_back())
        tb.addAction(self._act_back)

        # Forward
        self._act_fwd = QAction(_svg_icon(_ICONS["forward"]), "Forward", self)
        self._act_fwd.setToolTip("Forward  (Alt+Right)")
        self._act_fwd.triggered.connect(lambda: self._current_tab() and self._current_tab().safe_forward())
        tb.addAction(self._act_fwd)

        # Refresh
        self._act_reload = QAction(_svg_icon(_ICONS["refresh"]), "Refresh", self)
        self._act_reload.setToolTip("Refresh  (F5)")
        self._act_reload.triggered.connect(lambda: self._current_tab() and self._current_tab().reload())
        tb.addAction(self._act_reload)

        # Stop
        self._act_stop = QAction(_svg_icon(_ICONS["stop"]), "Stop", self)
        self._act_stop.setToolTip("Stop loading  (Esc)")
        self._act_stop.triggered.connect(lambda: self._current_tab() and self._current_tab().stop())
        self._act_stop.setEnabled(False)
        tb.addAction(self._act_stop)

        # Home
        self._act_home = QAction(_svg_icon(_ICONS["home"]), "Home", self)
        self._act_home.setToolTip("Home page")
        self._act_home.triggered.connect(self._navigate_home)
        tb.addAction(self._act_home)

        tb.addSeparator()

        # URL bar (stretches to fill remaining width)
        self._url_bar = URLBar(self)
        self._url_bar.navigate_requested.connect(self._on_url_navigate)
        self._url_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        tb.addWidget(self._url_bar)

        tb.addSeparator()

        # New tab button
        self._act_new_tab = QAction(_svg_icon(_ICONS["new_tab"]), "New Tab", self)
        self._act_new_tab.setToolTip("New tab  (Ctrl+T)")
        self._act_new_tab.triggered.connect(lambda: self.add_new_tab(HOME_URL, "New Tab"))
        tb.addAction(self._act_new_tab)

    def _build_progress_bar(self) -> None:
        """Thin gradient progress bar injected between toolbar and content."""
        self._progress = QProgressBar(self)
        self._progress.setObjectName("loadProgress")
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setTextVisible(False)
        self._progress.setFixedHeight(3)
        self._progress.hide()

        # Wrap in a container widget that sits as the central widget wrapper
        self._central = QWidget()
        layout = QVBoxLayout(self._central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._progress)

        # Tab widget will be added to this layout below
        self.setCentralWidget(self._central)

    def _build_tabs(self) -> None:
        self._tabs = QTabWidget()
        self._tabs.setObjectName("tabWidget")
        self._tabs.setDocumentMode(True)
        self._tabs.setTabsClosable(True)
        self._tabs.setMovable(True)
        self._tabs.tabCloseRequested.connect(self._close_tab)
        self._tabs.currentChanged.connect(self._on_tab_changed)
        # Double-click empty tab-bar area → new tab
        self._tabs.tabBarDoubleClicked.connect(
            lambda idx: self.add_new_tab(HOME_URL, "New Tab") if idx == -1 else None
        )
        self._central.layout().addWidget(self._tabs)

    def _build_status_bar(self) -> None:
        self._status = QStatusBar()
        self._status.setObjectName("statusBar")
        self.setStatusBar(self._status)

    def _build_shortcuts(self) -> None:
        shortcuts = [
            (Qt.CTRL + Qt.Key_T,          lambda: self.add_new_tab(HOME_URL, "New Tab")),
            (Qt.CTRL + Qt.Key_W,          lambda: self._close_tab(self._tabs.currentIndex())),
            (Qt.CTRL + Qt.Key_L,          lambda: (self._url_bar.setFocus(), self._url_bar.selectAll())),
            (Qt.ALT + Qt.Key_Left,        lambda: self._current_tab() and self._current_tab().safe_back()),
            (Qt.ALT + Qt.Key_Right,       lambda: self._current_tab() and self._current_tab().safe_forward()),
            (Qt.Key_F5,                   lambda: self._current_tab() and self._current_tab().reload()),
            (Qt.Key_Escape,               lambda: self._current_tab() and self._current_tab().stop()),
            (Qt.CTRL + Qt.Key_R,          lambda: self._current_tab() and self._current_tab().reload()),
            (Qt.CTRL + Qt.SHIFT + Qt.Key_T, self._reopen_closed_tab),
        ]
        for key, slot in shortcuts:
            sc = QShortcut(QKeySequence(key), self)
            sc.activated.connect(slot)

        self._closed_tabs: list[str] = []  # stack of recently closed URLs

    # ── Tab management ────────────────────────────────────────────────────

    def add_new_tab(self, url: str = HOME_URL, title: str = "New Tab") -> BrowserTab:
        """Create and activate a new browser tab."""
        tab = BrowserTab(self)
        tab.navigate(url)

        # Connect tab signals
        tab.urlChanged.connect(lambda q, t=tab: self._on_url_changed(q, t))
        tab.titleChanged.connect(lambda title_str, t=tab: self._on_title_changed(title_str, t))
        tab.loadStarted.connect(lambda t=tab: self._on_load_started(t))
        tab.loadProgress.connect(lambda p, t=tab: self._on_load_progress(p, t))
        tab.loadFinished.connect(lambda ok, t=tab: self._on_load_finished(ok, t))
        tab.page().linkHovered.connect(lambda url_str: self._status.showMessage(url_str, 3000))
        tab.new_window_requested.connect(lambda q: self.add_new_tab(q.toString() or HOME_URL, "New Tab"))

        idx = self._tabs.addTab(tab, title)
        self._tabs.setCurrentIndex(idx)
        return tab

    def _close_tab(self, index: int) -> None:
        tab = self._tabs.widget(index)
        if isinstance(tab, BrowserTab):
            self._closed_tabs.append(tab.url().toString())
        if self._tabs.count() <= 1:
            # Keep at least one tab — navigate it home
            if isinstance(tab, BrowserTab):
                tab.navigate(HOME_URL)
            return
        self._tabs.removeTab(index)

    def _reopen_closed_tab(self) -> None:
        if self._closed_tabs:
            self.add_new_tab(self._closed_tabs.pop(), "Restoring...")

    def _current_tab(self) -> Optional[BrowserTab]:
        w = self._tabs.currentWidget()
        return w if isinstance(w, BrowserTab) else None

    # ── Navigation ────────────────────────────────────────────────────────

    def _on_url_navigate(self, url: str) -> None:
        tab = self._current_tab()
        if tab:
            tab.navigate(url)

    def _navigate_home(self) -> None:
        tab = self._current_tab()
        if tab:
            tab.navigate(HOME_URL)

    # ── Signal handlers ───────────────────────────────────────────────────

    def _on_tab_changed(self, index: int) -> None:
        tab = self._current_tab()
        if tab:
            self._url_bar.set_url(tab.url().toString())
            self._update_nav_buttons(tab)
            title = tab.title() or APP_TITLE
            self.setWindowTitle(f"{title} — {APP_TITLE}")

    def _on_url_changed(self, qurl: QUrl, tab: BrowserTab) -> None:
        if tab is self._current_tab():
            url_str = qurl.toString()
            self._url_bar.set_url(url_str)
            self._update_nav_buttons(tab)

    def _on_title_changed(self, title: str, tab: BrowserTab) -> None:
        idx = self._tabs.indexOf(tab)
        if idx != -1:
            short = (title[:22] + "…") if len(title) > 22 else title
            self._tabs.setTabText(idx, short or "Loading…")
        if tab is self._current_tab():
            self.setWindowTitle(f"{title or 'Loading…'} — {APP_TITLE}")

    def _on_load_started(self, tab: BrowserTab) -> None:
        if tab is self._current_tab():
            self._progress.show()
            self._progress.setValue(0)
            self._act_stop.setEnabled(True)
            self._act_reload.setEnabled(False)

    def _on_load_progress(self, progress: int, tab: BrowserTab) -> None:
        if tab is self._current_tab():
            self._progress.setValue(progress)

    def _on_load_finished(self, ok: bool, tab: BrowserTab) -> None:
        if tab is self._current_tab():
            self._progress.hide()
            self._progress.setValue(0)
            self._act_stop.setEnabled(False)
            self._act_reload.setEnabled(True)
            self._update_nav_buttons(tab)
            if not ok:
                self._status.showMessage("Page failed to load.", 4000)

    def _update_nav_buttons(self, tab: BrowserTab) -> None:
        hist = tab.history()
        self._act_back.setEnabled(hist.canGoBack())
        self._act_fwd.setEnabled(hist.canGoForward())

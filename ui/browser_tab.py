"""
ui/browser_tab.py
-----------------
BrowserTab — a self-contained QWebEngineView that:
  - Configures QtWebEngine settings (JS, local storage, etc.)
  - Bridges Qt signals to the MainWindow for title/URL/progress updates
  - Redirects target="_blank" links into new in-app tabs
  - Emits new_window_requested(url) so MainWindow can open a new tab
"""

from PyQt5.QtWebEngineWidgets import (
    QWebEngineView,
    QWebEnginePage,
    QWebEngineSettings,
)
from PyQt5.QtCore import QUrl, pyqtSignal
from PyQt5.QtWidgets import QWidget


class BrowserPage(QWebEnginePage):
    """
    Custom page that intercepts createWindow to route _blank targets
    back to the main window as new tabs instead of spawning OS windows.
    """

    new_window_requested = pyqtSignal(QUrl)

    def createWindow(self, window_type: QWebEnginePage.WebWindowType):  # type: ignore[override]
        """
        Called when a link has target='_blank' or window.open() is used.
        We emit a signal and return None — the MainWindow will create the
        new tab and setUrl() on it.  Returning None prevents Qt from
        spawning a detached window.
        """
        # Emit with an empty URL; the navigation will populate it via
        # the subsequent urlChanged signal from the newly created tab.
        self.new_window_requested.emit(QUrl())
        return None  # suppress default floating window


class BrowserTab(QWebEngineView):
    """
    One browser tab.  Wraps QWebEngineView with a configured page and
    exposes signals the MainWindow can connect to without knowing internals.
    """

    # Re-emitted so MainWindow can track "which tab emitted this"
    new_window_requested = pyqtSignal(QUrl)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._setup_page()
        self._configure_settings()

    # ── Setup ─────────────────────────────────────────────────────────────

    def _setup_page(self) -> None:
        page = BrowserPage(self)
        page.new_window_requested.connect(self.new_window_requested)
        self.setPage(page)

    def _configure_settings(self) -> None:
        s: QWebEngineSettings = self.settings()
        s.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        s.setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        s.setAttribute(QWebEngineSettings.WebGLEnabled, True)
        s.setAttribute(QWebEngineSettings.PluginsEnabled, False)
        s.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        s.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, True)
        s.setAttribute(QWebEngineSettings.ScrollAnimatorEnabled, True)

    # ── Convenience ───────────────────────────────────────────────────────

    def navigate(self, url: str) -> None:
        """Navigate to a URL string (adds https:// if scheme is missing)."""
        if not url.startswith(("http://", "https://", "ftp://", "file://")):
            url = "https://" + url
        self.setUrl(QUrl(url))

    def safe_back(self) -> None:
        if self.history().canGoBack():
            self.back()

    def safe_forward(self) -> None:
        if self.history().canGoForward():
            self.forward()

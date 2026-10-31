"""
ui/url_bar.py
-------------
Smart URL / search bar widget.

Behaviour:
  - If the user presses Enter, resolve_input() decides whether to:
      a) Navigate directly (input looks like a URL: contains '.' and no spaces)
      b) Fire a Google search (everything else)
  - Clicking the bar selects all text for quick replacement.
  - Losing focus leaves the current URL visible but not selected.
"""

from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent


class URLBar(QLineEdit):
    """Custom address bar that emits a resolved URL string on Enter."""

    navigate_requested = pyqtSignal(str)  # emits a full URL string

    SEARCH_ENGINE = "https://www.google.com/search?q={}"
    HOME_URL = "https://www.google.com"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("urlBar")
        self.setPlaceholderText("Search or enter a URL...")
        self.setClearButtonEnabled(True)
        self.returnPressed.connect(self._on_return_pressed)

    # ── Public helpers ────────────────────────────────────────────────────

    def set_url(self, url: str) -> None:
        """Update the bar text; do NOT steal focus."""
        self.setText(url)
        self.setCursorPosition(0)

    def resolve_input(self, text: str) -> str:
        """
        Convert raw user text into a navigable URL string.

        Rules (in order):
          1. Empty → home page.
          2. Already has a scheme (http/https/ftp/file) → use as-is.
          3. Looks like a hostname/URL (has dot, no spaces) → prepend https://.
          4. Localhost or IP address → prepend http://.
          5. Everything else → Google search.
        """
        text = text.strip()
        if not text:
            return self.HOME_URL

        # Already has a recognised scheme
        if any(text.startswith(s) for s in ("http://", "https://", "ftp://", "file://")):
            return text

        # Looks like a URL: contains a dot (or colon for port) and no spaces
        if ("." in text or ":" in text) and " " not in text:
            return "https://" + text

        # Localhost or bare IP
        if text.lower().startswith("localhost") or text[0].isdigit():
            return "http://" + text

        # Fallback: search
        return self.SEARCH_ENGINE.format(text.replace(" ", "+"))

    # ── Qt overrides ──────────────────────────────────────────────────────

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        """Select all text on click so the user can start typing immediately."""
        super().mousePressEvent(event)
        self.selectAll()

    def focusInEvent(self, event) -> None:  # type: ignore[override]
        super().focusInEvent(event)
        self.selectAll()

    # ── Private slots ─────────────────────────────────────────────────────

    def _on_return_pressed(self) -> None:
        url = self.resolve_input(self.text())
        self.setText(url)
        self.setCursorPosition(0)
        self.navigate_requested.emit(url)
        self.clearFocus()

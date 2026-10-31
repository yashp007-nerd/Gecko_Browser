"""
browser.py
----------
NovaBrowser — entry point.

Usage:
    python browser.py

Bootstraps QApplication, loads the dark stylesheet, and launches MainWindow.
"""

import sys
import os

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QCoreApplication
from PyQt5.QtGui import QIcon, QPixmap

# Enable High-DPI scaling before QApplication is created
QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

# Required before importing WebEngine on some Windows configs
os.environ.setdefault("QTWEBENGINE_CHROMIUM_FLAGS", "--disable-gpu-sandbox")

from ui.main_window import MainWindow


def load_stylesheet(app: QApplication) -> None:
    """Read and apply the dark QSS stylesheet."""
    qss_path = os.path.join(os.path.dirname(__file__), "styles", "dark_theme.qss")
    if os.path.exists(qss_path):
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    else:
        print(f"[warn] Stylesheet not found at {qss_path}")


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("NovaBrowser")
    app.setApplicationDisplayName("NovaBrowser")
    app.setOrganizationName("NovaBrowser")

    # Generate a minimal window icon (dark blue circle)
    icon_pixmap = QPixmap(64, 64)
    icon_pixmap.fill(Qt.transparent)
    from PyQt5.QtGui import QPainter, QColor, QBrush, QPen
    painter = QPainter(icon_pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QBrush(QColor("#4d8ef0")))
    painter.setPen(QPen(QColor("#2d6fd4"), 3))
    painter.drawEllipse(4, 4, 56, 56)
    painter.setPen(QPen(QColor("#ffffff"), 3))
    painter.drawLine(32, 18, 32, 46)
    painter.drawLine(18, 32, 46, 32)
    painter.end()
    app.setWindowIcon(QIcon(icon_pixmap))

    load_stylesheet(app)

    window = MainWindow()
    window.show()

    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())

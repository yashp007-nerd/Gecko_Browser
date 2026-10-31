@echo off
echo [Browser Installer] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo [Browser Installer] Installing PyQt5 and PyQtWebEngine...
python -m pip install PyQt5==5.15.11 PyQtWebEngine==5.15.7 --quiet
echo [OK] All dependencies installed successfully.
pause

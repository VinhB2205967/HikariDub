"""
Hikari Tsukimi v3.0 — AI Dubbing & Creative Studio (Clean MVVM Qt6 / PySide6 Entrypoint).
Supports High-DPI 100%-200% scaling, unified QSS theme, and state-machine worker pipeline.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
for _k in list(sys.modules.keys()):
    if _k == "app" or _k.startswith("app."):
        del sys.modules[_k]
sys.path.insert(0, BASE_DIR)

from app.qt_compat import QApplication, Qt
from app.theme import build_stylesheet
from services.settings_service import SettingsService
from ui.main_window import StudioMainWindow


def main():
    os.environ["PYTHONIOENCODING"] = "utf-8"
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("Hikari Tsukimi Studio v3.0")
    app.setStyleSheet(build_stylesheet())

    settings = SettingsService(BASE_DIR)
    win = StudioMainWindow(settings)
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

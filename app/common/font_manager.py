"""
Font Manager for Hikari Tsukimi Studio.
Loads any custom .ttf/.otf fonts from assets/fonts or fonts/ if present.
"""

import os
from PyQt6.QtGui import QFontDatabase


def load_custom_fonts() -> list:
    """Load custom font files from local fonts directories if available."""
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    loaded = []
    for folder in [os.path.join(root, "fonts"), os.path.join(root, "assets", "fonts")]:
        if not os.path.isdir(folder):
            continue
        for fname in os.listdir(folder):
            if fname.lower().endswith((".ttf", ".otf")):
                fpath = os.path.join(folder, fname)
                fid = QFontDatabase.addApplicationFont(fpath)
                if fid != -1:
                    loaded.extend(QFontDatabase.applicationFontFamilies(fid))
    return loaded

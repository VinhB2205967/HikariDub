"""
Design System Tokens & Unified QSS Stylesheet for Hikari Tsukimi v3.0 (Qt6 / PySide6).
No hardcoded colors in UI views — all styling flows through Tokens and build_stylesheet().
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Tokens:
    # Surfaces & Borders
    BG_BASE: str = "#0F1117"
    BG_CARD: str = "#171A23"
    BG_ELEVATED: str = "#1E2230"
    BG_INPUT: str = "#12151E"
    BORDER: str = "#262B38"
    BORDER_FOCUS: str = "#7C5CFF"

    # Typography Colors
    TEXT_PRIMARY: str = "#E6E8EE"
    TEXT_SECONDARY: str = "#8B93A7"
    TEXT_MUTED: str = "#5E667A"

    # Brand & Semantic Accents
    PRIMARY_START: str = "#7C5CFF"
    PRIMARY_END: str = "#4F8CFF"
    SUCCESS: str = "#2ECC71"
    WARNING: str = "#F5A524"
    ERROR: str = "#FF5C5C"

    # Typography Sizes
    FONT_FAMILY: str = '"Inter", "Segoe UI", system-ui, sans-serif'
    SIZE_BODY: int = 13
    SIZE_SUB: int = 12
    SIZE_CARD_TITLE: int = 16
    SIZE_PAGE_TITLE: int = 20

    # Spacing & Radius (8px grid)
    RADIUS_MD: int = 10
    RADIUS_LG: int = 12


TOKENS = Tokens()


def build_stylesheet(t: Tokens = TOKENS) -> str:
    return f"""
    QWidget {{
        background-color: {t.BG_BASE};
        color: {t.TEXT_PRIMARY};
        font-family: {t.FONT_FAMILY};
        font-size: {t.SIZE_BODY}px;
    }}
    QMainWindow, QDialog {{
        background-color: {t.BG_BASE};
    }}
    QFrame#TopBar, QFrame#BottomBar, QFrame#SideRail {{
        background-color: {t.BG_CARD};
        border: 1px solid {t.BORDER};
    }}
    QFrame#Card {{
        background-color: {t.BG_CARD};
        border: 1px solid {t.BORDER};
        border-radius: {t.RADIUS_LG}px;
    }}
    QFrame#Card:hover {{
        border-color: #343B4E;
    }}
    QLabel#PageTitle {{
        font-size: {t.SIZE_PAGE_TITLE}px;
        font-weight: 700;
        color: {t.TEXT_PRIMARY};
        background: transparent;
    }}
    QLabel#CardTitle {{
        font-size: {t.SIZE_CARD_TITLE}px;
        font-weight: 700;
        color: {t.TEXT_PRIMARY};
        background: transparent;
    }}
    QLabel#SubLabel {{
        font-size: {t.SIZE_SUB}px;
        color: {t.TEXT_SECONDARY};
        background: transparent;
    }}
    QPushButton#PrimaryButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {t.PRIMARY_START}, stop:1 {t.PRIMARY_END});
        color: #FFFFFF;
        font-weight: 700;
        font-size: {t.SIZE_BODY}px;
        border: none;
        border-radius: {t.RADIUS_MD}px;
        padding: 8px 16px;
        min-height: 20px;
    }}
    QPushButton#PrimaryButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #8D70FF, stop:1 #639BFF);
    }}
    QPushButton#PrimaryButton:pressed {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #6848E8, stop:1 #3D78E8);
    }}
    QPushButton#PrimaryButton:disabled {{
        background: {t.BG_ELEVATED};
        color: {t.TEXT_MUTED};
    }}
    QPushButton#SecondaryButton {{
        background-color: {t.BG_ELEVATED};
        color: {t.TEXT_PRIMARY};
        font-weight: 600;
        border: 1px solid {t.BORDER};
        border-radius: {t.RADIUS_MD}px;
        padding: 7px 14px;
    }}
    QPushButton#SecondaryButton:hover {{
        border-color: {t.PRIMARY_END};
        background-color: #252A3A;
    }}
    QPushButton#SecondaryButton:disabled {{
        color: {t.TEXT_MUTED};
        border-color: #1C202B;
    }}
    QPushButton#DangerButton {{
        background-color: rgba(255, 92, 92, 0.14);
        color: {t.ERROR};
        font-weight: 700;
        border: 1px solid rgba(255, 92, 92, 0.45);
        border-radius: {t.RADIUS_MD}px;
        padding: 7px 14px;
    }}
    QPushButton#DangerButton:hover {{
        background-color: rgba(255, 92, 92, 0.25);
    }}
    QPushButton#DangerButton:disabled {{
        background-color: {t.BG_ELEVATED};
        color: {t.TEXT_MUTED};
        border-color: {t.BORDER};
    }}
    QPushButton#GhostButton, QToolButton#IconButton {{
        background-color: transparent;
        color: {t.TEXT_SECONDARY};
        border: 1px solid transparent;
        border-radius: 8px;
        padding: 6px 10px;
    }}
    QPushButton#GhostButton:hover, QToolButton#IconButton:hover {{
        background-color: {t.BG_ELEVATED};
        color: {t.TEXT_PRIMARY};
        border-color: {t.BORDER};
    }}
    QPushButton#GhostButton:checked, QToolButton#IconButton:checked {{
        background-color: rgba(124, 92, 255, 0.18);
        color: {t.TEXT_PRIMARY};
        border-color: {t.PRIMARY_START};
    }}
    QLineEdit, QPlainTextEdit, QComboBox {{
        background-color: {t.BG_INPUT};
        color: {t.TEXT_PRIMARY};
        border: 1px solid {t.BORDER};
        border-radius: {t.RADIUS_MD}px;
        padding: 6px 10px;
        selection-background-color: {t.PRIMARY_START};
    }}
    QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{
        border-color: {t.BORDER_FOCUS};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
    }}
    QSlider::groove:horizontal {{
        height: 6px;
        background: {t.BG_INPUT};
        border-radius: 3px;
    }}
    QSlider::sub-page:horizontal {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {t.PRIMARY_START}, stop:1 {t.PRIMARY_END});
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        background: #FFFFFF;
        border: 2px solid {t.PRIMARY_START};
        width: 14px;
        height: 14px;
        margin: -5px 0;
        border-radius: 7px;
    }}
    QProgressBar {{
        background-color: {t.BG_INPUT};
        border: 1px solid {t.BORDER};
        border-radius: 6px;
        text-align: center;
        color: {t.TEXT_PRIMARY};
        font-size: 11px;
        font-weight: 700;
        max-height: 14px;
    }}
    QProgressBar::chunk {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {t.PRIMARY_START}, stop:1 {t.PRIMARY_END});
        border-radius: 5px;
    }}
    QTableWidget {{
        background-color: {t.BG_INPUT};
        alternate-background-color: {t.BG_CARD};
        color: {t.TEXT_PRIMARY};
        gridline-color: {t.BORDER};
        border: 1px solid {t.BORDER};
        border-radius: {t.RADIUS_MD}px;
    }}
    QHeaderView::section {{
        background-color: {t.BG_ELEVATED};
        color: {t.TEXT_SECONDARY};
        font-weight: 700;
        font-size: {t.SIZE_SUB}px;
        border: none;
        border-bottom: 1px solid {t.BORDER};
        padding: 6px 8px;
    }}
    QSplitter::handle {{
        background-color: {t.BORDER};
        width: 2px;
    }}
    QSplitter::handle:hover {{
        background-color: {t.PRIMARY_START};
    }}
    QScrollBar:vertical {{
        background: transparent;
        width: 8px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: #2C3344;
        min-height: 24px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: #3E485F;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    """

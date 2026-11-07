"""
Hikari Tsukimi — Modern SaaS Design System & Theme Engine
Style Direction: Modern SaaS • Premium UI • Creative Technology
Inspired by Linear, Stripe, Framer, and Raycast.

Color Palette:
- Primary:        Electric Blue (#6366F1)
- Secondary:      Violet        (#8B5CF6)
- Accent:         Cyan          (#06B6D4)
- Highlight:      Pink          (#EC4899)
- Background:     Dark Navy     (#0B1020)
- Surface:        Deep Slate    (#151B2E)
- Text Primary:    Crisp White   (#F8FAFC)
- Text Secondary: Muted Slate   (#94A3B8)
"""

from __future__ import annotations
import os
import time
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import (
    QColor, QPalette, QPainter, QPen, QBrush,
    QLinearGradient, QRadialGradient, QPainterPath, QFont
)
from PyQt6.QtWidgets import QApplication, QWidget


class Colors:
    """Core semantic color tokens for the Modern SaaS Design System."""
    PRIMARY          = "#6366F1"   # Electric Blue
    PRIMARY_HOVER    = "#818CF8"   # Lighter Electric Blue
    PRIMARY_PRESSED  = "#4F46E5"   # Deep Indigo
    SECONDARY        = "#8B5CF6"   # Violet
    SECONDARY_HOVER  = "#A78BFA"   # Soft Violet
    ACCENT           = "#06B6D4"   # Cyan
    ACCENT_BRIGHT    = "#22D3EE"   # Bright Cyan
    HIGHLIGHT        = "#EC4899"   # Pink
    HIGHLIGHT_HOVER  = "#F472B6"   # Soft Pink

    BG_DARK          = "#0B1020"   # Dark Navy (Main Background)
    BG_DEEP          = "#070B16"   # Deep Input / Console Base
    BG_SIDEBAR       = "#090E1C"   # Sidebar Navigation Background
    SURFACE          = "#151B2E"   # Primary Card / Panel Surface
    SURFACE_ALT      = "#1A2238"   # Elevated / Secondary Surface
    SURFACE_HOVER    = "#1F2943"   # Hover Surface State
    SURFACE_PRESSED  = "#111728"   # Active / Pressed Surface State

    BORDER           = "#242F4B"   # Standard Crisp Card Border
    BORDER_SUBTLE    = "#1C253C"   # Subtle Divider Border
    BORDER_HOVER     = "#6366F1"   # Electric Blue Hover Border
    BORDER_ACCENT    = "#06B6D4"   # Cyan Focus / Accent Border

    TEXT_PRIMARY     = "#F8FAFC"   # High-contrast Primary Text
    TEXT_SECONDARY   = "#94A3B8"   # Balanced Secondary Text
    TEXT_MUTED       = "#64748B"   # Muted / Disabled / Caption Text

    SUCCESS          = "#10B981"   # Emerald Success
    WARNING          = "#F59E0B"   # Amber Warning
    DANGER           = "#EF4444"   # Rose Danger


class Gradients:
    """QSS Gradient strings following the Modern SaaS specification."""
    # 1. Blue -> Purple (Primary CTA & Active Controls)
    BLUE_PURPLE = (
        "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
        "stop:0 #6366F1, stop:1 #8B5CF6)"
    )
    BLUE_PURPLE_HOVER = (
        "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
        "stop:0 #818CF8, stop:0.5 #8B5CF6, stop:1 #A855F7)"
    )
    BLUE_PURPLE_PRESSED = (
        "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
        "stop:0 #4F46E5, stop:1 #7C3AED)"
    )

    # 2. Purple -> Pink (Creative Highlights & Badges)
    PURPLE_PINK = (
        "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
        "stop:0 #8B5CF6, stop:1 #EC4899)"
    )
    PURPLE_PINK_HOVER = (
        "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
        "stop:0 #A78BFA, stop:1 #F472B6)"
    )

    # 3. Cyan -> Blue (Technical Accents & Secondary Actions)
    CYAN_BLUE = (
        "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
        "stop:0 #06B6D4, stop:1 #6366F1)"
    )
    CYAN_BLUE_HOVER = (
        "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
        "stop:0 #22D3EE, stop:1 #818CF8)"
    )

    # 4. Indigo -> Violet -> Pink (Hero Action & Brand Signature)
    INDIGO_VIOLET_PINK = (
        "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
        "stop:0 #6366F1, stop:0.5 #8B5CF6, stop:1 #EC4899)"
    )
    INDIGO_VIOLET_PINK_HOVER = (
        "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
        "stop:0 #818CF8, stop:0.5 #A78BFA, stop:1 #F472B6)"
    )
    INDIGO_VIOLET_PINK_PRESSED = (
        "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
        "stop:0 #4F46E5, stop:0.5 #7C3AED, stop:1 #DB2777)"
    )

    # 5. Danger Rose -> Pink
    DANGER_GRAD = (
        "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
        "stop:0 #EF4444, stop:1 #EC4899)"
    )
    DANGER_GRAD_HOVER = (
        "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
        "stop:0 #F87171, stop:1 #F472B6)"
    )

    # 6. Glassmorphic Surface Gradients
    CARD_SURFACE = (
        "qlineargradient(x1:0, y1:0, x2:0, y2:1, "
        "stop:0 #171F34, stop:1 #13192B)"
    )
    CARD_SURFACE_HOVER = (
        "qlineargradient(x1:0, y1:0, x2:0, y2:1, "
        "stop:0 #1D2640, stop:1 #161E33)"
    )
    HEADER_SURFACE = (
        "qlineargradient(x1:0, y1:0, x2:1, y2:0, "
        "stop:0 #0E1528, stop:0.5 #131B31, stop:1 #0E1528)"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Custom QSS overrides injected into QFluentWidgets' FluentStyleSheet engine
# ─────────────────────────────────────────────────────────────────────────────

QFW_BUTTON_OVERRIDE_QSS = f"""
/* ── Modern SaaS Secondary / Standard Buttons ── */
PushButton, ToolButton, ToggleButton, ToggleToolButton {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1C243B, stop:1 #151B2E);
    border: 1px solid {Colors.BORDER};
    border-top: 1px solid #2E3C5E;
    border-radius: 8px;
    color: {Colors.TEXT_PRIMARY};
    font-weight: 600;
    outline: none;
}}

PushButton:hover, ToolButton:hover, ToggleButton:hover, ToggleToolButton:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #212B46, stop:1 #25224B);
    border: 1px solid {Colors.PRIMARY};
    color: {Colors.TEXT_PRIMARY};
}}

PushButton:pressed, ToolButton:pressed, ToggleButton:pressed, ToggleToolButton:pressed {{
    background: {Colors.SURFACE_PRESSED};
    border: 1px solid {Colors.ACCENT};
    color: {Colors.TEXT_SECONDARY};
}}

PushButton:focus, ToolButton:focus {{
    border: 1px solid {Colors.ACCENT};
}}

PushButton:disabled, ToolButton:disabled, ToggleButton:disabled, ToggleToolButton:disabled {{
    background: #101524;
    border: 1px solid #1A2236;
    color: #475569;
}}

/* ── Modern SaaS Primary Action Buttons (Blue -> Purple Gradient) ── */
PrimaryPushButton,
PrimaryToolButton,
ToggleButton:checked,
ToggleToolButton:checked {{
    background: {Gradients.BLUE_PURPLE};
    border: 1px solid #818CF8;
    border-bottom: 1px solid #6366F1;
    border-radius: 8px;
    color: {Colors.TEXT_PRIMARY};
    font-weight: 700;
}}

PrimaryPushButton:hover,
PrimaryToolButton:hover,
ToggleButton:checked:hover,
ToggleToolButton:checked:hover {{
    background: {Gradients.INDIGO_VIOLET_PINK_HOVER};
    border: 1px solid #C4B5FD;
    color: #FFFFFF;
}}

PrimaryPushButton:pressed,
PrimaryToolButton:pressed,
ToggleButton:checked:pressed,
ToggleToolButton:checked:pressed {{
    background: {Gradients.BLUE_PURPLE_PRESSED};
    border: 1px solid {Colors.PRIMARY};
    color: #E2E8F0;
}}

PrimaryPushButton:disabled,
PrimaryToolButton:disabled,
ToggleButton:checked:disabled,
ToggleToolButton:checked:disabled {{
    background: #161D30;
    border: 1px solid #222C46;
    color: #475569;
}}

/* ── RadioButton with Electric Blue / Cyan Indicator ── */
RadioButton {{
    color: {Colors.TEXT_PRIMARY};
    font-weight: 500;
}}
RadioButton:hover {{
    color: #FFFFFF;
}}
RadioButton::indicator {{
    border: 2px solid #475569;
    background-color: {Colors.BG_DEEP};
}}
RadioButton::indicator:hover {{
    border: 2px solid {Colors.PRIMARY};
    background-color: rgba(99, 102, 241, 0.15);
}}
RadioButton::indicator:checked {{
    background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
        stop:0 {Colors.BG_DARK},
        stop:0.45 {Colors.BG_DARK},
        stop:0.55 {Colors.PRIMARY},
        stop:1 {Colors.ACCENT});
}}

/* ── Transparent Tool Buttons ── */
TransparentToolButton, TransparentPushButton {{
    border-radius: 7px;
    color: {Colors.TEXT_SECONDARY};
}}
TransparentToolButton:hover, TransparentPushButton:hover {{
    background-color: rgba(99, 102, 241, 0.16);
    color: {Colors.TEXT_PRIMARY};
}}
"""

QFW_LINE_EDIT_OVERRIDE_QSS = f"""
LineEdit, TextEdit, PlainTextEdit, TextBrowser {{
    background-color: {Colors.BG_DEEP};
    border: 1px solid {Colors.BORDER};
    border-bottom: 1px solid #334155;
    border-radius: 8px;
    color: {Colors.TEXT_PRIMARY};
    selection-background-color: {Colors.PRIMARY};
    selection-color: #FFFFFF;
}}

LineEdit:hover, TextEdit:hover, PlainTextEdit:hover, TextBrowser:hover {{
    background-color: #0A1020;
    border: 1px solid #3B4C73;
    border-bottom: 1px solid {Colors.PRIMARY};
}}

LineEdit:focus, LineEdit[transparent=false]:focus, LineEdit:focus[transparent=true],
TextEdit:focus, PlainTextEdit:focus, TextBrowser:focus {{
    background-color: #080D1A;
    border: 1px solid {Colors.PRIMARY};
    border-bottom: 2px solid {Colors.ACCENT};
}}

LineEdit:disabled, TextEdit:disabled, PlainTextEdit:disabled, TextBrowser:disabled {{
    background-color: #090D18;
    border: 1px solid #1A2236;
    color: #475569;
}}
"""

QFW_COMBO_BOX_OVERRIDE_QSS = f"""
ComboBox, ModelComboBox {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #182036, stop:1 #111728);
    border: 1px solid {Colors.BORDER};
    border-top: 1px solid #2E3C5E;
    border-radius: 8px;
    color: {Colors.TEXT_PRIMARY};
    font-weight: 500;
}}

ComboBox:hover, ModelComboBox:hover {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1F2943, stop:1 #161E33);
    border: 1px solid {Colors.PRIMARY};
}}

ComboBox:pressed, ModelComboBox:pressed, ComboBox:focus, ModelComboBox:focus {{
    background: {Colors.BG_DEEP};
    border: 1px solid {Colors.ACCENT};
}}

ComboBox:disabled, ModelComboBox:disabled {{
    background: #0F1422;
    border: 1px solid #1C253C;
    color: #475569;
}}
"""

QFW_SPIN_BOX_OVERRIDE_QSS = f"""
SpinBox, DoubleSpinBox, CompactSpinBox, CompactDoubleSpinBox {{
    background-color: {Colors.BG_DEEP};
    border: 1px solid {Colors.BORDER};
    border-radius: 8px;
    color: {Colors.TEXT_PRIMARY};
    font-weight: 600;
    selection-background-color: {Colors.PRIMARY};
    selection-color: #FFFFFF;
}}
SpinBox:hover, DoubleSpinBox:hover {{
    background-color: #0B1122;
    border: 1px solid {Colors.PRIMARY};
}}
SpinBox:focus, DoubleSpinBox:focus {{
    background-color: #080D1A;
    border: 1px solid {Colors.ACCENT};
}}
"""

QFW_PIVOT_OVERRIDE_QSS = f"""
SegmentedWidget {{
    background-color: #0D1324;
    border: 1px solid {Colors.BORDER};
    border-radius: 9px;
    padding: 2px;
}}
PivotItem, SegmentedItem {{
    color: {Colors.TEXT_SECONDARY};
    font-weight: 600;
    border-radius: 7px;
}}
PivotItem:hover, SegmentedItem:hover {{
    color: {Colors.TEXT_PRIMARY};
    background-color: rgba(99, 102, 241, 0.10);
}}
PivotItem[isSelected=true], SegmentedItem[isSelected=true] {{
    color: #FFFFFF;
    font-weight: 700;
}}
"""

QFW_CHECK_BOX_OVERRIDE_QSS = f"""
CheckBox {{
    color: {Colors.TEXT_PRIMARY};
    font-weight: 500;
}}
CheckBox:hover {{
    color: #FFFFFF;
}}
"""

QFW_SWITCH_OVERRIDE_QSS = f"""
SwitchButton {{
    color: {Colors.TEXT_PRIMARY};
}}
"""

QFW_TABLE_LIST_OVERRIDE_QSS = f"""
QTableView, QListView, QListWidget, TableWidget, ListWidget {{
    background-color: {Colors.BG_DEEP};
    border: 1px solid {Colors.BORDER};
    border-radius: 10px;
    color: {Colors.TEXT_PRIMARY};
    gridline-color: {Colors.BORDER_SUBTLE};
    selection-background-color: rgba(99, 102, 241, 0.25);
    selection-color: #FFFFFF;
    outline: none;
}}
QHeaderView::section {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1A2238, stop:1 #13192B);
    color: {Colors.ACCENT_BRIGHT};
    font-weight: 700;
    border: none;
    border-bottom: 1px solid {Colors.BORDER};
    border-right: 1px solid {Colors.BORDER_SUBTLE};
    padding: 8px 12px;
}}
QTableView::item, QListView::item {{
    border-radius: 6px;
    padding: 4px 8px;
}}
QTableView::item:hover, QListView::item:hover {{
    background-color: rgba(99, 102, 241, 0.14);
}}
QTableView::item:selected, QListView::item:selected {{
    background-color: rgba(99, 102, 241, 0.28);
    color: #FFFFFF;
}}
"""

QFW_MENU_OVERRIDE_QSS = f"""
RoundMenu, MenuActionListWidget {{
    background-color: {Colors.SURFACE};
    border: 1px solid {Colors.BORDER};
    border-radius: 10px;
    color: {Colors.TEXT_PRIMARY};
}}
MenuActionListWidget::item {{
    color: {Colors.TEXT_PRIMARY};
    border-radius: 6px;
    padding: 6px 12px;
}}
MenuActionListWidget::item:hover, MenuActionListWidget::item:selected {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(99, 102, 241, 0.30), stop:1 rgba(139, 92, 246, 0.25));
    color: #FFFFFF;
}}
"""

QFW_NAVIGATION_OVERRIDE_QSS = f"""
NavigationInterface, NavigationPanel {{
    background-color: {Colors.BG_SIDEBAR};
    border-right: 1px solid {Colors.BORDER};
}}
"""

QFW_LABEL_OVERRIDE_QSS = f"""
FluentLabelBase {{
    color: {Colors.TEXT_PRIMARY};
}}
CaptionLabel {{
    color: {Colors.TEXT_SECONDARY};
}}
HyperlinkLabel {{
    color: {Colors.ACCENT_BRIGHT};
}}
HyperlinkLabel:hover {{
    color: {Colors.PRIMARY_HOVER};
}}
"""

QFW_DIALOG_OVERRIDE_QSS = f"""
QDialog, MessageBox, MessageBoxBase, MaskDialogBase {{
    background-color: {Colors.SURFACE};
    color: {Colors.TEXT_PRIMARY};
}}
#centerWidget {{
    background-color: {Colors.SURFACE};
    border: 1px solid {Colors.PRIMARY};
    border-radius: 14px;
}}
#buttonGroup {{
    background-color: {Colors.BG_DARK};
    border-top: 1px solid {Colors.BORDER};
    border-bottom-left-radius: 14px;
    border-bottom-right-radius: 14px;
}}
"""

QFW_INFO_BAR_OVERRIDE_QSS = f"""
InfoBar {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #161F36, stop:1 #1B243E);
    border: 1px solid {Colors.PRIMARY};
    border-radius: 10px;
}}
"""


def get_global_app_stylesheet() -> str:
    """Returns the master QApplication stylesheet for standard Qt widgets & containers."""
    return f"""
        QWidget {{
            font-family: 'Segoe UI Variable Text', 'Segoe UI Variable Display', 'Inter', 'Segoe UI', sans-serif;
            color: {Colors.TEXT_PRIMARY};
        }}

        /* ── Main Window & Scroll Areas ── */
        FluentWindow, StackedWidget {{
            background-color: {Colors.BG_DARK};
        }}
        QScrollArea {{
            background: transparent;
            border: none;
        }}

        /* ── Standard QComboBox & QSpinBox (e.g., CanvasControlsWidget) ── */
        QComboBox {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1A233A, stop:1 #13192B);
            border: 1px solid {Colors.BORDER};
            border-radius: 7px;
            color: {Colors.TEXT_PRIMARY};
            font-weight: 600;
            padding: 3px 10px;
        }}
        QComboBox:hover {{
            border: 1px solid {Colors.PRIMARY};
            background: #1E2842;
        }}
        QComboBox:focus {{
            border: 1px solid {Colors.ACCENT};
        }}
        QComboBox QAbstractItemView {{
            background-color: {Colors.SURFACE};
            border: 1px solid {Colors.PRIMARY};
            border-radius: 8px;
            color: {Colors.TEXT_PRIMARY};
            selection-background-color: {Colors.PRIMARY};
            selection-color: #FFFFFF;
            padding: 4px;
        }}

        /* ── Smooth Minimalist ScrollBars ── */
        QScrollBar:vertical {{
            background: rgba(11, 16, 32, 0.5);
            width: 7px;
            border-radius: 3px;
            margin: 2px 1px;
        }}
        QScrollBar::handle:vertical {{
            background: #283554;
            border-radius: 3px;
            min-height: 28px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {Colors.PRIMARY}, stop:1 {Colors.ACCENT});
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}

        QScrollBar:horizontal {{
            background: rgba(11, 16, 32, 0.5);
            height: 7px;
            border-radius: 3px;
            margin: 1px 2px;
        }}
        QScrollBar::handle:horizontal {{
            background: #283554;
            border-radius: 3px;
            min-width: 28px;
        }}
        QScrollBar::handle:horizontal:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {Colors.PRIMARY}, stop:1 {Colors.ACCENT});
        }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
            background: none;
        }}

        /* ── Modern Glass Tooltip ── */
        QToolTip {{
            background-color: #131A2E;
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.PRIMARY};
            border-radius: 8px;
            padding: 6px 10px;
            font-size: 12px;
            font-weight: 500;
        }}

        /* ── StatusBar ── */
        QStatusBar {{
            background-color: {Colors.BG_DARK};
            color: {Colors.TEXT_SECONDARY};
            border-top: 1px solid {Colors.BORDER};
        }}
    """


# ─────────────────────────────────────────────────────────────────────────────
# Custom Painter Patches for QFluentWidgets Components
# ─────────────────────────────────────────────────────────────────────────────

def _patch_qfluentwidgets_engine():
    """
    Hooks into QFluentWidgets' style and painting pipeline so that all cards,
    progress bars, segmented tabs, navigation items, and controls render with
    the Modern SaaS gradient & glassmorphic aesthetic.
    """
    try:
        from qfluentwidgets.common.style_sheet import FluentStyleSheet, Theme

        if not getattr(FluentStyleSheet, "_hikari_saas_patched", False):
            _orig_content = FluentStyleSheet.content

            _override_map = {
                "BUTTON": QFW_BUTTON_OVERRIDE_QSS,
                "LINE_EDIT": QFW_LINE_EDIT_OVERRIDE_QSS,
                "COMBO_BOX": QFW_COMBO_BOX_OVERRIDE_QSS,
                "SPIN_BOX": QFW_SPIN_BOX_OVERRIDE_QSS,
                "PIVOT": QFW_PIVOT_OVERRIDE_QSS,
                "CHECK_BOX": QFW_CHECK_BOX_OVERRIDE_QSS,
                "SWITCH_BUTTON": QFW_SWITCH_OVERRIDE_QSS,
                "TABLE_VIEW": QFW_TABLE_LIST_OVERRIDE_QSS,
                "LIST_VIEW": QFW_TABLE_LIST_OVERRIDE_QSS,
                "MENU": QFW_MENU_OVERRIDE_QSS,
                "NAVIGATION_INTERFACE": QFW_NAVIGATION_OVERRIDE_QSS,
                "LABEL": QFW_LABEL_OVERRIDE_QSS,
                "DIALOG": QFW_DIALOG_OVERRIDE_QSS,
                "MESSAGE_DIALOG": QFW_DIALOG_OVERRIDE_QSS,
                "INFO_BAR": QFW_INFO_BAR_OVERRIDE_QSS,
            }

            def _patched_content(self, theme=Theme.AUTO):
                base_qss = _orig_content(self, theme)
                extra = _override_map.get(self.name, "")
                if extra:
                    return base_qss + "\n" + extra
                return base_qss

            FluentStyleSheet.content = _patched_content
            FluentStyleSheet._hikari_saas_patched = True
    except Exception as e:
        print(f"[DesignSystem] FluentStyleSheet patch warning: {e}")

    # 2. Patch CardWidget & SimpleCardWidget paintEvent for Glassmorphic Depth & Hover Border Glow
    try:
        from qfluentwidgets.components.widgets.card_widget import CardWidget, SimpleCardWidget

        if not getattr(CardWidget, "_hikari_card_patched", False):
            _orig_card_init = CardWidget.__init__

            def _patched_card_init(self, parent=None):
                _orig_card_init(self, parent)
                self._borderRadius = 12
                self._hikari_hover_prog = 0.0

            def _patched_card_paint(self, e):
                p = QPainter(self)
                p.setRenderHint(QPainter.RenderHint.Antialiasing)

                w, h = float(self.width()), float(self.height())
                if w <= 2 or h <= 2:
                    p.end()
                    return

                r = float(getattr(self, "_borderRadius", 12))
                rect = QRectF(1.0, 1.0, w - 2.0, h - 2.0)

                path = QPainterPath()
                path.addRoundedRect(rect, r, r)

                # Determine hover progress (from animation filter or boolean isHover)
                hover_t = float(getattr(self, "_hikari_hover_prog", 1.0 if getattr(self, "isHover", False) else 0.0))
                obj_name = self.objectName()

                # Surface gradient with subtle elevation on hover
                surf_grad = QLinearGradient(0, 0, 0, h)
                if obj_name == "hikariRunGroup":
                    # Featured Action Card: Rich Indigo/Violet tinted surface
                    surf_grad.setColorAt(0.0, QColor(30, 39, 68, 245))
                    surf_grad.setColorAt(1.0, QColor(20, 26, 46, 245))
                elif obj_name == "hikariRow2":
                    # Log & Progress Console Card
                    surf_grad.setColorAt(0.0, QColor(16, 22, 38, 250))
                    surf_grad.setColorAt(1.0, QColor(11, 16, 30, 250))
                else:
                    top_c = _lerp_color(QColor("#171F35"), QColor("#1D2742"), hover_t)
                    bot_c = _lerp_color(QColor("#12182A"), QColor("#161E34"), hover_t)
                    surf_grad.setColorAt(0.0, top_c)
                    surf_grad.setColorAt(1.0, bot_c)

                p.fillPath(path, QBrush(surf_grad))

                # Subtle top glass specular highlight line
                p.save()
                p.setClipPath(path)
                spec_grad = QLinearGradient(0, 0, w, 0)
                spec_grad.setColorAt(0.0, QColor(255, 255, 255, 0))
                spec_grad.setColorAt(0.25, QColor(255, 255, 255, int(18 + 16 * hover_t)))
                spec_grad.setColorAt(0.75, QColor(99, 102, 241, int(20 + 30 * hover_t)))
                spec_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
                p.setPen(QPen(QBrush(spec_grad), 1.2))
                p.drawLine(QPointF(r, 1.5), QPointF(w - r, 1.5))
                p.restore()

                # Crisp border: transitions from #242F4B to Gradient (Electric Blue -> Violet -> Cyan) on hover
                if obj_name == "hikariRunGroup" or hover_t > 0.02:
                    b_grad = QLinearGradient(0, 0, w, h)
                    alpha = int(95 + 145 * (hover_t if obj_name != "hikariRunGroup" else max(0.45, hover_t)))
                    b_grad.setColorAt(0.0, QColor(99, 102, 241, alpha))    # Electric Blue #6366F1
                    b_grad.setColorAt(0.5, QColor(139, 92, 246, alpha))    # Violet #8B5CF6
                    b_grad.setColorAt(1.0, QColor(6, 182, 212, alpha))     # Cyan #06B6D4
                    p.setPen(QPen(QBrush(b_grad), 1.2))
                else:
                    p.setPen(QPen(QColor(Colors.BORDER), 1.0))

                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawRoundedRect(rect, r, r)
                p.end()

            CardWidget.__init__ = _patched_card_init
            CardWidget.paintEvent = _patched_card_paint
            SimpleCardWidget.paintEvent = _patched_card_paint
            CardWidget._hikari_card_patched = True
    except Exception as e:
        print(f"[DesignSystem] CardWidget patch warning: {e}")

    # 3. Patch ProgressBar paintEvent for Gradient Bar + Animated Shimmer
    try:
        from qfluentwidgets.components.widgets.progress_bar import ProgressBar

        if not getattr(ProgressBar, "_hikari_pb_patched", False):
            def _patched_pb_paint(self, e):
                p = QPainter(self)
                p.setRenderHint(QPainter.RenderHint.Antialiasing)

                w, h = float(self.width()), float(self.height())
                track_h = min(max(6.0, h), 10.0)
                y_off = (h - track_h) / 2.0
                r = track_h / 2.0

                # 1. Draw dark navy track with subtle border
                track_rect = QRectF(0.5, y_off, w - 1.0, track_h)
                p.setPen(QPen(QColor("#242F4B"), 1.0))
                p.setBrush(QColor("#090E1C"))
                p.drawRoundedRect(track_rect, r, r)

                # 2. Calculate progress ratio (support both setValue() and animated _val)
                mn, mx = self.minimum(), self.maximum()
                span = mx - mn
                raw_v = float(self.value())
                ani_v = float(getattr(self, "_val", 0.0))
                val = max(raw_v, ani_v) if raw_v > 0 else ani_v
                ratio = max(0.0, min(1.0, (val - mn) / span)) if span > 0 else 0.0

                if ratio > 0.005:
                    fill_w = max(track_h, (w - 1.0) * ratio)
                    fill_rect = QRectF(0.5, y_off, fill_w, track_h)

                    grad = QLinearGradient(0, 0, w, 0)
                    grad.setColorAt(0.0, QColor(Colors.ACCENT))       # Cyan #06B6D4
                    grad.setColorAt(0.4, QColor(Colors.PRIMARY))      # Electric Blue #6366F1
                    grad.setColorAt(0.75, QColor(Colors.SECONDARY))   # Violet #8B5CF6
                    grad.setColorAt(1.0, QColor(Colors.HIGHLIGHT))    # Pink #EC4899

                    p.setPen(Qt.PenStyle.NoPen)
                    p.setBrush(QBrush(grad))
                    p.drawRoundedRect(fill_rect, r, r)

                    # Subtle traveling shimmer when processing (0 < ratio < 1)
                    if 0.01 < ratio < 0.995:
                        phase = (time.monotonic() * 0.85) % 1.0
                        shim_x = fill_w * phase
                        shim_grad = QLinearGradient(shim_x - 40, 0, shim_x + 40, 0)
                        shim_grad.setColorAt(0.0, QColor(255, 255, 255, 0))
                        shim_grad.setColorAt(0.5, QColor(255, 255, 255, 90))
                        shim_grad.setColorAt(1.0, QColor(255, 255, 255, 0))
                        p.setBrush(QBrush(shim_grad))
                        p.drawRoundedRect(fill_rect, r, r)

                p.end()

            ProgressBar.paintEvent = _patched_pb_paint
            ProgressBar.setMinimumHeight = lambda self, h: QWidget.setMinimumHeight(self, max(8, h))
            ProgressBar._hikari_pb_patched = True
    except Exception as e:
        print(f"[DesignSystem] ProgressBar patch warning: {e}")

    # 4. Patch SegmentedWidget paintEvent for Pill-Style Gradient Active Tab
    try:
        from qfluentwidgets.components.navigation.segmented_widget import SegmentedWidget

        if not getattr(SegmentedWidget, "_hikari_seg_patched", False):
            def _patched_seg_paint(self, e):
                from PyQt6.QtCore import QAbstractAnimation
                QWidget.paintEvent(self, e)
                p = QPainter(self)
                p.setRenderHint(QPainter.RenderHint.Antialiasing)

                w, h = float(self.width()), float(self.height())
                # Draw background track
                p.setPen(QPen(QColor(Colors.BORDER), 1.0))
                p.setBrush(QColor("#0D1324"))
                p.drawRoundedRect(QRectF(0.5, 0.5, w - 1.0, h - 1.0), 8.0, 8.0)

                item = self.currentItem()
                if not item and getattr(self, "items", None):
                    item = next(iter(self.items.values()), None)
                if not item:
                    p.end()
                    return

                if self.slideAni.state() == QAbstractAnimation.State.Running:
                    ind_x = float(self.slideAni.value())
                else:
                    ind_x = float(item.x())

                item_w = float(item.width())
                pill_rect = QRectF(ind_x + 3.0, 3.0, max(10.0, item_w - 6.0), h - 6.0)

                pill_grad = QLinearGradient(pill_rect.left(), 0, pill_rect.right(), 0)
                pill_grad.setColorAt(0.0, QColor(99, 102, 241, 145))   # Electric Blue #6366F1
                pill_grad.setColorAt(1.0, QColor(139, 92, 246, 145))   # Violet #8B5CF6

                p.setPen(QPen(QColor("#818CF8"), 1.0))
                p.setBrush(QBrush(pill_grad))
                p.drawRoundedRect(pill_rect, 6.0, 6.0)
                p.end()

            SegmentedWidget.paintEvent = _patched_seg_paint
            SegmentedWidget._hikari_seg_patched = True
    except Exception as e:
        print(f"[DesignSystem] SegmentedWidget patch warning: {e}")

    # 5. Patch NavigationIndicator & NavigationPushButton for Modern SaaS Sidebar
    try:
        from qfluentwidgets.components.navigation.navigation_widget import (
            NavigationIndicator, NavigationPushButton
        )

        if not getattr(NavigationIndicator, "_hikari_nav_patched", False):
            def _patched_nav_ind_paint(self, e):
                p = QPainter(self)
                p.setRenderHint(QPainter.RenderHint.Antialiasing)
                w, h = float(self.width()), float(self.height())
                grad = QLinearGradient(0, 0, 0, h)
                grad.setColorAt(0.0, QColor(Colors.ACCENT_BRIGHT))
                grad.setColorAt(0.5, QColor(Colors.PRIMARY))
                grad.setColorAt(1.0, QColor(Colors.HIGHLIGHT))
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QBrush(grad))
                r = min(w, h) / 2.0
                p.drawRoundedRect(QRectF(0, 0, w, h), r, r)
                p.end()

            NavigationIndicator.paintEvent = _patched_nav_ind_paint
            NavigationIndicator._hikari_nav_patched = True

        if not getattr(NavigationPushButton, "_hikari_nav_btn_patched", False):
            _orig_nav_btn_paint = NavigationPushButton.paintEvent

            def _patched_nav_btn_paint(self, e):
                # Draw subtle gradient active/hover pill behind standard icon + text
                if getattr(self, "isSelected", False) or getattr(self, "isEnter", False):
                    p = QPainter(self)
                    p.setRenderHint(QPainter.RenderHint.Antialiasing)
                    m = self._margins() if hasattr(self, "_margins") else None
                    left_m = m.left() if m else 0
                    right_m = m.right() if m else 0
                    rect = QRectF(left_m + 4, 2, self.width() - left_m - right_m - 8, self.height() - 4)

                    if getattr(self, "isSelected", False):
                        bg_grad = QLinearGradient(rect.left(), 0, rect.right(), 0)
                        bg_grad.setColorAt(0.0, QColor(99, 102, 241, 55))
                        bg_grad.setColorAt(0.6, QColor(139, 92, 246, 38))
                        bg_grad.setColorAt(1.0, QColor(6, 182, 212, 20))
                        p.setPen(QPen(QColor(99, 102, 241, 110), 1.0))
                        p.setBrush(QBrush(bg_grad))
                        p.drawRoundedRect(rect, 7.0, 7.0)

                        # Draw vertical gradient accent bar on left edge
                        ind_grad = QLinearGradient(0, rect.top() + 5, 0, rect.bottom() - 5)
                        ind_grad.setColorAt(0.0, QColor(Colors.ACCENT_BRIGHT))
                        ind_grad.setColorAt(0.5, QColor(Colors.PRIMARY))
                        ind_grad.setColorAt(1.0, QColor(Colors.HIGHLIGHT))
                        p.setPen(Qt.PenStyle.NoPen)
                        p.setBrush(QBrush(ind_grad))
                        p.drawRoundedRect(QRectF(left_m + 5, rect.top() + 6, 3.5, rect.height() - 12), 1.75, 1.75)
                    elif getattr(self, "isEnter", False):
                        p.setPen(QPen(QColor(99, 102, 241, 45), 1.0))
                        p.setBrush(QColor(255, 255, 255, 10))
                        p.drawRoundedRect(rect, 7.0, 7.0)
                    p.end()

                _orig_nav_btn_paint(self, e)

            NavigationPushButton.paintEvent = _patched_nav_btn_paint
            NavigationPushButton._hikari_nav_btn_patched = True
    except Exception as e:
        print(f"[DesignSystem] Navigation patch warning: {e}")

    # 6. Slider uses qconfig.themeColor (#6366F1) automatically via setThemeColor


def _lerp_color(c1: QColor, c2: QColor, t: float) -> QColor:
    t = max(0.0, min(1.0, t))
    return QColor(
        int(c1.red() + (c2.red() - c1.red()) * t),
        int(c1.green() + (c2.green() - c1.green()) * t),
        int(c1.blue() + (c2.blue() - c1.blue()) * t),
        int(c1.alpha() + (c2.alpha() - c1.alpha()) * t),
    )


def install_design_system(app: QApplication):
    """
    Applies the complete Modern SaaS Design System to the QApplication:
    1. Sets QFluentWidgets theme & primary color (#6366F1).
    2. Configures dark navy QPalette (#0B1020 / #151B2E / #F8FAFC).
    3. Patches QFluentWidgets engine (FluentStyleSheet, CardWidget, ProgressBar, SegmentedWidget, Navigation).
    4. Installs global QSS stylesheet.
    """
    from qfluentwidgets import setTheme, Theme, setThemeColor, qconfig

    _patch_qfluentwidgets_engine()

    qconfig.set(qconfig.themeMode, Theme.DARK, save=False)
    setTheme(Theme.DARK)

    primary_color = QColor(Colors.PRIMARY)
    qconfig.set(qconfig.themeColor, primary_color, save=False)
    setThemeColor(primary_color)

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(Colors.BG_DARK))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(Colors.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Base, QColor(Colors.BG_DEEP))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(Colors.SURFACE))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(Colors.SURFACE))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(Colors.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Text, QColor(Colors.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Button, QColor(Colors.SURFACE))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(Colors.TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(Colors.ACCENT_BRIGHT))
    palette.setColor(QPalette.ColorRole.Link, QColor(Colors.ACCENT_BRIGHT))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(Colors.PRIMARY))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#FFFFFF"))
    app.setPalette(palette)

    app.setStyleSheet(get_global_app_stylesheet())

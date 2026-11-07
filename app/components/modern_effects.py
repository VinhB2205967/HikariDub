"""
Hikari Tsukimi — Modern SaaS Animation, Motion & UI Components
Provides hardware-friendly animations, reduced-motion support, Top SaaS Header Bar,
Live Status Badge, Hover Glow Controllers, and Empty State components.
"""

from __future__ import annotations
import os
import math
import ctypes
from PyQt6.QtCore import (
    Qt, QObject, QEvent, QVariantAnimation, QEasingCurve,
    QTimer, QRectF, QPointF, pyqtSignal
)
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QLinearGradient,
    QRadialGradient, QPainterPath, QFont
)
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QFrame,
    QSizePolicy, QGraphicsOpacityEffect, QStackedWidget
)
from qfluentwidgets import PushButton, PrimaryPushButton

from app.common.design_system import Colors, Gradients


# ─────────────────────────────────────────────────────────────────────────────
# 1. Reduced Motion Detection (Accessibility & Performance)
# ─────────────────────────────────────────────────────────────────────────────

def prefers_reduced_motion() -> bool:
    """
    Checks whether the user or OS has requested reduced motion
    (Windows SPI_GETCLIENTAREAANIMATION or HIKARI_REDUCED_MOTION=1).
    """
    if os.environ.get("HIKARI_REDUCED_MOTION", "0") == "1":
        return True
    if os.name == "nt":
        try:
            enabled = ctypes.c_int(1)
            SPI_GETCLIENTAREAANIMATION = 0x1042
            ctypes.windll.user32.SystemParametersInfoW(
                SPI_GETCLIENTAREAANIMATION, 0, ctypes.byref(enabled), 0
            )
            return enabled.value == 0
        except Exception:
            return False
    return False


# ─────────────────────────────────────────────────────────────────────────────
# 2. Smooth Hover Glow & Card Elevation Filter
# ─────────────────────────────────────────────────────────────────────────────

class HoverGlowFilter(QObject):
    """
    Lightweight event filter that smoothly interpolates `_hikari_hover_prog`
    between 0.0 and 1.0 on Enter/Leave events, triggering smooth border glow
    and surface gradient transitions on CardWidget and custom buttons.
    """

    def __init__(self, target: QWidget, duration_ms: int = 160):
        super().__init__(target)
        self._target = target
        self._target._hikari_hover_prog = 0.0

        self._anim = QVariantAnimation(self)
        self._anim.setDuration(0 if prefers_reduced_motion() else duration_ms)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.valueChanged.connect(self._on_val)

    def _on_val(self, val):
        if self._target:
            self._target._hikari_hover_prog = float(val)
            self._target.update()

    def eventFilter(self, obj, event):
        et = event.type()
        if et == QEvent.Type.Enter:
            if prefers_reduced_motion():
                self._target._hikari_hover_prog = 1.0
                self._target.update()
            else:
                self._anim.stop()
                self._anim.setStartValue(float(getattr(self._target, "_hikari_hover_prog", 0.0)))
                self._anim.setEndValue(1.0)
                self._anim.start()
        elif et == QEvent.Type.Leave:
            if prefers_reduced_motion():
                self._target._hikari_hover_prog = 0.0
                self._target.update()
            else:
                self._anim.stop()
                self._anim.setStartValue(float(getattr(self._target, "_hikari_hover_prog", 0.0)))
                self._anim.setEndValue(0.0)
                self._anim.start()
        return False


def attach_hover_glow(widget: QWidget, duration_ms: int = 160):
    """Safely attaches a HoverGlowFilter to a widget once."""
    if widget is None or getattr(widget, "_has_hikari_hover_filter", False):
        return
    flt = HoverGlowFilter(widget, duration_ms)
    widget.installEventFilter(flt)
    widget._hikari_hover_filter_ref = flt
    widget._has_hikari_hover_filter = True


# ─────────────────────────────────────────────────────────────────────────────
# 3. Smooth StackedWidget Tab Fade Transition
# ─────────────────────────────────────────────────────────────────────────────

def install_stacked_fade_transition(stacked: QStackedWidget, duration_ms: int = 170):
    """
    Adds a subtle, non-blocking opacity fade transition when switching pages
    inside a QStackedWidget (e.g., SRT tabs, Settings tabs, Report tabs).
    """
    if stacked is None or getattr(stacked, "_hikari_fade_installed", False):
        return
    stacked._hikari_fade_installed = True

    def _on_current_changed(idx: int):
        if prefers_reduced_motion():
            return
        w = stacked.widget(idx)
        if w is None:
            return
        # Avoid applying QGraphicsEffect to widgets containing native video canvas
        if w.findChild(QWidget, "hikariCol2") is not None:
            return
        try:
            eff = QGraphicsOpacityEffect(w)
            w.setGraphicsEffect(eff)
            anim = QVariantAnimation(w)
            anim.setDuration(duration_ms)
            anim.setStartValue(0.35)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.valueChanged.connect(lambda v: eff.setOpacity(float(v)))
            anim.finished.connect(lambda: w.setGraphicsEffect(None))
            w._hikari_tab_anim = anim
            anim.start()
        except Exception:
            pass

    stacked.currentChanged.connect(_on_current_changed)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Dialog Fade-In Entrance Animation
# ─────────────────────────────────────────────────────────────────────────────

def install_dialog_entrance(dialog_cls):
    """Patches a Dialog class showEvent to smoothly fade in when opened."""
    if getattr(dialog_cls, "_hikari_entrance_patched", False):
        return
    _orig_show = dialog_cls.showEvent

    def _patched_show(self, event):
        _orig_show(self, event)
        if prefers_reduced_motion():
            return
        try:
            self.setWindowOpacity(0.0)
            anim = QVariantAnimation(self)
            anim.setDuration(160)
            anim.setStartValue(0.0)
            anim.setEndValue(1.0)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            anim.valueChanged.connect(lambda v: self.setWindowOpacity(float(v)))
            self._hikari_entrance_anim = anim
            anim.start()
        except Exception:
            self.setWindowOpacity(1.0)

    dialog_cls.showEvent = _patched_show
    dialog_cls._hikari_entrance_patched = True


# ─────────────────────────────────────────────────────────────────────────────
# 5. Ambient SaaS Background Painter
# ─────────────────────────────────────────────────────────────────────────────

def paint_ambient_background(widget: QWidget, painter: QPainter, phase: float = 0.0):
    """
    Draws deep Dark Navy (#0B1020) with subtle, atmospheric radial glows
    of Electric Blue (#6366F1), Violet (#8B5CF6), and Cyan (#06B6D4).
    """
    w = float(widget.width())
    h = float(widget.height())
    painter.fillRect(0, 0, int(w), int(h), QColor(Colors.BG_DARK))

    dx = math.sin(phase) * 30.0 if phase else 0.0
    dy = math.cos(phase * 0.7) * 20.0 if phase else 0.0

    # Top-left Electric Blue radial glow
    g1 = QRadialGradient(QPointF(w * 0.18 + dx, h * 0.12 + dy), max(w, h) * 0.45)
    g1.setColorAt(0.0, QColor(99, 102, 241, 26))   # #6366F1
    g1.setColorAt(0.5, QColor(99, 102, 241, 10))
    g1.setColorAt(1.0, QColor(11, 16, 32, 0))
    painter.fillRect(0, 0, int(w), int(h), QBrush(g1))

    # Top-right Violet/Pink radial glow
    g2 = QRadialGradient(QPointF(w * 0.85 - dx, h * 0.18 - dy), max(w, h) * 0.42)
    g2.setColorAt(0.0, QColor(139, 92, 246, 22))   # #8B5CF6
    g2.setColorAt(0.45, QColor(236, 72, 153, 9))   # #EC4899
    g2.setColorAt(1.0, QColor(11, 16, 32, 0))
    painter.fillRect(0, 0, int(w), int(h), QBrush(g2))

    # Bottom-center Cyan glow
    g3 = QRadialGradient(QPointF(w * 0.50, h * 0.92), max(w, h) * 0.40)
    g3.setColorAt(0.0, QColor(6, 182, 212, 18))    # #06B6D4
    g3.setColorAt(1.0, QColor(11, 16, 32, 0))
    painter.fillRect(0, 0, int(w), int(h), QBrush(g3))


# ─────────────────────────────────────────────────────────────────────────────
# 6. Animated Status Pill Badge (Idle / Processing / Success / Error)
# ─────────────────────────────────────────────────────────────────────────────

class AnimatedStatusBadge(QWidget):
    """
    Modern SaaS status pill with animated indicator dot / spinner ring.
    States: 'ready', 'processing', 'success', 'warning', 'error'.
    """

    def __init__(self, text: str = "Sẵn sàng", state: str = "ready", parent=None):
        super().__init__(parent)
        self._text = text
        self._state = state
        self._angle = 0.0
        self._pulse = 0.0

        self._timer = QTimer(self)
        self._timer.setInterval(45)
        self._timer.timeout.connect(self._tick)

        self.setFixedHeight(26)
        self._update_width()

    def _update_width(self):
        fm = self.fontMetrics()
        tw = fm.horizontalAdvance(self._text)
        self.setFixedWidth(max(96, tw + 38))

    def set_state(self, state: str, text: str | None = None):
        self._state = state
        if text is not None:
            self._text = text
        self._update_width()

        if state == "processing" and not prefers_reduced_motion():
            if not self._timer.isActive():
                self._timer.start()
        else:
            self._timer.stop()
        self.update()

    def _tick(self):
        self._angle = (self._angle + 18.0) % 360.0
        self._pulse = (self._pulse + 0.15) % (math.pi * 2.0)
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = float(self.width()), float(self.height())
        rect = QRectF(0.5, 0.5, w - 1.0, h - 1.0)

        palette_map = {
            "ready":      (QColor("#10B981"), QColor(16, 185, 129, 28), QColor(16, 185, 129, 95)),
            "processing": (QColor("#22D3EE"), QColor(99, 102, 241, 38), QColor(99, 102, 241, 140)),
            "success":    (QColor("#34D399"), QColor(16, 185, 129, 36), QColor(52, 211, 153, 130)),
            "warning":    (QColor("#FBBF24"), QColor(245, 158, 11, 32), QColor(245, 158, 11, 120)),
            "error":      (QColor("#F87171"), QColor(239, 68, 68, 34),  QColor(239, 68, 68, 130)),
        }
        dot_c, bg_c, border_c = palette_map.get(self._state, palette_map["ready"])

        p.setPen(QPen(border_c, 1.0))
        p.setBrush(bg_c)
        p.drawRoundedRect(rect, h / 2.0, h / 2.0)

        # Draw indicator dot or spinning arc
        cx, cy = 14.0, h / 2.0
        if self._state == "processing":
            pen_arc = QPen(dot_c, 2.0)
            pen_arc.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen_arc)
            p.setBrush(Qt.BrushStyle.NoBrush)
            arc_rect = QRectF(cx - 5.0, cy - 5.0, 10.0, 10.0)
            p.drawArc(arc_rect, int(-self._angle * 16), 240 * 16)
        else:
            p.setPen(Qt.PenStyle.NoPen)
            glow_c = QColor(dot_c.red(), dot_c.green(), dot_c.blue(), 75)
            p.setBrush(glow_c)
            p.drawEllipse(QPointF(cx, cy), 6.0, 6.0)
            p.setBrush(dot_c)
            p.drawEllipse(QPointF(cx, cy), 3.5, 3.5)

        # Draw label text
        p.setPen(QColor(Colors.TEXT_PRIMARY))
        font = QFont("Segoe UI Variable Text", 9)
        font.setWeight(QFont.Weight.DemiBold)
        p.setFont(font)
        text_rect = QRectF(25.0, 0.0, w - 31.0, h)
        p.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self._text)
        p.end()


# ─────────────────────────────────────────────────────────────────────────────
# 7. Modern SaaS Top Header Bar (Workspace Header)
# ─────────────────────────────────────────────────────────────────────────────

class ModernHeaderBar(QWidget):
    """
    Top Navigation & Context Header Bar inspired by Linear, Raycast & Framer.
    Displays current view title, subtitle, live AI engine status badge,
    and quick action buttons.
    """

    open_output_requested = pyqtSignal()
    go_settings_requested = pyqtSignal()
    go_home_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("hikariModernHeader")
        self.setFixedHeight(46)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 4, 16, 4)
        layout.setSpacing(12)

        # 1. Left: Active Screen Icon Badge + Title & Subtitle
        self.lbl_icon = QLabel("✦")
        self.lbl_icon.setFixedSize(32, 32)
        self.lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_icon.setStyleSheet(f"""
            background: {Gradients.BLUE_PURPLE};
            color: #FFFFFF;
            font-size: 15px;
            font-weight: 800;
            border-radius: 8px;
            border: 1px solid #818CF8;
        """)
        layout.addWidget(self.lbl_icon)

        title_col = QVBoxLayout()
        title_col.setContentsMargins(0, 0, 0, 0)
        title_col.setSpacing(1)

        self.lbl_title = QLabel("BẢNG ĐIỀU KHIỂN STUDIO")
        self.lbl_title.setStyleSheet(f"""
            color: {Colors.TEXT_PRIMARY};
            font-size: 13px;
            font-weight: 800;
            letter-spacing: 0.6px;
        """)

        self.lbl_subtitle = QLabel("Không gian xử lý Video AI, Phụ đề & Lồng tiếng đa ngôn ngữ tự động")
        self.lbl_subtitle.setStyleSheet(f"""
            color: {Colors.TEXT_SECONDARY};
            font-size: 11px;
            font-weight: 500;
        """)

        title_col.addWidget(self.lbl_title)
        title_col.addWidget(self.lbl_subtitle)
        layout.addLayout(title_col)

        layout.addStretch(1)

        # 2. Right: Live Engine Status Badge + Quick Actions + Brand Pill
        self.status_badge = AnimatedStatusBadge("AI Engine Sẵn sàng", "ready", self)
        layout.addWidget(self.status_badge)

        quick_btn_qss = f"""
            PushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1B243B, stop:1 #141B2D);
                border: 1px solid {Colors.BORDER};
                border-radius: 7px;
                color: {Colors.TEXT_PRIMARY};
                font-size: 11px;
                font-weight: 600;
                padding: 4px 11px;
                min-height: 26px;
                max-height: 26px;
            }}
            PushButton:hover {{
                background: {Gradients.BLUE_PURPLE};
                border: 1px solid #818CF8;
                color: #FFFFFF;
            }}
            PushButton:pressed {{
                background: {Colors.PRIMARY_PRESSED};
            }}
        """

        self.btn_quick_home = PushButton("🎬 Bảng điều khiển")
        self.btn_quick_home.setStyleSheet(quick_btn_qss)
        self.btn_quick_home.setToolTip("Quay về màn hình chính Bảng Điều Khiển Studio")
        self.btn_quick_home.clicked.connect(self.go_home_requested.emit)
        layout.addWidget(self.btn_quick_home)

        self.btn_quick_output = PushButton("📂 Thư mục xuất")
        self.btn_quick_output.setStyleSheet(quick_btn_qss)
        self.btn_quick_output.setToolTip("Mở nhanh thư mục chứa các dự án video đầu ra")
        self.btn_quick_output.clicked.connect(self.open_output_requested.emit)
        layout.addWidget(self.btn_quick_output)

        self.btn_quick_settings = PushButton("⚙ Cấu hình AI")
        self.btn_quick_settings.setStyleSheet(quick_btn_qss)
        self.btn_quick_settings.setToolTip("Mở nhanh cài đặt mô hình Whisper, OCR và phần cứng")
        self.btn_quick_settings.clicked.connect(self.go_settings_requested.emit)
        layout.addWidget(self.btn_quick_settings)

        self.lbl_tier_badge = QLabel("✦ PRO STUDIO")
        self.lbl_tier_badge.setFixedHeight(26)
        self.lbl_tier_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_tier_badge.setStyleSheet(f"""
            background: {Gradients.INDIGO_VIOLET_PINK};
            color: #FFFFFF;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 0.8px;
            padding: 0px 10px;
            border-radius: 13px;
            border: 1px solid #F472B6;
        """)
        layout.addWidget(self.lbl_tier_badge)

    def set_page_info(self, icon_str: str, title: str, subtitle: str):
        self.lbl_icon.setText(icon_str)
        self.lbl_title.setText(title)
        self.lbl_subtitle.setText(subtitle)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = float(self.width()), float(self.height())

        # Subtle dark glass header gradient
        bg = QLinearGradient(0, 0, w, 0)
        bg.setColorAt(0.0, QColor(14, 20, 38, 235))
        bg.setColorAt(0.5, QColor(21, 27, 46, 235))
        bg.setColorAt(1.0, QColor(14, 20, 38, 235))
        p.fillRect(QRectF(0, 0, w, h), QBrush(bg))

        # Subtle bottom gradient accent border line
        line_grad = QLinearGradient(0, 0, w, 0)
        line_grad.setColorAt(0.0, QColor(99, 102, 241, 140))    # Electric Blue #6366F1
        line_grad.setColorAt(0.45, QColor(139, 92, 246, 110))   # Violet #8B5CF6
        line_grad.setColorAt(0.8, QColor(6, 182, 212, 95))      # Cyan #06B6D4
        line_grad.setColorAt(1.0, QColor(36, 47, 75, 80))
        p.setPen(QPen(QBrush(line_grad), 1.0))
        p.drawLine(QPointF(0, h - 0.5), QPointF(w, h - 0.5))
        p.end()


# ─────────────────────────────────────────────────────────────────────────────
# 8. Modern SaaS Empty State Component
# ─────────────────────────────────────────────────────────────────────────────

class ModernEmptyState(QWidget):
    """
    Clean, balanced empty state placeholder for lists, grids, or editors.
    """

    def __init__(self, icon_text: str, title: str, description: str, parent=None):
        super().__init__(parent)
        self.setObjectName("hikariEmptyState")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 28, 24, 28)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        badge = QLabel(icon_text)
        badge.setFixedSize(48, 48)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(99, 102, 241, 0.22), stop:1 rgba(236, 72, 153, 0.18));
            border: 1px solid rgba(99, 102, 241, 0.45);
            border-radius: 24px;
            color: {Colors.ACCENT_BRIGHT};
            font-size: 20px;
        """)

        lbl_title = QLabel(title)
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setWordWrap(True)
        lbl_title.setStyleSheet(f"""
            color: {Colors.TEXT_PRIMARY};
            font-size: 13px;
            font-weight: 700;
        """)

        lbl_desc = QLabel(description)
        lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_desc.setWordWrap(True)
        lbl_desc.setStyleSheet(f"""
            color: {Colors.TEXT_SECONDARY};
            font-size: 11px;
            line-height: 1.4;
        """)

        icon_row = QHBoxLayout()
        icon_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_row.addWidget(badge)

        layout.addLayout(icon_row)
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_desc)

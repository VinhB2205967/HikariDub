"""
Reusable UI Components for Hikari Tsukimi v3.0:
- PrimaryButton, SecondaryButton, DangerButton, GhostButton, IconButton
- ElidedLabel (never clips unexpectedly; shows full text in tooltip)
- CollapsibleCard
- LabeledSlider
- PasswordInput (with show/hide toggle; masks sensitive Session ID / API Key)
- StepBadge & HorizontalStepper (waiting / running / done / error states)
- WaveformTimeline (renders simulated/audio waveform + subtitle segments)
- DropVideoZone (drag & drop empty state)
"""

import math
from app.qt_compat import (
    QWidget, QFrame, QLabel, QPushButton, QToolButton, QLineEdit, QSlider,
    QVBoxLayout, QHBoxLayout, Qt, Signal, QSizePolicy, QPainter, QColor,
    QPen, QBrush, QRectF, QFont, QFontMetrics
)
from app.theme import TOKENS


class PrimaryButton(QPushButton):
    def __init__(self, text: str, tooltip: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName("PrimaryButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Fixed)
        self.setToolTip(tooltip or text)


class SecondaryButton(QPushButton):
    def __init__(self, text: str, tooltip: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName("SecondaryButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.setToolTip(tooltip or text)


class DangerButton(QPushButton):
    def __init__(self, text: str, tooltip: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName("DangerButton")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.setToolTip(tooltip or text)


class GhostButton(QPushButton):
    def __init__(self, text: str, checkable: bool = False, tooltip: str = "", parent=None):
        super().__init__(text, parent)
        self.setObjectName("GhostButton")
        self.setCheckable(checkable)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(tooltip or text)


class ElidedLabel(QLabel):
    """Label that cleanly elides text with '...' when space is tight and sets full tooltip."""

    def __init__(self, text: str = "", parent=None):
        super().__init__(text, parent)
        self._full_text = text
        self.setToolTip(text)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

    def set_full_text(self, text: str):
        self._full_text = text or ""
        self.setToolTip(self._full_text)
        self._update_elided()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_elided()

    def _update_elided(self):
        fm = QFontMetrics(self.font())
        avail = max(40, self.width() - 4)
        self.setText(fm.elidedText(self._full_text, Qt.TextElideMode.ElideMiddle, avail))


class PasswordInput(QWidget):
    """Masked password input with Show/Hide toggle button for Session ID & API keys."""

    textChanged = Signal(str)

    def __init__(self, placeholder: str = "", parent=None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        self.line = QLineEdit(self)
        self.line.setPlaceholderText(placeholder)
        self.line.setEchoMode(QLineEdit.EchoMode.Password)
        self.line.textChanged.connect(self.textChanged.emit)

        self.btn_toggle = GhostButton("Hiện", checkable=True, tooltip="Hiện / Ẩn mã bí mật", parent=self)
        self.btn_toggle.setFixedWidth(54)
        self.btn_toggle.toggled.connect(self._on_toggled)

        lay.addWidget(self.line, 1)
        lay.addWidget(self.btn_toggle)

    def _on_toggled(self, checked: bool):
        self.line.setEchoMode(QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password)
        self.btn_toggle.setText("Ẩn" if checked else "Hiện")

    def text(self) -> str:
        return self.line.text()

    def setText(self, val: str):
        self.line.setText(val or "")


class LabeledSlider(QWidget):
    """Horizontal slider with label and live formatted readout."""

    valueChanged = Signal(int)

    def __init__(self, title: str, min_v: int, max_v: int, init_v: int, suffix: str = "%", parent=None):
        super().__init__(parent)
        self._suffix = suffix
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        self.lbl_title = QLabel(title, self)
        self.lbl_title.setObjectName("SubLabel")
        self.lbl_title.setMinimumWidth(68)

        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.setRange(min_v, max_v)
        self.slider.setValue(init_v)

        self.lbl_val = QLabel(f"{init_v}{suffix}", self)
        self.lbl_val.setMinimumWidth(42)
        self.lbl_val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_val.setStyleSheet(f"color: {TOKENS.PRIMARY_END}; font-weight: 700; font-size: 12px;")

        self.slider.valueChanged.connect(self._on_change)
        lay.addWidget(self.lbl_title)
        lay.addWidget(self.slider, 1)
        lay.addWidget(self.lbl_val)

    def _on_change(self, v: int):
        self.lbl_val.setText(f"{v}{self._suffix}")
        self.valueChanged.emit(v)

    def value(self) -> int:
        return self.slider.value()


class CollapsibleCard(QFrame):
    """Card with clickable header that expands/collapses its body cleanly."""

    def __init__(self, title: str, expanded: bool = True, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self._expanded = expanded

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 10)
        root.setSpacing(8)

        self.header_btn = QPushButton(self)
        self.header_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.header_btn.setStyleSheet(
            f"text-align: left; font-weight: 700; font-size: 14px; color: {TOKENS.TEXT_PRIMARY}; "
            "background: transparent; border: none; padding: 2px 0px;"
        )
        self.header_btn.clicked.connect(self.toggle)
        root.addWidget(self.header_btn)

        self.body = QWidget(self)
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(0, 4, 0, 0)
        self.body_layout.setSpacing(8)
        root.addWidget(self.body)

        self._title = title
        self._sync_ui()

    def toggle(self):
        self._expanded = not self._expanded
        self._sync_ui()

    def _sync_ui(self):
        arrow = "▾" if self._expanded else "▸"
        self.header_btn.setText(f"{arrow}  {self._title}")
        self.body.setVisible(self._expanded)


class StepperBar(QWidget):
    """4-Step visual pipeline stepper with states: waiting, running, done, error."""

    stepClicked = Signal(int)

    def __init__(self, labels: list, parent=None):
        super().__init__(parent)
        self.labels = labels
        self.states = ["waiting"] * len(labels)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)
        self.buttons = []
        for idx, text in enumerate(labels):
            btn = QPushButton(text, self)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setToolTip(f"Chạy riêng bước {text}")
            btn.clicked.connect(lambda _=False, i=idx: self.stepClicked.emit(i))
            self.buttons.append(btn)
            lay.addWidget(btn, 1)
        self._refresh_styles()

    def set_step_state(self, index: int, state: str):
        if 0 <= index < len(self.states):
            self.states[index] = state
            self._refresh_styles()

    def reset_all(self):
        self.states = ["waiting"] * len(self.labels)
        self._refresh_styles()

    def _refresh_styles(self):
        for i, btn in enumerate(self.buttons):
            st = self.states[i]
            base_lbl = self.labels[i]
            if st == "done":
                btn.setText(f"✓ {base_lbl}")
                btn.setStyleSheet(
                    f"background: rgba(46, 204, 113, 0.16); color: {TOKENS.SUCCESS}; "
                    f"border: 1px solid {TOKENS.SUCCESS}; border-radius: 8px; padding: 6px 10px; font-weight: 700;"
                )
            elif st == "running":
                btn.setText(f"⟳ {base_lbl}")
                btn.setStyleSheet(
                    f"background: rgba(124, 92, 255, 0.24); color: #FFFFFF; "
                    f"border: 1px solid {TOKENS.PRIMARY_START}; border-radius: 8px; padding: 6px 10px; font-weight: 700;"
                )
            elif st == "error":
                btn.setText(f"✕ {base_lbl}")
                btn.setStyleSheet(
                    f"background: rgba(255, 92, 92, 0.18); color: {TOKENS.ERROR}; "
                    f"border: 1px solid {TOKENS.ERROR}; border-radius: 8px; padding: 6px 10px; font-weight: 700;"
                )
            else:
                btn.setText(base_lbl)
                btn.setStyleSheet(
                    f"background: {TOKENS.BG_ELEVATED}; color: {TOKENS.TEXT_SECONDARY}; "
                    f"border: 1px solid {TOKENS.BORDER}; border-radius: 8px; padding: 6px 10px; font-weight: 600;"
                )


class WaveformTimeline(QWidget):
    """Draws audio waveform bars, subtitle blocks, and playhead cursor."""

    seekRequested = Signal(int)  # milliseconds

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(54)
        self.setMaximumHeight(64)
        self.duration_ms = 1000
        self.position_ms = 0
        self.subtitles = []  # list of (start_ms, end_ms, text)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_subtitles(self, subs: list):
        self.subtitles = subs or []
        self.update()

    def set_position(self, pos_ms: int, dur_ms: int = None):
        self.position_ms = max(0, pos_ms)
        if dur_ms and dur_ms > 0:
            self.duration_ms = dur_ms
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.width() > 0:
            ratio = max(0.0, min(1.0, event.position().x() / float(self.width())))
            self.seekRequested.emit(int(ratio * self.duration_ms))

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = float(self.width()), float(self.height())
        p.fillRect(QRectF(0, 0, w, h), QColor(TOKENS.BG_INPUT))

        # Draw simulated waveform bars
        bar_w = 3.0
        gap = 2.0
        count = max(1, int(w / (bar_w + gap)))
        p.setPen(Qt.PenStyle.NoPen)
        for i in range(count):
            amp = 0.25 + 0.55 * abs(math.sin(i * 0.37) * math.cos(i * 0.13))
            bh = amp * (h - 20)
            x = i * (bar_w + gap)
            y = (h - bh) / 2.0
            played = (x / max(1.0, w)) <= (self.position_ms / float(max(1, self.duration_ms)))
            p.setBrush(QColor(TOKENS.PRIMARY_END if played else "#2A3042"))
            p.drawRoundedRect(QRectF(x, y, bar_w, bh), 1.5, 1.5)

        # Draw subtitle segment markers along bottom edge
        dur = float(max(1, self.duration_ms))
        for s_ms, e_ms, _ in self.subtitles:
            sx = (s_ms / dur) * w
            sw = max(4.0, ((e_ms - s_ms) / dur) * w)
            p.setBrush(QColor(124, 92, 255, 140))
            p.drawRoundedRect(QRectF(sx, h - 10, sw, 7), 2, 2)

        # Playhead line
        px = (self.position_ms / dur) * w
        p.setPen(QPen(QColor(TOKENS.SUCCESS), 2.0))
        p.drawLine(int(px), 0, int(px), int(h))
        p.end()

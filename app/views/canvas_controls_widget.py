"""
Canvas Controls Widget - Hikari Dub v3.0
Streamlined Aspect Ratio, Video Zoom, and Position Transform controls.
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy,
    QFrame, QDoubleSpinBox, QSpinBox, QComboBox, QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from qfluentwidgets import PushButton

from app.core.canvas_transform import (
    CanvasTransform, ASPECT_RATIOS, get_canvas_size,
    save_transform, load_transform
)

# ─────────────────────────────── Style constants (Modern SaaS Palette) ───────
_DARK_BG     = "#151B2E"
_PANEL_BG    = "#111728"
_BORDER      = "#242F4B"
_PRIMARY     = "#6366F1"
_SECONDARY   = "#8B5CF6"
_ACCENT      = "#06B6D4"
_ACCENT_BRI  = "#22D3EE"
_HIGHLIGHT   = "#EC4899"
_TEXT        = "#F8FAFC"
_TEXT_DIM    = "#94A3B8"

_SECTION_STYLE = f"""
    color: {_ACCENT_BRI};
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 0.3px;
"""
_LABEL_STYLE = f"color: {_TEXT_DIM}; font-size: 11px; font-weight: 600;"
_VALUE_STYLE = f"color: {_TEXT}; font-size: 11px; font-weight: 700;"

_BADGE_STYLE = f"""
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(99, 102, 241, 0.22), stop:1 rgba(139, 92, 246, 0.22));
    border: 1px solid {_PRIMARY};
    border-radius: 6px;
    color: {_ACCENT_BRI};
    font-size: 11px;
    font-weight: 700;
    font-family: 'Consolas', monospace;
    padding: 3px 9px;
"""

_BTN_STYLE = f"""
    PushButton {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1C253E, stop:1 #141B2E);
        border: 1px solid {_BORDER};
        border-radius: 6px;
        color: {_TEXT};
        font-size: 11px;
        font-weight: 600;
        padding: 3px 9px;
        min-height: 24px;
        max-height: 24px;
    }}
    PushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366F1, stop:1 #8B5CF6);
        border: 1px solid #A78BFA;
        color: #FFFFFF;
    }}
    PushButton:pressed {{
        background: #4F46E5;
        color: #FFFFFF;
    }}
"""

_SPINBOX_STYLE = f"""
    QDoubleSpinBox, QSpinBox {{
        background-color: #090E1C;
        border: 1px solid {_BORDER};
        border-radius: 6px;
        color: {_TEXT};
        font-size: 11px;
        font-weight: 600;
        padding-left: 6px;
        padding-right: 2px;
        min-height: 24px;
        max-height: 24px;
    }}
    QDoubleSpinBox:hover, QSpinBox:hover {{
        border: 1px solid {_PRIMARY};
    }}
    QDoubleSpinBox:focus, QSpinBox:focus {{
        border: 1px solid {_ACCENT_BRI};
        background-color: #070B16;
    }}
    QDoubleSpinBox::up-button, QSpinBox::up-button {{
        subcontrol-origin: border;
        subcontrol-position: top right;
        width: 15px;
        border-left: 1px solid {_BORDER};
        border-bottom: 1px solid {_BORDER};
        background: #1A2238;
        border-top-right-radius: 5px;
    }}
    QDoubleSpinBox::down-button, QSpinBox::down-button {{
        subcontrol-origin: border;
        subcontrol-position: bottom right;
        width: 15px;
        border-left: 1px solid {_BORDER};
        background: #1A2238;
        border-bottom-right-radius: 5px;
    }}
    QDoubleSpinBox::up-button:hover, QSpinBox::up-button:hover,
    QDoubleSpinBox::down-button:hover, QSpinBox::down-button:hover {{
        background: {_PRIMARY};
    }}
"""

_SLIDER_STYLE = f"""
    QSlider::groove:horizontal {{
        height: 5px;
        background: #090E1C;
        border: 1px solid {_BORDER};
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {_ACCENT_BRI}, stop:1 {_PRIMARY});
        border: 2px solid #FFFFFF;
        width: 14px;
        height: 14px;
        margin: -6px 0;
        border-radius: 7px;
    }}
    QSlider::handle:horizontal:hover {{
        background: {_HIGHLIGHT};
        border: 2px solid #FFFFFF;
    }}
    QSlider::sub-page:horizontal {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {_ACCENT}, stop:0.6 {_PRIMARY}, stop:1 {_SECONDARY});
        border-radius: 2px;
    }}
"""

_COMBO_STYLE = f"""
    QComboBox {{
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1C253E, stop:1 #131A2C);
        border: 1px solid {_BORDER};
        border-radius: 6px;
        color: {_TEXT};
        font-size: 11px;
        font-weight: 600;
        padding: 3px 8px;
        min-height: 24px;
        max-height: 24px;
        min-width: 120px;
    }}
    QComboBox:hover {{
        border: 1px solid {_PRIMARY};
    }}
    QComboBox:focus {{
        border: 1px solid {_ACCENT_BRI};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 18px;
    }}
    QComboBox QAbstractItemView {{
        background-color: #151B2E;
        border: 1px solid {_PRIMARY};
        color: {_TEXT};
        selection-background-color: {_PRIMARY};
        selection-color: #FFFFFF;
    }}
"""

SEP_STYLE = f"background: {_BORDER}; max-width: 1px; min-width: 1px; max-height: 18px; min-height: 18px;"


def _make_label(text: str, style: str = _LABEL_STYLE) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(style)
    return lbl


def _make_separator() -> QFrame:
    sep = QFrame()
    sep.setFrameShape(QFrame.Shape.VLine)
    sep.setStyleSheet(SEP_STYLE)
    return sep


class CanvasControlsWidget(QWidget):
    """
    Unified toolbar for Canvas Aspect Ratio, Video Zoom, and Position Transform controls.
    Streamlined 2-row layout designed for maximum vertical workspace.
    """

    transform_changed = pyqtSignal(object)  # CanvasTransform
    fill_requested = pyqtSignal()
    theater_toggled = pyqtSignal()
    popout_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._transform = load_transform()
        self._updating = False

        self._build_ui()
        self._connect_signals()
        self._sync_ui_from_transform()

    def get_transform(self) -> CanvasTransform:
        return self._transform

    def set_theater_active(self, active: bool):
        if hasattr(self, 'btn_theater'):
            self.btn_theater.setText("⛶ Thu Nhỏ" if active else "⛶ Xem Rộng")

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(6, 4, 6, 4)
        root.setSpacing(3)

        # ── Row 1: Aspect Ratio & Video Zoom ────────────────────────────────
        row1 = QHBoxLayout()
        row1.setSpacing(6)

        row1.addWidget(_make_label("Tỷ lệ:", _SECTION_STYLE))

        self.combo_ratio = QComboBox()
        self.combo_ratio.setStyleSheet(_COMBO_STYLE)
        self.combo_ratio.setFixedHeight(24)
        self.combo_ratio.setToolTip("Chọn tỷ lệ khung hình canvas xuất video")

        ratio_display = {
            "16:9": "16:9 (Ngang)",
            "9:16": "9:16 (Dọc Shorts)",
            "3:4":  "3:4 (Dọc)",
            "1:1":  "1:1 (Vuông)",
            "4:3":  "4:3 (Truyền thống)",
            "custom": "Tùy chỉnh",
        }
        for r_key, r_label in ratio_display.items():
            self.combo_ratio.addItem(r_label, r_key)
        row1.addWidget(self.combo_ratio)

        # Custom dimensions (hidden unless "custom" is selected)
        self.lbl_cw = _make_label("W:")
        self.spin_cw = QSpinBox()
        self.spin_cw.setRange(100, 7680)
        self.spin_cw.setValue(1920)
        self.spin_cw.setFixedWidth(56)
        self.spin_cw.setStyleSheet(_SPINBOX_STYLE)

        self.lbl_ch = _make_label("H:")
        self.spin_ch = QSpinBox()
        self.spin_ch.setRange(100, 4320)
        self.spin_ch.setValue(1080)
        self.spin_ch.setFixedWidth(56)
        self.spin_ch.setStyleSheet(_SPINBOX_STYLE)

        row1.addWidget(self.lbl_cw)
        row1.addWidget(self.spin_cw)
        row1.addWidget(self.lbl_ch)
        row1.addWidget(self.spin_ch)
        self._set_custom_visible(False)

        # Fit & Fill quick buttons
        self.btn_fit = PushButton("⊡ Vừa")
        self.btn_fit.setStyleSheet(_BTN_STYLE)
        self.btn_fit.setFixedHeight(24)
        self.btn_fit.setToolTip("Hiển thị toàn bộ video vừa với Canvas (Fit)")

        self.btn_fill = PushButton("⊞ Đầy")
        self.btn_fill.setStyleSheet(_BTN_STYLE)
        self.btn_fill.setFixedHeight(24)
        self.btn_fill.setToolTip("Phóng to video lấp đầy Canvas không có viền đen (Fill)")

        row1.addWidget(self.btn_fit)
        row1.addWidget(self.btn_fill)

        # Canvas nominal size display as pill badge
        self.lbl_canvas_size = _make_label("1920 × 1080", _BADGE_STYLE)
        self.lbl_canvas_size.setToolTip("Kích thước Canvas xuất video")
        row1.addWidget(self.lbl_canvas_size)

        row1.addWidget(_make_separator())

        # Video Zoom inline on Row 1
        row1.addWidget(_make_label("Zoom:", _SECTION_STYLE))

        self.btn_zoom_out = PushButton("−")
        self.btn_zoom_out.setStyleSheet(_BTN_STYLE)
        self.btn_zoom_out.setFixedSize(22, 22)
        self.btn_zoom_out.setToolTip("Thu nhỏ video (−10%)")

        self.slider_zoom = QSlider(Qt.Orientation.Horizontal)
        self.slider_zoom.setRange(10, 300)
        self.slider_zoom.setValue(100)
        self.slider_zoom.setFixedWidth(110)
        self.slider_zoom.setStyleSheet(_SLIDER_STYLE)
        self.slider_zoom.setToolTip("Kéo để phóng to / thu nhỏ video bên trong Canvas")

        self.btn_zoom_in = PushButton("+")
        self.btn_zoom_in.setStyleSheet(_BTN_STYLE)
        self.btn_zoom_in.setFixedSize(22, 22)
        self.btn_zoom_in.setToolTip("Phóng to video (+10%)")

        self.lbl_zoom_val = _make_label("100%", f"color: {_ACCENT}; font-size: 11px; font-weight: 700;")
        self.lbl_zoom_val.setFixedWidth(38)

        row1.addWidget(self.btn_zoom_out)
        row1.addWidget(self.slider_zoom)
        row1.addWidget(self.btn_zoom_in)
        row1.addWidget(self.lbl_zoom_val)

        self.btn_zoom_reset = PushButton("↺ 100%")
        self.btn_zoom_reset.setStyleSheet(_BTN_STYLE)
        self.btn_zoom_reset.setFixedHeight(24)
        self.btn_zoom_reset.setToolTip("Đặt lại Video Zoom về 100%")
        row1.addWidget(self.btn_zoom_reset)

        row1.addStretch()
        root.addLayout(row1)

        # ── Row 2: Video Position, Rotation & Theater/Popout Mode ─────────────
        row2 = QHBoxLayout()
        row2.setSpacing(6)

        row2.addWidget(_make_label("Vị trí & Xoay:", _SECTION_STYLE))

        # Position X
        row2.addWidget(_make_label("X:"))
        self.spin_pos_x = QDoubleSpinBox()
        self.spin_pos_x.setDecimals(0)
        self.spin_pos_x.setRange(-4000, 4000)
        self.spin_pos_x.setValue(0)
        self.spin_pos_x.setSingleStep(10.0)
        self.spin_pos_x.setSuffix(" px")
        self.spin_pos_x.setFixedWidth(68)
        self.spin_pos_x.setStyleSheet(_SPINBOX_STYLE)
        self.spin_pos_x.setToolTip("Vị trí ngang video trong Canvas")
        row2.addWidget(self.spin_pos_x)

        # Position Y
        row2.addWidget(_make_label("Y:"))
        self.spin_pos_y = QDoubleSpinBox()
        self.spin_pos_y.setDecimals(0)
        self.spin_pos_y.setRange(-4000, 4000)
        self.spin_pos_y.setValue(0)
        self.spin_pos_y.setSingleStep(10.0)
        self.spin_pos_y.setSuffix(" px")
        self.spin_pos_y.setFixedWidth(68)
        self.spin_pos_y.setStyleSheet(_SPINBOX_STYLE)
        self.spin_pos_y.setToolTip("Vị trí dọc video trong Canvas")
        row2.addWidget(self.spin_pos_y)

        # Rotation
        row2.addWidget(_make_label("Xoay:"))
        self.spin_rot = QDoubleSpinBox()
        self.spin_rot.setDecimals(0)
        self.spin_rot.setRange(-360, 360)
        self.spin_rot.setValue(0)
        self.spin_rot.setSingleStep(1.0)
        self.spin_rot.setSuffix("°")
        self.spin_rot.setFixedWidth(56)
        self.spin_rot.setStyleSheet(_SPINBOX_STYLE)
        self.spin_rot.setToolTip("Góc xoay video")
        row2.addWidget(self.spin_rot)

        self.btn_center = PushButton("⊕ Giữa")
        self.btn_center.setStyleSheet(_BTN_STYLE)
        self.btn_center.setFixedHeight(24)
        self.btn_center.setToolTip("Đưa video về tâm Canvas (X=0, Y=0)")
        row2.addWidget(self.btn_center)

        self.btn_reset_all = PushButton("↺ Đặt lại")
        self.btn_reset_all.setStyleSheet(_BTN_STYLE)
        self.btn_reset_all.setFixedHeight(24)
        self.btn_reset_all.setToolTip("Khôi phục toàn bộ: Zoom 100%, X=0, Y=0, Xoay 0°")
        row2.addWidget(self.btn_reset_all)

        row2.addStretch()

        # Expand / Theater Mode button
        self.btn_theater = PushButton("⛶ Xem Rộng")
        self.btn_theater.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.btn_theater.setMinimumWidth(104)
        self.btn_theater.setStyleSheet(f"""
            PushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366F1, stop:1 #8B5CF6);
                border: 1px solid #A78BFA;
                border-radius: 6px;
                color: #FFFFFF;
                font-size: 11px;
                font-weight: 700;
                padding: 3px 10px;
                min-height: 24px;
                max-height: 24px;
            }}
            PushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #818CF8, stop:1 #A78BFA);
                border-color: #C084FC;
            }}
        """)
        self.btn_theater.setToolTip("Xem Rộng (Theater) — Mở rộng tối đa không gian xem trước (ẩn tạm thời 2 cột bên)")
        self.btn_theater.clicked.connect(self.theater_toggled.emit)
        row2.addWidget(self.btn_theater)

        # Pop-out Floating Window button
        self.btn_popout = PushButton("🔍 Cửa Sổ Riêng")
        self.btn_popout.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.btn_popout.setMinimumWidth(118)
        self.btn_popout.setStyleSheet(_BTN_STYLE)
        self.btn_popout.setFixedHeight(24)
        self.btn_popout.setToolTip("Cửa Sổ Riêng — Mở không gian xem trước trong cửa sổ riêng biệt để phóng to tùy ý")
        self.btn_popout.clicked.connect(self.popout_requested.emit)
        row2.addWidget(self.btn_popout)

        root.addLayout(row2)

        self.setStyleSheet(f"""
            CanvasControlsWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0E1426, stop:0.5 #131B31, stop:1 #0E1426);
                border: 1px solid {_BORDER};
                border-radius: 9px;
            }}
        """)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def _connect_signals(self):
        self.combo_ratio.currentIndexChanged.connect(self._on_ratio_changed)
        self.spin_cw.valueChanged.connect(self._on_custom_size_changed)
        self.spin_ch.valueChanged.connect(self._on_custom_size_changed)

        self.btn_fit.clicked.connect(self._on_fit_clicked)
        self.btn_fill.clicked.connect(self._on_fill_clicked)

        self.slider_zoom.valueChanged.connect(self._on_zoom_slider_changed)
        self.btn_zoom_in.clicked.connect(self._zoom_in)
        self.btn_zoom_out.clicked.connect(self._zoom_out)
        self.btn_zoom_reset.clicked.connect(self._zoom_reset)

        self.spin_pos_x.valueChanged.connect(self._on_pos_changed)
        self.spin_pos_y.valueChanged.connect(self._on_pos_changed)
        self.spin_rot.valueChanged.connect(self._on_pos_changed)

        self.btn_center.clicked.connect(self._center_video)
        self.btn_reset_all.clicked.connect(self._reset_all)

    def _set_custom_visible(self, visible: bool):
        for w in (self.lbl_cw, self.spin_cw, self.lbl_ch, self.spin_ch):
            w.setVisible(visible)

    def _sync_ui_from_transform(self):
        self._updating = True
        try:
            t = self._transform
            idx = self.combo_ratio.findData(t.aspect_ratio)
            if idx >= 0:
                self.combo_ratio.setCurrentIndex(idx)
            is_custom = (t.aspect_ratio == "custom")
            self._set_custom_visible(is_custom)
            self.spin_cw.setValue(int(t.canvas_w))
            self.spin_ch.setValue(int(t.canvas_h))
            self.lbl_canvas_size.setText(f"{t.canvas_w} × {t.canvas_h}")

            zoom_pct = int(round(t.video_scale * 100))
            self.slider_zoom.setValue(max(10, min(300, zoom_pct)))
            self.lbl_zoom_val.setText(f"{zoom_pct}%")

            self.spin_pos_x.setValue(round(t.pos_x))
            self.spin_pos_y.setValue(round(t.pos_y))
            self.spin_rot.setValue(round(t.rotation))
        finally:
            self._updating = False

    def _emit(self):
        if self._updating:
            return
        save_transform(self._transform)
        self.transform_changed.emit(self._transform)

    def _on_ratio_changed(self, _idx: int):
        if self._updating:
            return
        ratio = self.combo_ratio.currentData()
        self._transform.aspect_ratio = ratio
        is_custom = (ratio == "custom")
        self._set_custom_visible(is_custom)
        if not is_custom:
            w, h = get_canvas_size(ratio)
            self._transform.canvas_w = w
            self._transform.canvas_h = h
        else:
            self._transform.canvas_w = self.spin_cw.value()
            self._transform.canvas_h = self.spin_ch.value()
        self.lbl_canvas_size.setText(f"{self._transform.canvas_w} × {self._transform.canvas_h}")
        self._emit()

    def _on_custom_size_changed(self):
        if self._updating or self._transform.aspect_ratio != "custom":
            return
        self._transform.canvas_w = self.spin_cw.value()
        self._transform.canvas_h = self.spin_ch.value()
        self.lbl_canvas_size.setText(f"{self._transform.canvas_w} × {self._transform.canvas_h}")
        self._emit()

    def _on_zoom_slider_changed(self, val: int):
        if self._updating:
            return
        self.lbl_zoom_val.setText(f"{val}%")
        self._transform.video_scale = val / 100.0
        self._emit()

    def _zoom_in(self):
        self.slider_zoom.setValue(min(300, self.slider_zoom.value() + 10))

    def _zoom_out(self):
        self.slider_zoom.setValue(max(10, self.slider_zoom.value() - 10))

    def _zoom_reset(self):
        self.slider_zoom.setValue(100)

    def _on_pos_changed(self):
        if self._updating:
            return
        self._transform.pos_x = round(self.spin_pos_x.value())
        self._transform.pos_y = round(self.spin_pos_y.value())
        self._transform.rotation = round(self.spin_rot.value())
        self._emit()

    def _center_video(self):
        self._updating = True
        self.spin_pos_x.setValue(0)
        self.spin_pos_y.setValue(0)
        self._updating = False
        self._transform.pos_x = 0
        self._transform.pos_y = 0
        self._emit()

    def _on_fit_clicked(self):
        """Fit video to canvas (Zoom 100%, X=0, Y=0)."""
        self._updating = True
        self.slider_zoom.setValue(100)
        self.lbl_zoom_val.setText("100%")
        self.spin_pos_x.setValue(0)
        self.spin_pos_y.setValue(0)
        self._updating = False
        self._transform.video_scale = 1.0
        self._transform.pos_x = 0
        self._transform.pos_y = 0
        self._emit()

    def _on_fill_clicked(self):
        """Fill / Crop video inside canvas."""
        self.fill_requested.emit()

    def _reset_all(self):
        self._updating = True
        self.slider_zoom.setValue(100)
        self.lbl_zoom_val.setText("100%")
        self.spin_pos_x.setValue(0)
        self.spin_pos_y.setValue(0)
        self.spin_rot.setValue(0)
        self._updating = False
        self._transform.video_scale = 1.0
        self._transform.pos_x = 0
        self._transform.pos_y = 0
        self._transform.rotation = 0
        self._emit()

    def set_transform(self, transform: CanvasTransform):
        self._transform = transform
        self._sync_ui_from_transform()

    def set_zoom_scale(self, scale: float):
        """Set zoom scale (e.g. from Fill calculation)."""
        pct = int(round(scale * 100))
        self.slider_zoom.setValue(max(10, min(300, pct)))

    def update_pos_from_drag(self, dx: float, dy: float):
        self._transform.pos_x = float(round(self._transform.pos_x + dx))
        self._transform.pos_y = float(round(self._transform.pos_y + dy))
        self._updating = True
        self.spin_pos_x.setValue(self._transform.pos_x)
        self.spin_pos_y.setValue(self._transform.pos_y)
        self._updating = False
        self._emit()

    def update_zoom_from_scroll(self, delta: float):
        step = 5 if delta > 0 else -5
        new_val = max(10, min(300, self.slider_zoom.value() + step))
        self.slider_zoom.setValue(new_val)

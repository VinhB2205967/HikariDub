"""
Canvas Controls Widget - Hikari Dub v3.0
Provides aspect ratio selector, zoom controls, and transform panel.
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSizePolicy,
    QFrame, QDoubleSpinBox, QSpinBox, QComboBox, QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from qfluentwidgets import (
    PushButton, Slider, ComboBox, SpinBox, DoubleSpinBox as FDoubleSpinBox,
    ToolTipFilter, ToolTipPosition
)

from app.core.canvas_transform import (
    CanvasTransform, ASPECT_RATIOS, get_canvas_size,
    save_transform, load_transform
)

# ─────────────────────────────── Style constants ──────────────────────────────
_DARK_BG     = "#121620"
_PANEL_BG    = "#0F1219"
_BORDER      = "#293244"
_ACCENT      = "#22D3EE"
_TEXT        = "#F1F5F9"
_TEXT_DIM    = "#94A3B8"

_SECTION_STYLE = f"""
    color: {_ACCENT};
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 0.5px;
"""
_LABEL_STYLE = f"color: {_TEXT_DIM}; font-size: 11px;"
_VALUE_STYLE = f"color: {_TEXT}; font-size: 12px; font-weight: 600;"

_BTN_STYLE = f"""
    PushButton {{
        background-color: #191F2B;
        border: 1px solid {_BORDER};
        border-radius: 5px;
        color: {_TEXT};
        font-size: 11px;
        font-weight: 500;
        padding: 4px 8px;
    }}
    PushButton:hover {{
        background-color: #222A39;
        border: 1px solid {_ACCENT};
        color: {_ACCENT};
    }}
    PushButton:pressed {{
        background-color: #121620;
    }}
"""
_BTN_ACTIVE_STYLE = f"""
    PushButton {{
        background-color: #0E3A45;
        border: 1px solid {_ACCENT};
        border-radius: 5px;
        color: {_ACCENT};
        font-size: 11px;
        font-weight: 700;
        padding: 4px 8px;
    }}
"""

_SPINBOX_STYLE = f"""
    QDoubleSpinBox, QSpinBox, SpinBox {{
        background-color: #0F1219;
        border: 1px solid {_BORDER};
        border-radius: 4px;
        color: {_TEXT};
        font-size: 11px;
        padding: 2px 4px;
    }}
    QDoubleSpinBox:focus, QSpinBox:focus {{
        border: 1px solid {_ACCENT};
    }}
"""

_SLIDER_STYLE = f"""
    QSlider::groove:horizontal {{
        height: 3px;
        background: {_BORDER};
        border-radius: 2px;
    }}
    QSlider::handle:horizontal {{
        background: {_ACCENT};
        border: 2px solid {_ACCENT};
        width: 12px;
        height: 12px;
        margin: -5px 0;
        border-radius: 6px;
    }}
    QSlider::sub-page:horizontal {{
        background: {_ACCENT};
        border-radius: 2px;
    }}
"""

_COMBO_STYLE = f"""
    QComboBox {{
        background-color: #191F2B;
        border: 1px solid {_BORDER};
        border-radius: 5px;
        color: {_TEXT};
        font-size: 11px;
        font-weight: 500;
        padding: 3px 8px;
        min-width: 80px;
    }}
    QComboBox:hover {{
        border: 1px solid {_ACCENT};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 18px;
    }}
    QComboBox QAbstractItemView {{
        background-color: #191F2B;
        border: 1px solid {_BORDER};
        color: {_TEXT};
        selection-background-color: #222A39;
    }}
"""

SEP_STYLE = f"background: {_BORDER}; max-width: 1px; min-width: 1px;"

# ──────────────────────────────────────────────────────────────────────────────


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
    Top toolbar + side panel for aspect ratio, zoom and transform controls.

    Signals
    -------
    transform_changed(CanvasTransform)
        Emitted whenever any control changes the current transform.
    preview_zoom_changed(float)
        Emitted only when the Preview Zoom changes (does not affect export).
    fit_requested()
        User clicked "Vừa màn hình" — preview should auto-fit.
    reset_preview_zoom_requested()
        User clicked "100%" — set preview zoom to 1.0.
    """

    transform_changed = pyqtSignal(object)         # CanvasTransform
    preview_zoom_changed = pyqtSignal(float)
    fit_requested = pyqtSignal()
    reset_preview_zoom_requested = pyqtSignal()

    # ── Construction ──────────────────────────────────────────────────────────

    def __init__(self, parent=None):
        super().__init__(parent)
        self._transform = load_transform()
        self._updating = False   # re-entrancy guard

        self._build_ui()
        self._connect_signals()
        self._sync_ui_from_transform()

    def get_transform(self) -> CanvasTransform:
        return self._transform

    # ── UI build ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(6, 4, 6, 4)
        root.setSpacing(4)

        # ── Row 1: Aspect Ratio toolbar ──────────────────────────────────────
        ar_row = QHBoxLayout()
        ar_row.setSpacing(6)

        ar_lbl = _make_label("Tỷ lệ:", _SECTION_STYLE)
        ar_row.addWidget(ar_lbl)

        self.combo_ratio = QComboBox()
        self.combo_ratio.setStyleSheet(_COMBO_STYLE)
        self.combo_ratio.setFixedHeight(26)
        self.combo_ratio.setToolTip("Chọn tỷ lệ khung hình canvas xuất video")
        for ratio in ASPECT_RATIOS:
            label = "Tùy chỉnh" if ratio == "custom" else ratio
            self.combo_ratio.addItem(label, ratio)
        ar_row.addWidget(self.combo_ratio)

        # Custom W/H spinboxes (hidden unless "custom" is selected)
        self.lbl_cw = _make_label("W:")
        self.spin_cw = QSpinBox()
        self.spin_cw.setRange(100, 7680)
        self.spin_cw.setValue(1920)
        self.spin_cw.setFixedWidth(64)
        self.spin_cw.setStyleSheet(_SPINBOX_STYLE)
        self.spin_cw.setToolTip("Chiều rộng canvas (px)")

        self.lbl_ch = _make_label("H:")
        self.spin_ch = QSpinBox()
        self.spin_ch.setRange(100, 4320)
        self.spin_ch.setValue(1080)
        self.spin_ch.setFixedWidth(64)
        self.spin_ch.setStyleSheet(_SPINBOX_STYLE)
        self.spin_ch.setToolTip("Chiều cao canvas (px)")

        ar_row.addWidget(self.lbl_cw)
        ar_row.addWidget(self.spin_cw)
        ar_row.addWidget(self.lbl_ch)
        ar_row.addWidget(self.spin_ch)
        self._set_custom_visible(False)

        ar_row.addWidget(_make_separator())

        # Preview display buttons
        self.btn_fit = PushButton("⊡ Vừa màn hình")
        self.btn_fit.setStyleSheet(_BTN_STYLE)
        self.btn_fit.setFixedHeight(26)
        self.btn_fit.setToolTip("Tự động điều chỉnh preview vừa khu vực xem")

        self.btn_100 = PushButton("⊞ 100%")
        self.btn_100.setStyleSheet(_BTN_STYLE)
        self.btn_100.setFixedHeight(26)
        self.btn_100.setToolTip("Hiển thị preview ở kích thước thực (100%)")

        ar_row.addWidget(self.btn_fit)
        ar_row.addWidget(self.btn_100)
        ar_row.addStretch()

        # Canvas size indicator
        self.lbl_canvas_size = _make_label("1920 × 1080", _VALUE_STYLE)
        self.lbl_canvas_size.setToolTip("Kích thước canvas xuất video")
        ar_row.addWidget(self.lbl_canvas_size)

        root.addLayout(ar_row)

        # ── Row 2: Zoom toolbar ──────────────────────────────────────────────
        zoom_row = QHBoxLayout()
        zoom_row.setSpacing(6)

        zoom_lbl = _make_label("Preview zoom:", _SECTION_STYLE)
        zoom_row.addWidget(zoom_lbl)

        self.btn_zoom_out = PushButton("−")
        self.btn_zoom_out.setStyleSheet(_BTN_STYLE)
        self.btn_zoom_out.setFixedSize(26, 26)
        self.btn_zoom_out.setToolTip("Thu nhỏ view (−10%)")

        self.slider_zoom = QSlider(Qt.Orientation.Horizontal)
        self.slider_zoom.setRange(10, 300)
        self.slider_zoom.setValue(100)
        self.slider_zoom.setFixedWidth(160)
        self.slider_zoom.setStyleSheet(_SLIDER_STYLE)
        self.slider_zoom.setToolTip("Kéo để zoom in/out khu vực xem trước")

        self.btn_zoom_in = PushButton("+")
        self.btn_zoom_in.setStyleSheet(_BTN_STYLE)
        self.btn_zoom_in.setFixedSize(26, 26)
        self.btn_zoom_in.setToolTip("Phóng to view (+10%)")

        self.lbl_zoom_pct = _make_label("100%", _VALUE_STYLE)
        self.lbl_zoom_pct.setFixedWidth(42)

        self.btn_zoom_reset = PushButton("↺ Reset view")
        self.btn_zoom_reset.setStyleSheet(_BTN_STYLE)
        self.btn_zoom_reset.setFixedHeight(26)
        self.btn_zoom_reset.setToolTip("Đặt lại view về 100%")

        zoom_row.addWidget(self.btn_zoom_out)
        zoom_row.addWidget(self.slider_zoom)
        zoom_row.addWidget(self.btn_zoom_in)
        zoom_row.addWidget(self.lbl_zoom_pct)
        zoom_row.addWidget(self.btn_zoom_reset)
        zoom_row.addStretch()

        root.addLayout(zoom_row)

        # ── Row 3: Video transform inline panel ──────────────────────────────
        tf_row = QHBoxLayout()
        tf_row.setSpacing(8)

        tf_lbl = _make_label("Video:", _SECTION_STYLE)
        tf_row.addWidget(tf_lbl)

        # Scale %
        tf_row.addWidget(_make_label("Scale:"))
        self.spin_scale = QDoubleSpinBox()
        self.spin_scale.setRange(1.0, 500.0)
        self.spin_scale.setValue(100.0)
        self.spin_scale.setSingleStep(5.0)
        self.spin_scale.setSuffix(" %")
        self.spin_scale.setFixedWidth(80)
        self.spin_scale.setStyleSheet(_SPINBOX_STYLE)
        self.spin_scale.setToolTip("Tỷ lệ kích thước video trong canvas (ảnh hưởng xuất video)")
        tf_row.addWidget(self.spin_scale)

        tf_row.addWidget(_make_separator())

        # Position X
        tf_row.addWidget(_make_label("X:"))
        self.spin_pos_x = QDoubleSpinBox()
        self.spin_pos_x.setRange(-4000, 4000)
        self.spin_pos_x.setValue(0)
        self.spin_pos_x.setSingleStep(5.0)
        self.spin_pos_x.setSuffix(" px")
        self.spin_pos_x.setFixedWidth(86)
        self.spin_pos_x.setStyleSheet(_SPINBOX_STYLE)
        self.spin_pos_x.setToolTip("Vị trí ngang video trong canvas")
        tf_row.addWidget(self.spin_pos_x)

        # Position Y
        tf_row.addWidget(_make_label("Y:"))
        self.spin_pos_y = QDoubleSpinBox()
        self.spin_pos_y.setRange(-4000, 4000)
        self.spin_pos_y.setValue(0)
        self.spin_pos_y.setSingleStep(5.0)
        self.spin_pos_y.setSuffix(" px")
        self.spin_pos_y.setFixedWidth(86)
        self.spin_pos_y.setStyleSheet(_SPINBOX_STYLE)
        self.spin_pos_y.setToolTip("Vị trí dọc video trong canvas")
        tf_row.addWidget(self.spin_pos_y)

        tf_row.addWidget(_make_separator())

        # Rotation
        tf_row.addWidget(_make_label("Xoay:"))
        self.spin_rot = QDoubleSpinBox()
        self.spin_rot.setRange(-360, 360)
        self.spin_rot.setValue(0)
        self.spin_rot.setSingleStep(1.0)
        self.spin_rot.setSuffix(" °")
        self.spin_rot.setFixedWidth(74)
        self.spin_rot.setStyleSheet(_SPINBOX_STYLE)
        self.spin_rot.setToolTip("Góc xoay video (độ)")
        tf_row.addWidget(self.spin_rot)

        tf_row.addWidget(_make_separator())

        self.btn_center = PushButton("⊕ Căn giữa")
        self.btn_center.setStyleSheet(_BTN_STYLE)
        self.btn_center.setFixedHeight(26)
        self.btn_center.setToolTip("Đặt video về vị trí trung tâm canvas")
        tf_row.addWidget(self.btn_center)

        self.btn_reset_transform = PushButton("↺ Reset")
        self.btn_reset_transform.setStyleSheet(_BTN_STYLE)
        self.btn_reset_transform.setFixedHeight(26)
        self.btn_reset_transform.setToolTip("Đặt lại tất cả: Scale 100%, vị trí trung tâm, không xoay")
        tf_row.addWidget(self.btn_reset_transform)

        tf_row.addStretch()
        root.addLayout(tf_row)

        # ── Container styling ─────────────────────────────────────────────────
        self.setStyleSheet(f"""
            CanvasControlsWidget {{
                background-color: {_PANEL_BG};
                border-bottom: 1px solid {_BORDER};
            }}
            QLabel {{
                color: {_TEXT_DIM};
                font-size: 11px;
            }}
        """)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    # ── Signal wiring ─────────────────────────────────────────────────────────

    def _connect_signals(self):
        self.combo_ratio.currentIndexChanged.connect(self._on_ratio_changed)
        self.spin_cw.valueChanged.connect(self._on_custom_size_changed)
        self.spin_ch.valueChanged.connect(self._on_custom_size_changed)

        self.btn_fit.clicked.connect(self.fit_requested.emit)
        self.btn_100.clicked.connect(self.reset_preview_zoom_requested.emit)

        self.slider_zoom.valueChanged.connect(self._on_slider_zoom)
        self.btn_zoom_in.clicked.connect(self._zoom_in)
        self.btn_zoom_out.clicked.connect(self._zoom_out)
        self.btn_zoom_reset.clicked.connect(self._zoom_reset)

        self.spin_scale.valueChanged.connect(self._on_transform_changed)
        self.spin_pos_x.valueChanged.connect(self._on_transform_changed)
        self.spin_pos_y.valueChanged.connect(self._on_transform_changed)
        self.spin_rot.valueChanged.connect(self._on_transform_changed)

        self.btn_center.clicked.connect(self._center_video)
        self.btn_reset_transform.clicked.connect(self._reset_transform)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _set_custom_visible(self, visible: bool):
        for w in (self.lbl_cw, self.spin_cw, self.lbl_ch, self.spin_ch):
            w.setVisible(visible)

    def _sync_ui_from_transform(self):
        """Populate all controls from self._transform without triggering signals."""
        self._updating = True
        try:
            t = self._transform
            # Ratio combo
            ratio_index = self.combo_ratio.findData(t.aspect_ratio)
            if ratio_index >= 0:
                self.combo_ratio.setCurrentIndex(ratio_index)
            is_custom = (t.aspect_ratio == "custom")
            self._set_custom_visible(is_custom)
            self.spin_cw.setValue(t.canvas_w)
            self.spin_ch.setValue(t.canvas_h)
            self.lbl_canvas_size.setText(f"{t.canvas_w} × {t.canvas_h}")

            # Zoom slider
            pz = int(t.preview_zoom * 100)
            self.slider_zoom.setValue(max(10, min(300, pz)))
            self.lbl_zoom_pct.setText(f"{pz}%")

            # Transform spinboxes
            self.spin_scale.setValue(t.video_scale * 100.0)
            self.spin_pos_x.setValue(t.pos_x)
            self.spin_pos_y.setValue(t.pos_y)
            self.spin_rot.setValue(t.rotation)
        finally:
            self._updating = False

    def _emit_transform(self):
        if self._updating:
            return
        save_transform(self._transform)
        self.transform_changed.emit(self._transform)

    # ── Slots ─────────────────────────────────────────────────────────────────

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
        self._emit_transform()

    def _on_custom_size_changed(self):
        if self._updating or self._transform.aspect_ratio != "custom":
            return
        self._transform.canvas_w = self.spin_cw.value()
        self._transform.canvas_h = self.spin_ch.value()
        self.lbl_canvas_size.setText(f"{self._transform.canvas_w} × {self._transform.canvas_h}")
        self._emit_transform()

    def _on_transform_changed(self):
        if self._updating:
            return
        self._transform.video_scale = self.spin_scale.value() / 100.0
        self._transform.pos_x = self.spin_pos_x.value()
        self._transform.pos_y = self.spin_pos_y.value()
        self._transform.rotation = self.spin_rot.value()
        self._emit_transform()

    def _on_slider_zoom(self, val: int):
        if self._updating:
            return
        pct = val
        self.lbl_zoom_pct.setText(f"{pct}%")
        self._transform.preview_zoom = pct / 100.0
        save_transform(self._transform)
        self.preview_zoom_changed.emit(self._transform.preview_zoom)

    def _zoom_in(self):
        new_val = min(300, self.slider_zoom.value() + 10)
        self.slider_zoom.setValue(new_val)

    def _zoom_out(self):
        new_val = max(10, self.slider_zoom.value() - 10)
        self.slider_zoom.setValue(new_val)

    def _zoom_reset(self):
        self.slider_zoom.setValue(100)

    def _center_video(self):
        self._updating = True
        self.spin_pos_x.setValue(0)
        self.spin_pos_y.setValue(0)
        self._updating = False
        self._on_transform_changed()

    def _reset_transform(self):
        self._updating = True
        self.spin_scale.setValue(100.0)
        self.spin_pos_x.setValue(0)
        self.spin_pos_y.setValue(0)
        self.spin_rot.setValue(0)
        self._updating = False
        self._on_transform_changed()

    # ── Public API ────────────────────────────────────────────────────────────

    def set_transform(self, transform: CanvasTransform):
        """Update all controls from an external CanvasTransform."""
        self._transform = transform
        self._sync_ui_from_transform()

    def update_pos_from_drag(self, dx: float, dy: float):
        """Called by CanvasPreviewWidget when user drags the video."""
        self._transform.pos_x += dx
        self._transform.pos_y += dy
        self._updating = True
        self.spin_pos_x.setValue(self._transform.pos_x)
        self.spin_pos_y.setValue(self._transform.pos_y)
        self._updating = False
        self._emit_transform()

    def update_preview_zoom_from_scroll(self, delta: float):
        """Called by CanvasPreviewWidget on mouse wheel."""
        step = 10 if delta > 0 else -10
        new_val = max(10, min(300, self.slider_zoom.value() + step))
        self.slider_zoom.setValue(new_val)

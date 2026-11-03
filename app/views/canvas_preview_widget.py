"""
Canvas Preview Widget - Hikari Dub v3.0
Professional video preview area with:
  - Dark canvas background with visible frame border
  - Preview zoom (visual only, does NOT affect export)
  - Pan/drag video to change position (pos_x/pos_y, DOES affect export)
  - Mouse wheel scroll to zoom preview
  - Center indicator crosshair
"""

from __future__ import annotations
import math
from PyQt6.QtWidgets import QWidget, QLabel, QSizePolicy, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt, QPointF, QRectF, pyqtSignal, QSize
from PyQt6.QtGui import (
    QPainter, QPixmap, QColor, QPen, QBrush, QTransform,
    QPainterPath, QCursor, QFont
)

from app.core.canvas_transform import CanvasTransform


_BG_COLOR       = QColor("#080A0F")
_CANVAS_BG      = QColor("#0a0a0a")
_BORDER_COLOR   = QColor("#22D3EE")
_GRID_COLOR     = QColor("#1A2030")
_CENTER_COLOR   = QColor("#22D3EE")
_TEXT_COLOR     = QColor("#475569")
_SHADOW_COLOR   = QColor(0, 0, 0, 100)


class CanvasPreviewWidget(QWidget):
    """
    Renders a video frame pixmap inside a virtual canvas.

    Signals
    -------
    drag_moved(dx, dy)
        Emitted during video drag with pixel delta — controls widget uses this
        to update pos_x/pos_y in the transform.
    scroll_zoomed(delta)
        Emitted on mouse wheel with +1 or -1 — controls widget maps to zoom %.
    """

    drag_moved   = pyqtSignal(float, float)
    scroll_zoomed = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._transform   = CanvasTransform()
        self._pixmap      = QPixmap()          # current video frame
        self._drag_start  = None               # QPointF | None
        self._preview_zoom = 1.0               # purely visual
        self._pan_x = 0.0                      # viewport pan
        self._pan_y = 0.0
        self._fit_mode = True                  # start in Fit mode

        self.setMinimumSize(360, 240)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(f"background-color: #080A0F; border-radius: 8px;")
        self.setMouseTracking(True)
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))

    # ── Public API ─────────────────────────────────────────────────────────────

    def set_frame(self, pixmap: QPixmap):
        """Update the displayed video frame."""
        self._pixmap = pixmap
        self.update()

    def apply_transform(self, transform: CanvasTransform):
        """Apply a new CanvasTransform — updates display only, not export."""
        self._transform = transform
        self.update()

    def set_preview_zoom(self, zoom: float):
        """Set preview zoom (1.0 = 100%). Does NOT affect export."""
        self._preview_zoom = max(0.1, min(3.0, zoom))
        self._fit_mode = False
        self.update()

    def fit_to_screen(self):
        """Auto-fit canvas to available preview area."""
        self._fit_mode = True
        self._pan_x = 0.0
        self._pan_y = 0.0
        self.update()

    def reset_to_100(self):
        """Show canvas at 100% zoom, centered."""
        self._preview_zoom = 1.0
        self._fit_mode = False
        self._pan_x = 0.0
        self._pan_y = 0.0
        self.update()

    # ── Mouse events ──────────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = QPointF(event.position())
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._drag_start is not None:
            pos = QPointF(event.position())
            raw_dx = pos.x() - self._drag_start.x()
            raw_dy = pos.y() - self._drag_start.y()
            # Convert screen delta to canvas-space delta (inverse of preview_zoom)
            eff_zoom = self._effective_zoom()
            dx = raw_dx / eff_zoom
            dy = raw_dy / eff_zoom
            self._drag_start = pos
            self.drag_moved.emit(dx, dy)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = None
            self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.scroll_zoomed.emit(1.0 if delta > 0 else -1.0)
        event.accept()

    # ── Painting ──────────────────────────────────────────────────────────────

    def _effective_zoom(self) -> float:
        if self._fit_mode:
            cw = self._transform.canvas_w or 1920
            ch = self._transform.canvas_h or 1080
            w  = self.width()  or 1
            h  = self.height() or 1
            return min(w / cw, h / ch)
        return self._preview_zoom

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        W = self.width()
        H = self.height()

        # Fill widget background
        painter.fillRect(0, 0, W, H, _BG_COLOR)

        t       = self._transform
        cw      = t.canvas_w
        ch      = t.canvas_h
        zoom    = self._effective_zoom()

        # Displayed canvas dimensions
        disp_cw = cw * zoom
        disp_ch = ch * zoom

        # Canvas origin (top-left), centered in widget + viewport pan
        origin_x = (W - disp_cw) / 2 + self._pan_x
        origin_y = (H - disp_ch) / 2 + self._pan_y

        # ── Draw canvas background ────────────────────────────────────────────
        painter.fillRect(
            int(origin_x), int(origin_y), int(disp_cw), int(disp_ch),
            _CANVAS_BG
        )

        # ── Draw subtle grid lines inside canvas ──────────────────────────────
        pen_grid = QPen(_GRID_COLOR, 1, Qt.PenStyle.SolidLine)
        painter.setPen(pen_grid)
        grid_step = 80  # logical pixels
        x = origin_x
        while x <= origin_x + disp_cw:
            painter.drawLine(int(x), int(origin_y), int(x), int(origin_y + disp_ch))
            x += grid_step * zoom
        y = origin_y
        while y <= origin_y + disp_ch:
            painter.drawLine(int(origin_x), int(y), int(origin_x + disp_cw), int(y))
            y += grid_step * zoom

        # ── Draw video frame ─────────────────────────────────────────────────
        if not self._pixmap.isNull():
            pm_w = self._pixmap.width()
            pm_h = self._pixmap.height()

            # Fit video into canvas
            fit_ratio = min(cw / pm_w, ch / pm_h) if (pm_w > 0 and pm_h > 0) else 1.0
            vscale    = t.video_scale
            rot_deg   = t.rotation

            # Scaled video size in canvas coords
            vid_cw = pm_w * fit_ratio * vscale
            vid_ch = pm_h * fit_ratio * vscale

            # Center of video in canvas coords
            vid_cx = cw / 2 + t.pos_x
            vid_cy = ch / 2 + t.pos_y

            # Map to screen coords
            screen_cx = origin_x + vid_cx * zoom
            screen_cy = origin_y + vid_cy * zoom
            screen_vw = vid_cw * zoom
            screen_vh = vid_ch * zoom

            # Clip to canvas bounds
            canvas_clip = QPainterPath()
            canvas_clip.addRect(QRectF(origin_x, origin_y, disp_cw, disp_ch))
            painter.setClipPath(canvas_clip)

            painter.save()
            painter.translate(screen_cx, screen_cy)
            if abs(rot_deg) > 0.01:
                painter.rotate(rot_deg)

            dst_rect = QRectF(-screen_vw / 2, -screen_vh / 2, screen_vw, screen_vh)
            painter.drawPixmap(dst_rect.toRect(), self._pixmap)
            painter.restore()
            painter.setClipping(False)

        else:
            # No frame yet — show placeholder text
            painter.setPen(QPen(_TEXT_COLOR))
            font = QFont("Arial", 12)
            painter.setFont(font)
            painter.drawText(
                QRectF(origin_x, origin_y, disp_cw, disp_ch),
                Qt.AlignmentFlag.AlignCenter,
                "Chưa có video\nChọn video nguồn để xem trước"
            )

        # ── Draw canvas border ────────────────────────────────────────────────
        pen_border = QPen(_BORDER_COLOR, 1.5, Qt.PenStyle.SolidLine)
        painter.setPen(pen_border)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(int(origin_x), int(origin_y), int(disp_cw), int(disp_ch))

        # ── Draw center crosshair (small) ─────────────────────────────────────
        cx_s = int(origin_x + disp_cw / 2)
        cy_s = int(origin_y + disp_ch / 2)
        cross_size = 10
        pen_cross = QPen(_CENTER_COLOR, 1, Qt.PenStyle.DotLine)
        painter.setPen(pen_cross)
        painter.drawLine(cx_s - cross_size, cy_s, cx_s + cross_size, cy_s)
        painter.drawLine(cx_s, cy_s - cross_size, cx_s, cy_s + cross_size)

        # ── HUD: zoom info ────────────────────────────────────────────────────
        painter.setPen(QPen(_TEXT_COLOR))
        font_hud = QFont("Consolas", 9)
        painter.setFont(font_hud)
        zoom_pct  = int(zoom * 100)
        ratio_lbl = t.aspect_ratio.upper() if t.aspect_ratio != "custom" else "CUSTOM"
        hud_text  = f" {ratio_lbl}  {cw}×{ch}  view:{zoom_pct}%  scale:{int(t.video_scale*100)}% "
        painter.drawText(int(origin_x) + 6, int(origin_y) + 14, hud_text)

        painter.end()


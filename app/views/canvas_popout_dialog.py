"""
Canvas Popout Dialog for HD multi-monitor preview.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from app.common.design_system import Colors


class CanvasPopoutDialog(QDialog):
    """Floating HD preview dialog."""

    def __init__(self, home_interface=None, parent=None):
        super().__init__(parent or home_interface)
        self.home_interface = home_interface
        self.setWindowTitle("Hikari Tsukimi — Xem Trước HD")
        self.resize(960, 580)
        self.setStyleSheet(f"background: {Colors.BG_DEEP}; color: {Colors.TEXT_PRIMARY};")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        self.lbl_info = QLabel("Cửa sổ xem trước Canvas HD")
        self.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_info, 1)

"""
Style Dialog Module for subtitle & watermark preview settings.
"""

from PyQt6.QtWidgets import QDialog, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt


class PreviewWidgetWM(QWidget):
    """Watermark preview widget."""

    def __init__(self, dialog=None, parent=None):
        super().__init__(parent)
        self.dialog = dialog
        self.text = "PRODUCED BY HIKARI TSUKIMI"
        lay = QVBoxLayout(self)
        self.label = QLabel(self.text, self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self.label)


class StyleDialog(QDialog):
    """Subtitle style configuration dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cài đặt kiểu phụ đề")
        self.resize(480, 320)
        lay = QVBoxLayout(self)
        self.preview = PreviewWidgetWM(self, self)
        lay.addWidget(self.preview)

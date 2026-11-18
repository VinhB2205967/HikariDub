"""
Report & Support Interface Module - Hikari Tsukimi Studio.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from qfluentwidgets import PrimaryPushButton, LineEdit, PlainTextEdit, InfoBar, InfoBarPosition, FluentIcon as FIF
from app.common.design_system import Colors


class ReportInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("reportInterface")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        lbl = QLabel("💬 Trung Tâm Hỗ Trợ & Báo Lỗi", self)
        lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 16px; font-weight: 700;")
        lay.addWidget(lbl)

        self.txt_subject = LineEdit(self)
        self.txt_subject.setPlaceholderText("Tiêu đề vấn đề hoặc góp ý...")
        lay.addWidget(self.txt_subject)

        self.txt_body = PlainTextEdit(self)
        self.txt_body.setPlaceholderText("Mô tả chi tiết lỗi hoặc đề xuất tính năng...")
        lay.addWidget(self.txt_body, 1)

        self.btn_send = PrimaryPushButton(FIF.SEND, "Lưu Phản Hồi", self)
        self.btn_send.clicked.connect(self._save_report)
        lay.addWidget(self.btn_send)

    def _save_report(self):
        InfoBar.success("Cảm ơn bạn", "Phản hồi của bạn đã được ghi nhận.", parent=self, position=InfoBarPosition.TOP)
        self.txt_subject.clear()
        self.txt_body.clear()

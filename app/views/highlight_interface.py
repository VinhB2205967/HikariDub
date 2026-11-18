"""
Highlight Interface Module - Hikari Tsukimi Studio.
"""

import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog
from qfluentwidgets import PrimaryPushButton, PushButton, LineEdit, SpinBox, PlainTextEdit, InfoBar, InfoBarPosition, FluentIcon as FIF
from app.common.design_system import Colors


class HighlightInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("highlightInterface")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        lbl = QLabel("✨ Cắt Highlight Tự Động từ Video Dài", self)
        lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 16px; font-weight: 700;")
        lay.addWidget(lbl)

        row = QHBoxLayout()
        self.video_input = LineEdit(self)
        self.video_input.setPlaceholderText("Chọn file video nguồn (.mp4, .mkv, .mov)...")
        btn_pick = PushButton(FIF.FOLDER, "Chọn Video", self)
        btn_pick.clicked.connect(self._pick_video)
        row.addWidget(self.video_input, 1)
        row.addWidget(btn_pick)
        lay.addLayout(row)

        dur_row = QHBoxLayout()
        dur_row.addWidget(QLabel("Thời lượng mỗi clip (giây):", self))
        self.spin_dur = SpinBox(self)
        self.spin_dur.setRange(10, 300)
        self.spin_dur.setValue(45)
        dur_row.addWidget(self.spin_dur)
        dur_row.addStretch(1)
        lay.addLayout(dur_row)

        self.btn_run = PrimaryPushButton(FIF.CUT, "Trích Xuất Highlight", self)
        self.btn_run.clicked.connect(self._run_highlight)
        lay.addWidget(self.btn_run)

        self.log_box = PlainTextEdit(self)
        self.log_box.setReadOnly(True)
        self.log_box.setPlaceholderText("Nhật ký xử lý highlight...")
        lay.addWidget(self.log_box, 1)

    def _pick_video(self):
        p, _ = QFileDialog.getOpenFileName(self, "Chọn Video", "", "Video Files (*.mp4 *.mkv *.mov *.avi)")
        if p:
            self.video_input.setText(p)

    def _run_highlight(self):
        vp = self.video_input.text().strip()
        if not vp or not os.path.exists(vp):
            InfoBar.warning("Thiếu video", "Vui lòng chọn file video hợp lệ.", parent=self, position=InfoBarPosition.TOP)
            return
        self.log_box.appendPlainText(f"Đã nhận video: {vp} (thời lượng clip {self.spin_dur.value()}s)")
        InfoBar.info("Sẵn sàng", "Đã thêm tác vụ cắt highlight.", parent=self, position=InfoBarPosition.TOP)

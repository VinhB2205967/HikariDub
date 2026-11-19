"""
Video Splitter Interface Module - Hikari Tsukimi Studio.
"""

import os
import subprocess
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog
from qfluentwidgets import PrimaryPushButton, PushButton, LineEdit, SpinBox, PlainTextEdit, InfoBar, InfoBarPosition, FluentIcon as FIF
from app.common.design_system import Colors


class VideoSplitterInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("videoSplitterInterface")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        lbl = QLabel("✂️ Chia Tập Video Thông Minh", self)
        lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 16px; font-weight: 700;")
        lay.addWidget(lbl)

        row = QHBoxLayout()
        self.video_input = LineEdit(self)
        self.video_input.setPlaceholderText("Chọn file video cần chia nhỏ...")
        btn_pick = PushButton(FIF.FOLDER, "Chọn Video", self)
        btn_pick.clicked.connect(self._pick_video)
        row.addWidget(self.video_input, 1)
        row.addWidget(btn_pick)
        lay.addLayout(row)

        seg_row = QHBoxLayout()
        seg_row.setSpacing(10)
        lbl_seg = QLabel("Thời lượng mỗi phần (giây):", self)
        lbl_seg.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 13px;")
        seg_row.addWidget(lbl_seg)
        self.spin_seg = SpinBox(self)
        self.spin_seg.setRange(5, 3600)
        self.spin_seg.setValue(60)
        self.spin_seg.setMinimumWidth(145)
        seg_row.addWidget(self.spin_seg)
        seg_row.addStretch(1)
        lay.addLayout(seg_row)

        self.btn_split = PrimaryPushButton(FIF.CUT, "Bắt Đầu Chia Video", self)
        self.btn_split.clicked.connect(self._split_video)
        lay.addWidget(self.btn_split)

        self.log_box = PlainTextEdit(self)
        self.log_box.setReadOnly(True)
        lay.addWidget(self.log_box, 1)

    def _pick_video(self):
        p, _ = QFileDialog.getOpenFileName(self, "Chọn Video", "", "Video Files (*.mp4 *.mkv *.mov *.avi)")
        if p:
            self.video_input.setText(p)

    def _split_video(self):
        vp = self.video_input.text().strip()
        if not vp or not os.path.exists(vp):
            InfoBar.warning("Thiếu video", "Vui lòng chọn file video hợp lệ.", parent=self, position=InfoBarPosition.TOP)
            return
        try:
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            out_dir = os.path.join(os.path.dirname(vp), "split_output")
            os.makedirs(out_dir, exist_ok=True)
            base = os.path.splitext(os.path.basename(vp))[0]
            pattern = os.path.join(out_dir, f"{base}_part_%03d.mp4")
            subprocess.run(
                [ffmpeg_exe, "-y", "-i", vp, "-c", "copy", "-map", "0", "-segment_time", str(self.spin_seg.value()), "-f", "segment", "-reset_timestamps", "1", pattern],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            self.log_box.appendPlainText(f"Đã chia xong vào: {out_dir}")
            InfoBar.success("Hoàn tất", f"Đã lưu các phần tại {out_dir}", parent=self, position=InfoBarPosition.TOP)
        except Exception as e:
            InfoBar.error("Lỗi chia video", str(e), parent=self, position=InfoBarPosition.TOP)

"""
Video Merger Interface Module - Hikari Tsukimi Studio.
"""

import os
import subprocess
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog
from qfluentwidgets import PrimaryPushButton, PushButton, PlainTextEdit, InfoBar, InfoBarPosition, FluentIcon as FIF
from app.common.design_system import Colors


class VideoMergerInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("videoMergerInterface")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        lbl = QLabel("🔗 Ghép Nối Nhiều Video", self)
        lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 16px; font-weight: 700;")
        lay.addWidget(lbl)

        row = QHBoxLayout()
        row.setSpacing(8)
        btn_add = PushButton(FIF.ADD, "Chọn Danh Sách Video", self)
        btn_add.clicked.connect(self._pick_videos)
        btn_clear = PushButton(FIF.DELETE, "Xóa Danh Sách", self)
        btn_clear.clicked.connect(lambda: self.txt_files.clear())
        self.btn_merge = PrimaryPushButton(FIF.MOVIE, "Ghép Video", self)
        self.btn_merge.clicked.connect(self._merge_videos)
        row.addWidget(btn_add)
        row.addWidget(btn_clear)
        row.addWidget(self.btn_merge)
        row.addStretch(1)
        lay.addLayout(row)

        self.txt_files = PlainTextEdit(self)
        self.txt_files.setPlaceholderText("Danh sách đường dẫn video cần ghép (mỗi dòng 1 file)...")
        lay.addWidget(self.txt_files, 1)

    def _pick_videos(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Chọn các file video", "", "Video Files (*.mp4 *.mkv *.mov *.avi)")
        if files:
            self.txt_files.setPlainText("\n".join(files))

    def _merge_videos(self):
        files = [f.strip() for f in self.txt_files.toPlainText().splitlines() if f.strip() and os.path.exists(f.strip())]
        if len(files) < 2:
            InfoBar.warning("Thiếu video", "Cần ít nhất 2 file video để ghép.", parent=self, position=InfoBarPosition.TOP)
            return
        try:
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            out_dir = os.path.dirname(files[0])
            list_txt = os.path.join(out_dir, "_merge_list.txt")
            out_mp4 = os.path.join(out_dir, "HikariDub_Merged.mp4")
            with open(list_txt, "w", encoding="utf-8") as f:
                for p in files:
                    safe = p.replace("'", "'\\''")
                    f.write(f"file '{safe}'\n")
            subprocess.run(
                [ffmpeg_exe, "-y", "-f", "concat", "-safe", "0", "-i", list_txt, "-c", "copy", out_mp4],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            InfoBar.success("Hoàn tất", f"Đã ghép xong: {out_mp4}", parent=self, position=InfoBarPosition.TOP)
        except Exception as e:
            InfoBar.error("Lỗi ghép video", str(e), parent=self, position=InfoBarPosition.TOP)

"""
Douyin Interface Module - Pure Python Edition (Hikari Tsukimi Studio).
Downloads videos from Douyin, TikTok, Bilibili, YouTube via yt-dlp.
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog
)
from PyQt6.QtCore import Qt
from qfluentwidgets import (
    PrimaryPushButton, PushButton, LineEdit, PlainTextEdit,
    ProgressBar, InfoBar, InfoBarPosition, FluentIcon as FIF
)

from app.common.design_system import Colors
from app.common.config_manager import get_config, set_config
from app.core.douyin_core import DouyinDownloadWorker


class DouyinInterface(QWidget):
    """Multi-platform video downloader interface."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("douyinInterface")
        self._worker = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        lbl_title = QLabel("Tải Video Đa Nền Tảng (Douyin / TikTok / Bilibili / YouTube)")
        lbl_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 16px; font-weight: 700;")
        layout.addWidget(lbl_title)

        # Save folder row
        dir_row = QHBoxLayout()
        self.dir_input = LineEdit(self)
        default_dir = get_config("output_dir", os.path.join(os.getcwd(), "Output"))
        self.dir_input.setText(default_dir)
        self.dir_input.setPlaceholderText("Thư mục lưu video tải về...")
        self.btn_browse = PushButton(FIF.FOLDER, "Chọn Thư Mục", self)
        self.btn_browse.clicked.connect(self._browse_dir)
        dir_row.addWidget(self.dir_input, 1)
        dir_row.addWidget(self.btn_browse)
        layout.addLayout(dir_row)

        # URLs input
        lbl_urls = QLabel("Danh sách URL video (mỗi dòng một link):")
        lbl_urls.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px;")
        layout.addWidget(lbl_urls)

        self.url_input = PlainTextEdit(self)
        self.url_input.setPlaceholderText("Dán link Douyin, TikTok, Bilibili hoặc YouTube vào đây...")
        self.url_input.setMinimumHeight(140)
        layout.addWidget(self.url_input)

        # Action row
        act_row = QHBoxLayout()
        self.btn_download = PrimaryPushButton(FIF.DOWNLOAD, "Bắt Đầu Tải Video", self)
        self.btn_download.clicked.connect(self._start_download)
        self.btn_open_dir = PushButton(FIF.FOLDER_ADD, "Mở Thư Mục Lưu", self)
        self.btn_open_dir.clicked.connect(self._open_dir)
        act_row.addWidget(self.btn_download)
        act_row.addWidget(self.btn_open_dir)
        act_row.addStretch(1)
        layout.addLayout(act_row)

        self.progress_bar = ProgressBar(self)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.log_output = PlainTextEdit(self)
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Nhật ký tải video...")
        layout.addWidget(self.log_output, 1)

    def _browse_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục lưu", self.dir_input.text().strip())
        if folder:
            self.dir_input.setText(folder)
            set_config("output_dir", folder)

    def _open_dir(self):
        d = self.dir_input.text().strip()
        if d:
            os.makedirs(d, exist_ok=True)
            os.startfile(d)

    def _start_download(self):
        urls = [u.strip() for u in self.url_input.toPlainText().splitlines() if u.strip()]
        if not urls:
            InfoBar.warning("Thiếu link", "Vui lòng nhập ít nhất 1 đường dẫn video.", parent=self, position=InfoBarPosition.TOP)
            return
        out_dir = self.dir_input.text().strip() or os.path.join(os.getcwd(), "Output")
        self.btn_download.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_output.clear()

        self._worker = DouyinDownloadWorker(urls, out_dir, parent=self)
        self._worker.progress.connect(self.progress_bar.setValue)
        self._worker.log.connect(self.log_output.appendPlainText)
        self._worker.finished.connect(self.on_download_finished)
        self._worker.error.connect(self._on_download_error)
        self._worker.start()

    def on_download_finished(self, fpath):
        self.btn_download.setEnabled(True)
        self.progress_bar.setValue(100)
        self.log_output.appendPlainText(f"Hoàn tất: {fpath}")
        InfoBar.success("Thành công", "Đã tải xong video!", parent=self, position=InfoBarPosition.TOP)

    def _on_download_error(self, err):
        self.btn_download.setEnabled(True)
        self.log_output.appendPlainText(f"[LỖI] {err}")
        InfoBar.error("Lỗi tải video", err, parent=self, position=InfoBarPosition.TOP)

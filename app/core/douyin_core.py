"""
Douyin Core Module - Pure Python Edition (Hikari Tsukimi Studio).
Downloads videos from Douyin, TikTok, Bilibili, YouTube, etc. using yt-dlp
with 'HikariDub_' filename prefix.
"""

import os
from PyQt6.QtCore import QThread, pyqtSignal


class DouyinDownloadWorker(QThread):
    """Background worker to download one or more video URLs via yt-dlp."""

    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, videos, output_dir: str, parent=None, options=None):
        super().__init__(parent)
        if isinstance(videos, str):
            self.videos = [v.strip() for v in videos.splitlines() if v.strip()]
        else:
            self.videos = list(videos or [])
        self.output_dir = output_dir or os.path.join(os.getcwd(), "Downloads")
        self.options = options or {}

    def run(self):
        try:
            import yt_dlp
        except ImportError as e:
            self.error.emit(f"Thiếu thư viện yt-dlp: {e}")
            return

        os.makedirs(self.output_dir, exist_ok=True)
        last_file = ""
        total = max(1, len(self.videos))

        for idx, url in enumerate(self.videos, 1):
            if not url:
                continue
            self.log.emit(f"Đang tải ({idx}/{total}): {url}")

            def _hook(d):
                if d.get("status") == "downloading":
                    total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                    downloaded = d.get("downloaded_bytes") or 0
                    if total_bytes > 0:
                        pct = int(((idx - 1) + downloaded / total_bytes) / total * 100)
                        self.progress.emit(min(99, max(0, pct)))
                elif d.get("status") == "finished":
                    nonlocal last_file
                    last_file = d.get("filename", last_file)

            ydl_opts = {
                "outtmpl": os.path.join(self.output_dir, "HikariDub_%(title).60s_%(id)s.%(ext)s"),
                "format": "bestvideo+bestaudio/best",
                "merge_output_format": "mp4",
                "progress_hooks": [_hook],
                "quiet": True,
                "no_warnings": True,
            }
            if isinstance(self.options, dict):
                ydl_opts.update(self.options)

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    if info:
                        prepared = ydl.prepare_filename(info)
                        mp4_cand = os.path.splitext(prepared)[0] + ".mp4"
                        last_file = mp4_cand if os.path.exists(mp4_cand) else prepared
            except Exception as e:
                self.error.emit(f"Lỗi tải {url}: {e}")
                return

        self.progress.emit(100)
        self.finished.emit(last_file)


HikariDownloadWorker = DouyinDownloadWorker

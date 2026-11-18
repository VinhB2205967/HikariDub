"""
Background QThread workers for Hikari Tsukimi Studio.
Includes TranslateWorker, TranscribeWorker, TTSWorker, and RenderWorker.
"""

import os
import threading
from PyQt6.QtCore import QThread, pyqtSignal


class TranslateWorker(QThread):
    """Runs subtitle translation in a background thread."""

    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished_srt = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(
        self,
        srt_path: str,
        workspace_dir: str,
        api_keys=None,
        prompt_style: str = "Mặc định",
        custom_prompt: str = "",
        target_lang: str = "Tiếng Việt",
        parent=None,
    ):
        super().__init__(parent)
        self.srt_path = srt_path
        self.workspace_dir = workspace_dir
        self.api_keys = api_keys or []
        self.prompt_style = prompt_style or "Mặc định"
        self.custom_prompt = custom_prompt or ""
        self.target_lang = target_lang or "Tiếng Việt"
        self._cancel_event = threading.Event()

    def cancel(self):
        self._cancel_event.set()

    def run(self):
        try:
            from app.core.ai_translator import translate_logic

            self.progress.emit(10)
            out_srt = translate_logic(
                self.srt_path,
                self.api_keys,
                lambda m: self.log.emit(str(m)),
                self._cancel_event,
                self.workspace_dir,
                prompt_style=self.prompt_style,
                custom_prompt_text=self.custom_prompt,
                target_lang=self.target_lang,
            )
            self.progress.emit(100)
            if out_srt and os.path.exists(out_srt):
                self.finished_srt.emit(out_srt)
            else:
                self.error.emit("Không tạo được file phụ đề đã dịch.")
        except Exception as e:
            self.error.emit(str(e))

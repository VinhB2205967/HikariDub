"""
Base HomeInterface Module - Pure Python Edition (Hikari Tsukimi Studio).
Provides the 3-column AI Dubbing Studio workspace without any .pyc dependency.
"""

import os
import threading
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QStackedWidget, QListWidget, QFileDialog,
    QDialog, QPlainTextEdit as QtPlainTextEdit, QPushButton
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QRectF
from PyQt6.QtGui import QImage
from qfluentwidgets import (
    PrimaryPushButton, PushButton, ComboBox, LineEdit, PlainTextEdit,
    ProgressBar, Pivot, InfoBar, InfoBarPosition, FluentIcon as FIF
)

from app.common.design_system import Colors
from app.common.config_manager import get_config, set_config


class _TranscribeWorker(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished_srt = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, video_path: str, workspace_dir: str, model_size: str = "small", parent=None):
        super().__init__(parent)
        self.video_path = video_path
        self.workspace_dir = workspace_dir
        self.model_size = model_size
        self._cancel = threading.Event()

    def cancel(self):
        self._cancel.set()

    def run(self):
        try:
            import pysrt
            from faster_whisper import WhisperModel
            import torch

            os.makedirs(self.workspace_dir, exist_ok=True)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"
            self.log.emit(f"Đang nạp Whisper ({self.model_size}, {device})...")
            self.progress.emit(15)

            model = WhisperModel(self.model_size, device=device, compute_type=compute_type)
            self.log.emit("Đang bóc băng lời thoại...")
            segments, _ = model.transcribe(self.video_path, vad_filter=True)

            subs = pysrt.SubRipFile()
            for idx, seg in enumerate(segments, 1):
                if self._cancel.is_set():
                    self.error.emit("Đã hủy bóc băng.")
                    return
                start = pysrt.SubRipTime(seconds=seg.start)
                end = pysrt.SubRipTime(seconds=seg.end)
                subs.append(pysrt.SubRipItem(idx, start, end, seg.text.strip()))

            from app.core.video_utils import get_safe_basename
            base = get_safe_basename(self.video_path)
            data_dir = os.path.join(self.workspace_dir, base, "Data")
            os.makedirs(data_dir, exist_ok=True)
            out_srt = os.path.join(data_dir, "temp_original.srt")
            subs.save(out_srt, encoding="utf-8")
            self.progress.emit(100)
            self.finished_srt.emit(out_srt)
        except Exception as e:
            self.error.emit(str(e))


class _TTSWorker(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished_audio = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, srt_path: str, workspace_dir: str, voice_model: str = "banmai", parent=None):
        super().__init__(parent)
        self.srt_path = srt_path
        self.workspace_dir = workspace_dir
        self.voice_model = voice_model
        self._cancel = threading.Event()

    def cancel(self):
        self._cancel.set()

    def run(self):
        try:
            from app.core.audio_generator import generate_audio_logic
            temp_files = []
            out_wav = generate_audio_logic(
                self.srt_path, "", self.voice_model,
                lambda m: self.log.emit(str(m)),
                self._cancel, temp_files, self.workspace_dir, "Tiếng Việt", 1.35
            )
            self.progress.emit(100)
            if out_wav and os.path.exists(out_wav):
                self.finished_audio.emit(out_wav)
            else:
                self.error.emit("Không tạo được file âm thanh lồng tiếng.")
        except Exception as e:
            self.error.emit(str(e))


class _RenderWorker(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished_video = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, video_path: str, srt_path: str, audio_path: str, workspace_dir: str, parent=None):
        super().__init__(parent)
        self.video_path = video_path
        self.srt_path = srt_path
        self.audio_path = audio_path
        self.workspace_dir = workspace_dir
        self._cancel = threading.Event()

    def cancel(self):
        self._cancel.set()

    def run(self):
        try:
            from app.core.video_renderer import render_logic
            out_mp4 = render_logic(
                self.video_path, self.srt_path, self.audio_path, self.workspace_dir,
                lambda m: self.log.emit(str(m)), self._cancel, "premium", None
            )
            self.progress.emit(100)
            if out_mp4 and os.path.exists(out_mp4):
                self.finished_video.emit(out_mp4)
            else:
                self.error.emit("Không xuất được video.")
        except Exception as e:
            self.error.emit(str(e))


class VideoCanvasWidget(QWidget):
    """Custom video preview canvas compatible with canvas_transform & home_interface patches."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_image = None
        self.masks_rel = []
        self.config = {}
        self.logo_rel = None
        self.sub_rel = None
        self._canvas_transform = None

    def setImage(self, img):
        self.current_image = img
        self.update()

    def _getVideoRect(self):
        return (0.0, 0.0, float(self.width()), float(self.height()))

    def get_video_rect(self):
        return self._getVideoRect()

    def _getMaskRect(self, m):
        vx, vy, vw, vh = self._getVideoRect()
        return QRectF(vx + float(m[0]) * vw, vy + float(m[1]) * vh, float(m[2]) * vw, float(m[3]) * vh)

    def saveConfig(self):
        pass


SrtListWidget = QListWidget


class SrtItemWidget(QWidget):
    """Subtitle item widget."""

    def __init__(self, index: int = 0, start: str = "", end: str = "", text: str = "", parent=None):
        super().__init__(parent)
        self.index = index
        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 4, 6, 4)
        self.lbl_time = QLabel(f"[{index}] {start} -> {end}", self)
        self.lbl_text = QLabel(text, self)
        self.lbl_text.setWordWrap(True)
        lay.addWidget(self.lbl_time)
        lay.addWidget(self.lbl_text)


class HomeInterface(QWidget):
    """Pure-Python 3-column Studio Workspace."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("homeInterface")
        self.license_status = "premium"
        self._video_paths = []
        self.selected_videos = []
        self._orig_srt_path = ""
        self._trans_srt_path = ""
        self._audio_path = ""
        self._workers = []
        self._auto_running = False

        root = QHBoxLayout(self)
        self.hBoxLayout = root
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(12)

        # ── Column 1: Controls ──
        self.col1_widget = QFrame(self)
        self.col1_widget.setMinimumWidth(330)
        self.col1_widget.setMaximumWidth(390)
        col1_outer = QVBoxLayout(self.col1_widget)
        col1_outer.setContentsMargins(0, 0, 0, 0)

        self.col1_scroll = QScrollArea(self.col1_widget)
        self.col1_scroll.setWidgetResizable(True)
        self.col1_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        self.col1_container = QWidget()
        self.col1_layout = QVBoxLayout(self.col1_container)
        self.col1_layout.setContentsMargins(12, 12, 12, 12)
        self.col1_layout.setSpacing(9)

        # Index 0 MUST be header label (home_interface.py styles itemAt(0))
        self.lbl_col1_header = QLabel("✦ CẤU HÌNH DỰ ÁN & GIỌNG ĐỌC AI", self.col1_container)
        self.col1_layout.addWidget(self.lbl_col1_header)

        # Video & Output selection
        self.btn_select_video = PrimaryPushButton(FIF.VIDEO, "Chọn Video Nguồn...", self.col1_container)
        self.btn_select_video.clicked.connect(self._onSelectVideo)
        self.col1_layout.addWidget(self.btn_select_video)

        self.video_combo = ComboBox(self.col1_container)
        self.video_combo.currentIndexChanged.connect(self._onVideoChanged)
        self.col1_layout.addWidget(self.video_combo)

        out_row = QHBoxLayout()
        self.line_output_path = LineEdit(self.col1_container)
        self.line_output_path.setText(get_config("output_dir", os.path.join(os.getcwd(), "Output")))
        self.btn_select_output = PushButton(FIF.FOLDER, "Lưu...", self.col1_container)
        self.btn_select_output.clicked.connect(self._onSelectOutput)
        out_row.addWidget(self.line_output_path, 1)
        out_row.addWidget(self.btn_select_output)
        self.col1_layout.addLayout(out_row)

        # Whisper Model & TTS Voice selectors
        lbl_stt = QLabel("Mô hình bóc băng (Whisper STT):", self.col1_container)
        lbl_stt.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        self.col1_layout.addWidget(lbl_stt)
        self.combo_whisper = ComboBox(self.col1_container)
        for lbl_w, val_w in [
            ("Tiny (Siêu tốc)", "tiny"),
            ("Base (Nhanh)", "base"),
            ("Small (Cân bằng - Khuyên dùng)", "small"),
            ("Medium (Chính xác cao)", "medium"),
            ("Large-v3 (Cao nhất)", "large-v3"),
        ]:
            self.combo_whisper.addItem(lbl_w, userData=val_w)
        saved_w = get_config("whisper_model", "small")
        for idx_w in range(self.combo_whisper.count()):
            if self.combo_whisper.itemData(idx_w) == saved_w:
                self.combo_whisper.setCurrentIndex(idx_w)
                break
        self.combo_whisper.currentIndexChanged.connect(
            lambda i: set_config("whisper_model", self.combo_whisper.itemData(i) or "small")
        )
        self.col1_layout.addWidget(self.combo_whisper)

        lbl_voice = QLabel("Giọng đọc AI (Piper Local & TikTok SessionID):", self.col1_container)
        lbl_voice.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        self.col1_layout.addWidget(lbl_voice)
        self.combo_voice = ComboBox(self.col1_container)
        for lbl_v, val_v in [
            ("Ban Mai (Nữ - Local Offline)", "piper:banmai"),
            ("Mạnh Dũng (Nam - Local Offline)", "piper:manhdung"),
            ("Chiêu Thanh (Nữ - Local Offline)", "piper:chieuthanh"),
            ("Lạc Phi (Nữ - Local Offline)", "piper:lacphi"),
            ("Ngọc Huyền (Nữ - Local Offline)", "piper:ngochuyen"),
            ("Vais1000 (Nữ tự nhiên - Local Offline)", "piper:vais1000"),
            ("TikTok VN - Nhân Vật Nữ 01 (SessionID)", "tiktok:BV074_streaming"),
            ("TikTok VN - Nhân Vật Nam 01 (SessionID)", "tiktok:BV075_streaming"),
            ("TikTok US - Jessie Nữ (SessionID)", "tiktok:en_us_002"),
            ("TikTok US - Joey Nam (SessionID)", "tiktok:en_us_006"),
            ("TikTok US - Professor (SessionID)", "tiktok:en_us_007"),
            ("TikTok US - Chris (SessionID)", "tiktok:en_us_009"),
            ("TikTok UK - Narrator (SessionID)", "tiktok:en_uk_001"),
            ("TikTok US - Ghostface (SessionID)", "tiktok:en_us_ghostface"),
            ("TikTok US - C3PO (SessionID)", "tiktok:en_us_c3po"),
            ("TikTok US - Stitch (SessionID)", "tiktok:en_us_stitch"),
            ("TikTok US - Stormtrooper (SessionID)", "tiktok:en_us_stormtrooper"),
            ("TikTok US - Rocket (SessionID)", "tiktok:en_us_rocket"),
            ("TikTok CN - Nữ 01 (SessionID)", "tiktok:BV001_streaming"),
            ("TikTok CN - Nam 01 (SessionID)", "tiktok:BV002_streaming"),
            ("TikTok JP - Nữ 01 (SessionID)", "tiktok:jp_001"),
            ("TikTok JP - Nam 01 (SessionID)", "tiktok:jp_006"),
            ("TikTok KR - Nữ 01 (SessionID)", "tiktok:kr_002"),
            ("TikTok KR - Nam 01 (SessionID)", "tiktok:kr_003"),
        ]:
            self.combo_voice.addItem(lbl_v, userData=val_v)
        saved_v = get_config("tts_voice", "piper:banmai")
        if saved_v and ":" not in saved_v:
            saved_v = f"piper:{saved_v}"
        for idx_v in range(self.combo_voice.count()):
            if self.combo_voice.itemData(idx_v) == saved_v:
                self.combo_voice.setCurrentIndex(idx_v)
                break
        self.combo_voice.currentIndexChanged.connect(
            lambda i: set_config("tts_voice", self.combo_voice.itemData(i) or "piper:banmai")
        )
        self.col1_layout.addWidget(self.combo_voice)

        self.line_tiktok_session = LineEdit(self.col1_container)
        self.line_tiktok_session.setPlaceholderText("TikTok Session ID (chỉ cần nếu dùng giọng TikTok)...")
        self.line_tiktok_session.setText(get_config("tiktok_session_id", "") or "")
        self.line_tiktok_session.textChanged.connect(
            lambda txt: set_config("tiktok_session_id", txt.strip())
        )
        self.col1_layout.addWidget(self.line_tiktok_session)

        # Translation settings
        lbl_lang = QLabel("Ngôn ngữ dịch & Phong cách:", self.col1_container)
        lbl_lang.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
        self.col1_layout.addWidget(lbl_lang)

        self.combo_target_lang = ComboBox(self.col1_container)
        self.combo_target_lang.addItems(["Tiếng Việt", "English", "中文", "日本語", "한국어"])
        self.col1_layout.addWidget(self.combo_target_lang)

        self.combo_prompt = ComboBox(self.col1_container)
        self.combo_prompt.addItem("Mặc định", userData="Mặc định")
        self.col1_layout.addWidget(self.combo_prompt)

        self.text_custom_prompt = PlainTextEdit(self.col1_container)
        self.text_custom_prompt.setPlaceholderText("Ghi chú phong cách dịch (tùy chọn)...")
        self.text_custom_prompt.setMaximumHeight(65)
        self.col1_layout.addWidget(self.text_custom_prompt)

        # Pipeline step buttons
        self.btn_step1 = PushButton(FIF.MICROPHONE, "1. Bóc Băng (STT)", self.col1_container)
        self.btn_step1.clicked.connect(self._onStep1Clicked)
        self.col1_layout.addWidget(self.btn_step1)

        self.btn_step2 = PushButton(FIF.LANGUAGE, "2. Dịch Kịch Bản", self.col1_container)
        self.btn_step2.clicked.connect(self._onTranslateClicked)
        self.col1_layout.addWidget(self.btn_step2)

        self.btn_step3 = PushButton(FIF.VOLUME, "3. Tạo Giọng Đọc", self.col1_container)
        self.btn_step3.clicked.connect(self._onVoiceClicked)
        self.col1_layout.addWidget(self.btn_step3)

        self.btn_step4 = PrimaryPushButton(FIF.MOVIE, "4. Render Video", self.col1_container)
        self.btn_step4.clicked.connect(self._onStep4Clicked)
        self.col1_layout.addWidget(self.btn_step4)

        self.run_group = QFrame(self.col1_container)
        full_row = QHBoxLayout(self.run_group)
        full_row.setContentsMargins(0, 0, 0, 0)
        self.btn_start_full = QPushButton("▶ Chạy Tự Động", self.run_group)
        self.btn_start_full.clicked.connect(self._onStartFullClicked)
        self.btn_cancel = PushButton(FIF.CANCEL, "Hủy", self.run_group)
        self.btn_cancel.clicked.connect(self._onCancelClicked)
        full_row.addWidget(self.btn_start_full, 1)
        full_row.addWidget(self.btn_cancel)
        self.col1_layout.addWidget(self.run_group)

        # Secondary utility buttons
        util_row = QHBoxLayout()
        self.btn_paste_transcript = PushButton("Dán Kịch Bản", self.col1_container)
        self.btn_paste_transcript.clicked.connect(self._onPasteTranscript)
        self.btn_upload_transcript = PushButton("Nạp SRT", self.col1_container)
        self.btn_upload_transcript.clicked.connect(self._onUploadSRT)
        util_row.addWidget(self.btn_paste_transcript)
        util_row.addWidget(self.btn_upload_transcript)
        self.col1_layout.addLayout(util_row)

        ov_row = QHBoxLayout()
        self.btn_add_mask = PushButton("Thêm Vùng Mờ", self.col1_container)
        self.btn_add_mask.clicked.connect(self._onAddMaskClicked)
        self.btn_add_logo = PushButton("Xóa Vùng Mờ", self.col1_container)
        self.btn_add_logo.clicked.connect(self._onClearMaskClicked)
        self.btn_add_bg_frame = PushButton("Khung Nền", self.col1_container)
        self.btn_remove_item = PushButton("Xóa", self.col1_container)
        self.btn_style = PushButton("Kiểu Chữ", self.col1_container)
        self.btn_apply_all = PushButton("Áp Dụng", self.col1_container)
        ov_row.addWidget(self.btn_add_mask)
        ov_row.addWidget(self.btn_add_logo)
        self.col1_layout.addLayout(ov_row)

        self.line_wm = LineEdit(self.col1_container)
        self.line_wm.setPlaceholderText("Watermark (tùy chọn)...")
        self.line_wm.hide()
        self.btn_add_bg_frame.hide()
        self.btn_remove_item.hide()
        self.btn_style.hide()
        self.btn_apply_all.hide()

        self.col1_layout.addStretch(1)
        self.col1_scroll.setWidget(self.col1_container)
        col1_outer.addWidget(self.col1_scroll)
        root.addWidget(self.col1_widget)

        # ── Column 2: Preview & Log ──
        self.col2_widget = QFrame(self)
        self.col2_layout = QVBoxLayout(self.col2_widget)
        self.col2_layout.setContentsMargins(12, 12, 12, 12)
        self.col2_layout.setSpacing(10)

        # Index 0 MUST be header label (home_interface.py styles itemAt(0))
        self.lbl_col2_header = QLabel("🎬 VIDEO ĐẦU VÀO & KHÔNG GIAN XEM TRƯỚC", self.col2_widget)
        self.col2_layout.addWidget(self.lbl_col2_header)

        self.video_frame = QFrame(self.col2_widget)
        self.video_frame.setMinimumHeight(320)
        self.video_frame.setStyleSheet("QFrame { background: #0B0F1A; border: 1px solid #1E293B; border-radius: 10px; }")
        vf_lay = QVBoxLayout(self.video_frame)
        vf_lay.setContentsMargins(0, 0, 0, 0)
        self.video_canvas = VideoCanvasWidget(self.video_frame)
        vf_lay.addWidget(self.video_canvas, 1)
        self.col2_layout.addWidget(self.video_frame, 3)

        self.row2_widget = QWidget(self.col2_widget)
        self.row2_layout = QHBoxLayout(self.row2_widget)
        self.row2_layout.setContentsMargins(0, 0, 0, 0)
        self.col2_layout.addWidget(self.row2_widget)

        self.progress_bar = ProgressBar(self.col2_widget)
        self.progress_bar.setValue(0)
        self.col2_layout.addWidget(self.progress_bar)

        self.log_text_edit = PlainTextEdit(self.col2_widget)
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setPlaceholderText("Nhật ký xử lý AI...")
        self.col2_layout.addWidget(self.log_text_edit, 1)
        root.addWidget(self.col2_widget, 2)

        # ── Column 3: Subtitles ──
        self.col3_widget = QFrame(self)
        self.col3_widget.setMinimumWidth(280)
        self.col3_widget.setMaximumWidth(360)
        self.col3_layout = QVBoxLayout(self.col3_widget)
        self.col3_layout.setContentsMargins(12, 12, 12, 12)
        self.col3_layout.setSpacing(8)

        # Index 0 MUST be header label (home_interface.py styles itemAt(0))
        self.lbl_col3_header = QLabel("📝 TRÌNH BIÊN TẬP PHỤ ĐỀ AI", self.col3_widget)
        self.col3_layout.addWidget(self.lbl_col3_header)

        self.srt_pivot = Pivot(self.col3_widget)
        self.srt_stacked_widget = QStackedWidget(self.col3_widget)
        self.srt_orig_list = QListWidget(self.col3_widget)
        self.srt_trans_list = QListWidget(self.col3_widget)
        self.srt_stacked_widget.addWidget(self.srt_orig_list)
        self.srt_stacked_widget.addWidget(self.srt_trans_list)
        self.srt_pivot.addItem("orig", "Phụ Đề Gốc", lambda: self.srt_stacked_widget.setCurrentWidget(self.srt_orig_list))
        self.srt_pivot.addItem("trans", "Phụ Đề Dịch", lambda: self.srt_stacked_widget.setCurrentWidget(self.srt_trans_list))
        self.srt_pivot.setCurrentItem("orig")
        self.col3_layout.addWidget(self.srt_pivot)
        self.col3_layout.addWidget(self.srt_stacked_widget, 1)

        srt_btn_row = QHBoxLayout()
        self.btn_replace_all = PushButton("Thay Thế", self.col3_widget)
        self.btn_save_srt = PushButton(FIF.SAVE, "Lưu SRT", self.col3_widget)
        self.btn_save_srt.clicked.connect(self._onSaveSrtClicked)
        srt_btn_row.addWidget(self.btn_replace_all)
        srt_btn_row.addWidget(self.btn_save_srt)
        self.col3_layout.addLayout(srt_btn_row)
        root.addWidget(self.col3_widget)

    def _appendLog(self, msg: str):
        if hasattr(self, "log_text_edit"):
            self.log_text_edit.appendPlainText(str(msg))

    def get_active_video_path(self) -> str:
        idx = self.video_combo.currentIndex()
        if 0 <= idx < len(self._video_paths):
            return self._video_paths[idx]
        return ""

    def get_active_workspace(self) -> str:
        out = self.line_output_path.text().strip() or os.path.join(os.getcwd(), "Output")
        os.makedirs(out, exist_ok=True)
        return out

    def get_current_srt_path(self) -> str:
        return self._trans_srt_path or self._orig_srt_path

    def _preview_video_frame(self, video_path: str):
        if not video_path or not os.path.exists(video_path):
            return
        try:
            import subprocess
            import tempfile
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
            tmp_png = os.path.join(tempfile.gettempdir(), "hikari_preview_frame.png")
            subprocess.run(
                [ffmpeg_exe, "-y", "-ss", "0.5", "-i", video_path, "-vframes", "1", tmp_png],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False
            )
            if os.path.exists(tmp_png):
                qimg = QImage(tmp_png)
                if not qimg.isNull():
                    self.video_canvas.setImage(qimg)
                    return
        except Exception as e:
            self._appendLog(f"Không xem trước được khung hình: {e}")

    def _onVideoChanged(self, idx: int):
        vp = self.get_active_video_path()
        if vp:
            self._preview_video_frame(vp)

    def _onSelectVideo(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Chọn Video", "", "Video Files (*.mp4 *.mkv *.mov *.avi)")
        if files:
            self._video_paths = files
            self.selected_videos = files
            self.video_combo.clear()
            for f in files:
                self.video_combo.addItem(os.path.basename(f), userData=f)
            self._preview_video_frame(files[0])
            self._appendLog(f"Đã nạp {len(files)} video.")

    def _onSelectOutput(self):
        folder = QFileDialog.getExistingDirectory(self, "Chọn Thư Mục Lưu", self.line_output_path.text().strip())
        if folder:
            self.line_output_path.setText(folder)
            set_config("output_dir", folder)

    def _onUploadSRT(self):
        p, _ = QFileDialog.getOpenFileName(self, "Chọn File SRT", "", "Subtitle Files (*.srt)")
        if p:
            self._orig_srt_path = p
            self._load_srt_to_list(p, self.srt_orig_list)
            self._appendLog(f"Đã nạp phụ đề: {p}")

    def _onPasteTranscript(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Dán Kịch Bản / Văn Bản")
        dlg.resize(520, 360)
        lay = QVBoxLayout(dlg)
        txt = QtPlainTextEdit(dlg)
        txt.setPlaceholderText("Dán nội dung kịch bản (mỗi dòng 1 câu)...")
        lay.addWidget(txt)
        btn_ok = QPushButton("Tạo Phụ Đề SRT", dlg)
        btn_ok.clicked.connect(dlg.accept)
        lay.addWidget(btn_ok)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            lines = [ln.strip() for ln in txt.toPlainText().splitlines() if ln.strip()]
            if lines:
                import pysrt
                subs = pysrt.SubRipFile()
                for i, line in enumerate(lines, 1):
                    subs.append(pysrt.SubRipItem(
                        i, pysrt.SubRipTime(seconds=(i - 1) * 3), pysrt.SubRipTime(seconds=i * 3), line
                    ))
                out_srt = os.path.join(self.get_active_workspace(), "pasted_orig.srt")
                subs.save(out_srt, encoding="utf-8")
                self._orig_srt_path = out_srt
                self._load_srt_to_list(out_srt, self.srt_orig_list)
                self._appendLog(f"Đã tạo SRT từ kịch bản dán: {out_srt}")

    def _onSaveSrtClicked(self):
        cur = self.get_current_srt_path()
        if not cur or not os.path.exists(cur):
            InfoBar.warning("Chưa có SRT", "Chưa có file phụ đề để lưu.", parent=self, position=InfoBarPosition.TOP)
            return
        dest, _ = QFileDialog.getSaveFileName(self, "Lưu File SRT", cur, "Subtitle Files (*.srt)")
        if dest:
            import shutil
            shutil.copy2(cur, dest)
            InfoBar.success("Đã lưu", f"Đã lưu SRT tới: {dest}", parent=self, position=InfoBarPosition.TOP)

    def _onAddMaskClicked(self):
        masks = list(getattr(self.video_canvas, "masks_rel", []) or [])
        masks.append([0.1, 0.78, 0.8, 0.14])
        self.video_canvas.masks_rel = masks
        self.video_canvas.update()
        cfg = dict(get_config("video_overlay", {}) or {})
        cfg["mask_logos"] = masks
        set_config("video_overlay", cfg)
        self._appendLog(f"Đã thêm vùng làm mờ ({len(masks)} vùng).")

    def _onClearMaskClicked(self):
        self.video_canvas.masks_rel = []
        self.video_canvas.update()
        cfg = dict(get_config("video_overlay", {}) or {})
        cfg["mask_logos"] = []
        set_config("video_overlay", cfg)
        self._appendLog("Đã xóa tất cả vùng làm mờ.")

    def _load_srt_to_list(self, srt_path: str, lw: QListWidget):
        lw.clear()
        try:
            import pysrt
            subs = pysrt.open(srt_path, encoding="utf-8")
            for s in subs:
                lw.addItem(f"[{s.index}] {s.start} -> {s.end}\n{s.text}")
        except Exception as e:
            self._appendLog(f"Lỗi đọc SRT: {e}")

    def _onStartFullClicked(self):
        vp = self.get_active_video_path()
        if not vp or not os.path.exists(vp):
            InfoBar.warning("Thiếu video", "Vui lòng chọn video nguồn trước.", parent=self, position=InfoBarPosition.TOP)
            return
        self._auto_running = True
        self._appendLog("▶ Bắt đầu quy trình tự động: STT → Dịch → TTS → Render...")
        self._onStep1Clicked()

    def _onCancelClicked(self):
        self._auto_running = False
        for w in self._workers:
            if hasattr(w, "cancel"):
                w.cancel()
        self._appendLog("Đã gửi yêu cầu hủy tác vụ.")

    def _onStep1Clicked(self):
        vp = self.get_active_video_path()
        if not vp or not os.path.exists(vp):
            InfoBar.warning("Thiếu video", "Vui lòng chọn video nguồn trước.", parent=self, position=InfoBarPosition.TOP)
            return
        w = _TranscribeWorker(vp, self.get_active_workspace(), get_config("whisper_model", "small"), self)
        w.progress.connect(self.progress_bar.setValue)
        w.log.connect(self._appendLog)
        w.finished_srt.connect(self._onTranscribeFinished)
        w.error.connect(self._onTranscribeError)
        self._workers.append(w)
        w.start()

    def _onTranscribeFinished(self, srt_path: str):
        self._orig_srt_path = srt_path
        self._load_srt_to_list(srt_path, self.srt_orig_list)
        self._appendLog(f"Bóc băng hoàn tất: {srt_path}")
        if self._auto_running:
            self._onTranslateClicked()
        else:
            InfoBar.success("Hoàn tất", "Đã bóc băng phụ đề xong!", parent=self, position=InfoBarPosition.TOP)

    def _onTranscribeError(self, err: str):
        self._auto_running = False
        self._setButtonsEnabled(True)
        self._appendLog(f"[LỖI] {err}")
        InfoBar.error("Lỗi", str(err), parent=self, position=InfoBarPosition.TOP)

    def _onTranslateClicked(self):
        pass  # Overridden by home_interface.py patch

    def _onTranslateFinished(self, srt_path: str):
        self._setButtonsEnabled(True)
        self._trans_srt_path = srt_path
        self._load_srt_to_list(srt_path, self.srt_trans_list)
        self.srt_pivot.setCurrentItem("trans")
        self.srt_stacked_widget.setCurrentWidget(self.srt_trans_list)
        self._appendLog(f"Dịch hoàn tất: {srt_path}")
        if self._auto_running:
            self._onVoiceClicked()
        else:
            InfoBar.success("Hoàn tất", "Đã dịch phụ đề xong!", parent=self, position=InfoBarPosition.TOP)

    def _onVoiceClicked(self):
        srt = self.get_current_srt_path()
        if not srt or not os.path.exists(srt):
            InfoBar.warning("Thiếu phụ đề", "Vui lòng bóc băng hoặc nạp file SRT trước.", parent=self, position=InfoBarPosition.TOP)
            return
        w = _TTSWorker(srt, self.get_active_workspace(), get_config("tts_voice", "banmai"), self)
        w.progress.connect(self.progress_bar.setValue)
        w.log.connect(self._appendLog)
        w.finished_audio.connect(self._onVoiceFinished)
        w.error.connect(self._onTranscribeError)
        self._workers.append(w)
        w.start()

    def _onVoiceFinished(self, wav_path: str):
        self._audio_path = wav_path
        self._appendLog(f"Tạo giọng đọc hoàn tất: {wav_path}")
        if self._auto_running:
            self._onStep4Clicked()
        else:
            InfoBar.success("Hoàn tất", "Đã tạo giọng đọc xong!", parent=self, position=InfoBarPosition.TOP)

    def _onStep4Clicked(self):
        vp = self.get_active_video_path()
        if not vp or not os.path.exists(vp):
            InfoBar.warning("Thiếu video", "Vui lòng chọn video nguồn trước.", parent=self, position=InfoBarPosition.TOP)
            return
        w = _RenderWorker(vp, self.get_current_srt_path(), self._audio_path, self.get_active_workspace(), self)
        w.progress.connect(self.progress_bar.setValue)
        w.log.connect(self._appendLog)
        w.finished_video.connect(self._onRenderFinished)
        w.error.connect(self._onTranscribeError)
        self._workers.append(w)
        w.start()

    def _onRenderFinished(self, mp4_path: str):
        self._auto_running = False
        self._appendLog(f"Xuất video hoàn tất: {mp4_path}")
        InfoBar.success("Thành công", f"Đã xuất video: {os.path.basename(mp4_path)}", parent=self, position=InfoBarPosition.TOP)

    def setVerticalScrollBarPolicy(self, *args, **kwargs):
        pass

    def _setButtonsEnabled(self, enabled: bool):
        for btn in [self.btn_step1, self.btn_step2, self.btn_step3, self.btn_step4, self.btn_start_full]:
            btn.setEnabled(bool(enabled))

    def _on_canvas_transform_changed(self, *args, **kwargs):
        pass

    def _on_fill_requested(self, *args, **kwargs):
        pass

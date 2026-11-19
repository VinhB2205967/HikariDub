"""
Base HomeInterface Module - Pure Python Edition (Hikari Tsukimi Studio).
Provides the 3-column AI Dubbing Studio workspace without any .pyc dependency.
"""

import os
import threading
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QStackedWidget, QListWidget, QFileDialog,
    QDialog, QPlainTextEdit as QtPlainTextEdit, QPushButton, QSlider
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QRectF, QUrl
from PyQt6.QtGui import QImage
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput, QVideoSink
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
    """Custom video preview canvas with draggable/resizable Mask, Logo, and Watermark overlays."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_image = None
        self.masks_rel = []
        self.config = {}
        self.logo_rel = None
        self.logo_path = ""
        self.logo_image = None
        self.wm_rel = [0.04, 0.04, 0.34, 0.09]
        self.watermark_text = ""
        self.sub_rel = None
        self._canvas_transform = None
        self._drag_target = None  # ('mask', idx, mode) | ('logo', 0, mode) | ('wm', 0, mode)
        self._drag_start = None
        self._drag_orig_rect = None
        self.setMouseTracking(True)

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

    def _hit_test_overlay(self, px: float, py: float):
        vx, vy, vw, vh = self._getVideoRect()
        if vw <= 1 or vh <= 1:
            return None
        handle = 14.0
        # Check masks (top-most first)
        for i in range(len(self.masks_rel) - 1, -1, -1):
            r = self._getMaskRect(self.masks_rel[i])
            if abs(px - r.right()) <= handle and abs(py - r.bottom()) <= handle:
                return ("mask", i, "resize", list(self.masks_rel[i]))
            if r.contains(px, py):
                return ("mask", i, "move", list(self.masks_rel[i]))
        # Check logo
        if self.logo_rel and self.logo_image is not None:
            r = self._getMaskRect(self.logo_rel)
            if abs(px - r.right()) <= handle and abs(py - r.bottom()) <= handle:
                return ("logo", 0, "resize", list(self.logo_rel))
            if r.contains(px, py):
                return ("logo", 0, "move", list(self.logo_rel))
        # Check watermark
        if self.watermark_text and self.wm_rel:
            r = self._getMaskRect(self.wm_rel)
            if abs(px - r.right()) <= handle and abs(py - r.bottom()) <= handle:
                return ("wm", 0, "resize", list(self.wm_rel))
            if r.contains(px, py):
                return ("wm", 0, "move", list(self.wm_rel))
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position()
            hit = self._hit_test_overlay(pos.x(), pos.y())
            if hit:
                self._drag_target = (hit[0], hit[1], hit[2])
                self._drag_start = (pos.x(), pos.y())
                self._drag_orig_rect = hit[3]
                event.accept()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pos = event.position()
        if self._drag_target and self._drag_start and self._drag_orig_rect:
            vx, vy, vw, vh = self._getVideoRect()
            if vw > 1 and vh > 1:
                dx = (pos.x() - self._drag_start[0]) / vw
                dy = (pos.y() - self._drag_start[1]) / vh
                ox, oy, ow, oh = self._drag_orig_rect
                kind, idx, mode = self._drag_target
                if mode == "move":
                    nx = max(0.0, min(1.0 - ow, ox + dx))
                    ny = max(0.0, min(1.0 - oh, oy + dy))
                    new_rect = [nx, ny, ow, oh]
                else:
                    nw = max(0.05, min(1.0 - ox, ow + dx))
                    nh = max(0.04, min(1.0 - oy, oh + dy))
                    new_rect = [ox, oy, nw, nh]
                if kind == "mask" and 0 <= idx < len(self.masks_rel):
                    self.masks_rel[idx] = new_rect
                elif kind == "logo":
                    self.logo_rel = new_rect
                elif kind == "wm":
                    self.wm_rel = new_rect
                self.update()
                event.accept()
                return
        else:
            hit = self._hit_test_overlay(pos.x(), pos.y())
            if hit:
                self.setCursor(Qt.CursorShape.SizeFDiagCursor if hit[2] == "resize" else Qt.CursorShape.SizeAllCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._drag_target:
            self._drag_target = None
            self._drag_start = None
            self._drag_orig_rect = None
            self.saveConfig()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def saveConfig(self):
        try:
            cfg = dict(get_config("video_overlay", {}) or {})
            cfg["mask_logos"] = list(self.masks_rel or [])
            cfg["logo_path"] = self.logo_path or ""
            cfg["logo_rel"] = list(self.logo_rel) if self.logo_rel else None
            cfg["watermark_text"] = self.watermark_text or ""
            cfg["wm_rel"] = list(self.wm_rel) if self.wm_rel else None
            set_config("video_overlay", cfg)
        except Exception:
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
        self.video_combo.addItem("Chưa có video nào được chọn", userData="")
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
        self.combo_voice.currentIndexChanged.connect(self._onVoiceSelectionChanged)
        self.col1_layout.addWidget(self.combo_voice)

        # Conditional TikTok Session ID container (visible only when a TikTok voice is selected)
        self.tiktok_session_box = QWidget(self.col1_container)
        tk_box_lay = QVBoxLayout(self.tiktok_session_box)
        tk_box_lay.setContentsMargins(0, 2, 0, 2)
        tk_box_lay.setSpacing(4)
        lbl_tk_sid = QLabel("TikTok Session ID (bắt buộc cho giọng TikTok):", self.tiktok_session_box)
        lbl_tk_sid.setStyleSheet("color: #38BDF8; font-size: 11px; font-weight: 600;")
        tk_box_lay.addWidget(lbl_tk_sid)
        self.line_tiktok_session = LineEdit(self.tiktok_session_box)
        self.line_tiktok_session.setPlaceholderText("Dán cookie sessionid TikTok vào đây...")
        self.line_tiktok_session.setText(get_config("tiktok_session_id", "") or "")
        self.line_tiktok_session.textChanged.connect(
            lambda txt: set_config("tiktok_session_id", txt.strip())
        )
        tk_box_lay.addWidget(self.line_tiktok_session)
        self.col1_layout.addWidget(self.tiktok_session_box)
        self._update_tiktok_session_visibility()

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
        full_col = QVBoxLayout(self.run_group)
        full_col.setContentsMargins(8, 8, 8, 8)
        full_col.setSpacing(6)
        from PyQt6.QtWidgets import QSizePolicy
        self.btn_start_full = QPushButton("▶ BẮT ĐẦU XỬ LÝ TOÀN BỘ (TỰ ĐỘNG)", self.run_group)
        self.btn_start_full.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_start_full.setMinimumHeight(38)
        self.btn_start_full.setToolTip("BẮT ĐẦU XỬ LÝ TOÀN BỘ (TỰ ĐỘNG) — Chạy lần lượt STT → Dịch → TTS → Xuất Video")
        self.btn_start_full.clicked.connect(self._onStartFullClicked)
        self.btn_cancel = PushButton("⏹ HỦY TIẾN TRÌNH", self.run_group)
        self.btn_cancel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_cancel.setMinimumHeight(32)
        self.btn_cancel.setToolTip("HỦY TIẾN TRÌNH — Dừng tác vụ đang chạy")
        self.btn_cancel.clicked.connect(self._onCancelClicked)
        full_col.addWidget(self.btn_start_full)
        full_col.addWidget(self.btn_cancel)
        self.col1_layout.addWidget(self.run_group)

        # Hidden compatibility controls expected by home_interface.py patches
        self.btn_add_bg_frame = PushButton("Khung Nền", self.col1_container)
        self.btn_remove_item = PushButton("Xóa", self.col1_container)
        self.btn_style = PushButton("Kiểu Chữ", self.col1_container)
        self.btn_apply_all = PushButton("Áp Dụng", self.col1_container)
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

        # Video Playback Controls Bar (Play/Pause, Seek, Timecode)
        self._init_media_player()
        play_bar = QFrame(self.col2_widget)
        play_bar.setStyleSheet("QFrame { background: #11182B; border: 1px solid #1E2942; border-radius: 8px; }")
        pb_lay = QHBoxLayout(play_bar)
        pb_lay.setContentsMargins(8, 4, 8, 4)
        pb_lay.setSpacing(8)
        self.btn_play_pause = PushButton(FIF.PLAY, "Phát", play_bar)
        self.btn_play_pause.setFixedHeight(28)
        self.btn_play_pause.clicked.connect(self._toggle_play_pause)
        self.lbl_time_cur = QLabel("00:00", play_bar)
        self.lbl_time_cur.setStyleSheet("color: #CBD5E1; font-size: 11px; border: none;")
        self.slider_seek = QSlider(Qt.Orientation.Horizontal, play_bar)
        self.slider_seek.setRange(0, 0)
        self.slider_seek.sliderMoved.connect(lambda pos: self.media_player.setPosition(pos))
        self.lbl_time_dur = QLabel("00:00", play_bar)
        self.lbl_time_dur.setStyleSheet("color: #94A3B8; font-size: 11px; border: none;")
        pb_lay.addWidget(self.btn_play_pause)
        pb_lay.addWidget(self.lbl_time_cur)
        pb_lay.addWidget(self.slider_seek, 1)
        pb_lay.addWidget(self.lbl_time_dur)
        self.col2_layout.addWidget(play_bar)

        # Quick tools bar right under the video preview frame
        self.row2_widget = QWidget(self.col2_widget)
        self.row2_layout = QHBoxLayout(self.row2_widget)
        self.row2_layout.setContentsMargins(4, 4, 4, 4)
        self.row2_layout.setSpacing(8)

        self.btn_paste_transcript = PushButton("Dán Kịch Bản", self.row2_widget)
        self.btn_paste_transcript.setToolTip("Dán kịch bản văn bản để tạo SRT")
        self.btn_paste_transcript.clicked.connect(self._onPasteTranscript)
        self.btn_upload_transcript = PushButton("Nạp SRT", self.row2_widget)
        self.btn_upload_transcript.setToolTip("Chọn file phụ đề .srt từ máy")
        self.btn_upload_transcript.clicked.connect(self._onUploadSRT)
        self.btn_add_mask = PushButton("Vùng Che", self.row2_widget)
        self.btn_add_mask.setToolTip("Thêm vùng làm mờ (kéo thả & chỉnh kích thước trực tiếp trên khung video)")
        self.btn_add_mask.clicked.connect(self._onAddMaskClicked)
        self.btn_add_logo = PushButton("Logo", self.row2_widget)
        self.btn_add_logo.setToolTip("Chọn ảnh Logo chèn lên video (kéo thả & chỉnh kích thước trực tiếp)")
        self.btn_add_logo.clicked.connect(self._onAddLogoClicked)
        self.btn_add_wm = PushButton("Watermark", self.row2_widget)
        self.btn_add_wm.setToolTip("Thêm chữ Watermark lên video (kéo thả & chỉnh kích thước trực tiếp)")
        self.btn_add_wm.clicked.connect(self._onAddWatermarkClicked)

        self.row2_layout.addWidget(self.btn_paste_transcript, 1)
        self.row2_layout.addWidget(self.btn_upload_transcript, 1)
        self.row2_layout.addWidget(self.btn_add_mask, 1)
        self.row2_layout.addWidget(self.btn_add_logo, 1)
        self.row2_layout.addWidget(self.btn_add_wm, 1)
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
        self.col3_widget.setMinimumWidth(300)
        self.col3_widget.setMaximumWidth(380)
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

        # Find & Replace inputs
        fr_row = QHBoxLayout()
        fr_row.setSpacing(6)
        self.input_find = LineEdit(self.col3_widget)
        self.input_find.setPlaceholderText("Tìm từ...")
        self.input_replace = LineEdit(self.col3_widget)
        self.input_replace.setPlaceholderText("Thay bằng...")
        fr_row.addWidget(self.input_find, 1)
        fr_row.addWidget(self.input_replace, 1)
        self.col3_layout.addLayout(fr_row)

        # Stacked full-width buttons so Vietnamese labels NEVER clip
        srt_btn_col = QVBoxLayout()
        srt_btn_col.setSpacing(6)
        from PyQt6.QtWidgets import QSizePolicy
        self.btn_replace_all = PushButton("🔄 Thay thế tất cả", self.col3_widget)
        self.btn_replace_all.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_replace_all.setMinimumHeight(32)
        self.btn_replace_all.setToolTip("Thay thế tất cả từ khớp trong phụ đề hiện tại")
        self.btn_replace_all.clicked.connect(self._onReplaceAllClicked)

        self.btn_save_srt = PushButton("💾 Lưu Kịch Bản (SRT)", self.col3_widget)
        self.btn_save_srt.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.btn_save_srt.setMinimumHeight(34)
        self.btn_save_srt.setToolTip("Lưu kịch bản phụ đề ra file .srt")
        self.btn_save_srt.clicked.connect(self._onSaveSrtClicked)

        srt_btn_col.addWidget(self.btn_replace_all)
        srt_btn_col.addWidget(self.btn_save_srt)
        self.col3_layout.addLayout(srt_btn_col)
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

    def _init_media_player(self):
        self.media_player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.audio_output.setVolume(0.85)
        self.media_player.setAudioOutput(self.audio_output)
        self.video_sink = QVideoSink(self)
        self.media_player.setVideoSink(self.video_sink)
        self.video_sink.videoFrameChanged.connect(self._on_video_frame)
        self.media_player.positionChanged.connect(self._on_player_pos)
        self.media_player.durationChanged.connect(self._on_player_dur)
        self.media_player.playbackStateChanged.connect(self._on_player_state)

    @staticmethod
    def _fmt_ms(ms: int) -> str:
        s = max(0, int(ms // 1000))
        return f"{s // 60:02d}:{s % 60:02d}"

    def _on_video_frame(self, frame):
        try:
            if frame and frame.isValid():
                img = frame.toImage()
                if not img.isNull():
                    self.video_canvas.setImage(img)
        except Exception:
            pass

    def _on_player_pos(self, pos: int):
        if hasattr(self, "slider_seek") and not self.slider_seek.isSliderDown():
            self.slider_seek.setValue(pos)
        if hasattr(self, "lbl_time_cur"):
            self.lbl_time_cur.setText(self._fmt_ms(pos))

    def _on_player_dur(self, dur: int):
        if hasattr(self, "slider_seek"):
            self.slider_seek.setRange(0, max(0, dur))
        if hasattr(self, "lbl_time_dur"):
            self.lbl_time_dur.setText(self._fmt_ms(dur))

    def _on_player_state(self, state):
        if hasattr(self, "btn_play_pause"):
            if state == QMediaPlayer.PlaybackState.PlayingState:
                self.btn_play_pause.setText("Tạm dừng")
                self.btn_play_pause.setIcon(FIF.PAUSE)
            else:
                self.btn_play_pause.setText("Phát")
                self.btn_play_pause.setIcon(FIF.PLAY)

    def _toggle_play_pause(self):
        vp = self.get_active_video_path()
        if not vp or not os.path.exists(vp):
            InfoBar.warning("Chưa có video", "Vui lòng chọn video nguồn trước khi phát.", parent=self, position=InfoBarPosition.TOP)
            return
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            if self.media_player.source().isEmpty():
                self.media_player.setSource(QUrl.fromLocalFile(vp))
            self.media_player.play()

    def _preview_video_frame(self, video_path: str):
        if not video_path or not os.path.exists(video_path):
            return
        try:
            self.media_player.stop()
            self.media_player.setSource(QUrl.fromLocalFile(video_path))
        except Exception:
            pass
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

    def _onVoiceSelectionChanged(self, idx: int):
        voice_id = self.combo_voice.itemData(idx) or "piper:banmai"
        set_config("tts_voice", voice_id)
        self._update_tiktok_session_visibility()

    def _update_tiktok_session_visibility(self):
        if not hasattr(self, "tiktok_session_box"):
            return
        voice_id = str(self.combo_voice.currentData() or "")
        is_tiktok = voice_id.startswith("tiktok:")
        self.tiktok_session_box.setVisible(is_tiktok)
        if is_tiktok and hasattr(self, "line_tiktok_session"):
            saved = get_config("tiktok_session_id", "") or ""
            if self.line_tiktok_session.text().strip() != saved:
                self.line_tiktok_session.blockSignals(True)
                self.line_tiktok_session.setText(saved)
                self.line_tiktok_session.blockSignals(False)

    def _onAddLogoClicked(self):
        p, _ = QFileDialog.getOpenFileName(self, "Chọn ảnh Logo", "", "Image Files (*.png *.jpg *.jpeg *.webp)")
        if not p:
            return
        img = QImage(p)
        if img.isNull():
            InfoBar.error("Lỗi ảnh", "Không đọc được file ảnh Logo.", parent=self, position=InfoBarPosition.TOP)
            return
        self.video_canvas.logo_path = p
        self.video_canvas.logo_image = img
        if not self.video_canvas.logo_rel:
            self.video_canvas.logo_rel = [0.76, 0.05, 0.18, 0.14]
        self.video_canvas.saveConfig()
        self.video_canvas.update()
        self._appendLog(f"Đã thêm Logo (kéo thả & kéo góc dưới-phải để chỉnh kích thước): {os.path.basename(p)}")

    def _onAddWatermarkClicked(self):
        from PyQt6.QtWidgets import QInputDialog
        cur = getattr(self.video_canvas, "watermark_text", "") or ""
        text, ok = QInputDialog.getText(self, "Watermark", "Nhập chữ Watermark (để trống để tắt):", text=cur)
        if ok:
            self.video_canvas.watermark_text = text.strip()
            if not self.video_canvas.wm_rel:
                self.video_canvas.wm_rel = [0.04, 0.04, 0.34, 0.09]
            self.video_canvas.saveConfig()
            self.video_canvas.update()
            self._appendLog(f"Đã cập nhật Watermark: '{text.strip()}'" if text.strip() else "Đã tắt Watermark.")

    def _onReplaceAllClicked(self):
        find_txt = self.input_find.text() if hasattr(self, "input_find") else ""
        repl_txt = self.input_replace.text() if hasattr(self, "input_replace") else ""
        srt = self.get_current_srt_path()
        if not find_txt or not srt or not os.path.exists(srt):
            InfoBar.warning("Thông báo", "Vui lòng nhập từ cần tìm và đảm bảo đã có phụ đề.", parent=self, position=InfoBarPosition.TOP)
            return
        try:
            import pysrt
            subs = pysrt.open(srt, encoding="utf-8")
            cnt = 0
            for s in subs:
                if find_txt in s.text:
                    s.text = s.text.replace(find_txt, repl_txt)
                    cnt += 1
            subs.save(srt, encoding="utf-8")
            target_list = self.srt_trans_list if srt == self._trans_srt_path else self.srt_orig_list
            self._load_srt_to_list(srt, target_list)
            InfoBar.success("Hoàn tất", f"Đã thay thế {cnt} dòng phụ đề.", parent=self, position=InfoBarPosition.TOP)
        except Exception as e:
            InfoBar.error("Lỗi", str(e), parent=self, position=InfoBarPosition.TOP)

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

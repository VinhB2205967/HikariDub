"""
MainWindow View & MVVM Controller for Hikari Tsukimi v3.0 (Qt6 / PySide6).
Implements:
- 56px Top Bar (Logo, AI Engine status pill, Output Folder, Settings, PRO badge)
- 64px Left Icon Navigation Rail
- 3-Column QSplitter (22% / 53% / 25% ratio, persisted on close)
- Column 1: 5 Collapsible Cards (Source, Whisper STT, AI Voice, Translation, Audio Mix & Vocal Filter)
- Column 2: QMediaPlayer live preview + Aspect Ratio + Transform Popover + WaveformTimeline + Overlay Icon Tabs
- Column 3: Editable Subtitle Table (Original & Translated side-by-side) + click-to-seek + Find/Replace
- Bottom Bar: 4-Step Interactive Stepper + Auto Run + Cancel + Progress/ETA + Collapsible Colored Log
"""

import os
import pysrt
from app.qt_compat import (
    QMainWindow, QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout, QScrollArea,
    QSplitter, QLineEdit, QPlainTextEdit, QComboBox, QProgressBar, QCheckBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, Qt, QUrl, QImage,
    QPixmap, QMediaPlayer, QAudioOutput, QVideoSink, QMenu
)
from app.theme import TOKENS
from services.settings_service import SettingsService
from ui.widgets import (
    PrimaryButton, SecondaryButton, DangerButton, GhostButton, ElidedLabel,
    PasswordInput, LabeledSlider, CollapsibleCard, StepperBar, WaveformTimeline
)
from core.pipeline_engine import PipelineContext
from workers.pipeline_worker import PipelineWorker


class VideoPreviewStage(QFrame):
    """Drag-and-drop video preview surface with aspect ratio & empty state."""

    fileDropped = None

    def __init__(self, hint_text: str, on_pick_cb, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.setAcceptDrops(True)
        self._on_pick = on_pick_cb
        self._qimg = None
        self._aspect = (16, 9)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.empty_box = QWidget(self)
        eb_lay = QVBoxLayout(self.empty_box)
        eb_lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        eb_lay.setSpacing(10)

        lbl_icon = QLabel("🎬", self.empty_box)
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icon.setStyleSheet("font-size: 32px; background: transparent;")
        eb_lay.addWidget(lbl_icon)

        self.lbl_hint = QLabel(hint_text, self.empty_box)
        self.lbl_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_hint.setObjectName("SubLabel")
        eb_lay.addWidget(self.lbl_hint)

        btn_pick = PrimaryButton("Chọn Video Nguồn", parent=self.empty_box)
        btn_pick.clicked.connect(self._on_pick)
        eb_lay.addWidget(btn_pick, 0, Qt.AlignmentFlag.AlignCenter)

        lay.addWidget(self.empty_box)

        self.lbl_frame = QLabel(self)
        self.lbl_frame.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_frame.setStyleSheet("background: #07090E; border-radius: 8px;")
        self.lbl_frame.hide()
        lay.addWidget(self.lbl_frame, 1)

    def set_frame(self, img: QImage):
        if img and not img.isNull():
            self._qimg = img
            self.empty_box.hide()
            self.lbl_frame.show()
            self._render_pixmap()

    def set_aspect_ratio(self, w: int, h: int):
        self._aspect = (max(1, w), max(1, h))
        self._render_pixmap()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._render_pixmap()

    def _render_pixmap(self):
        if not self._qimg or self._qimg.isNull():
            return
        pm = QPixmap.fromImage(self._qimg)
        scaled = pm.scaled(
            max(120, self.width() - 24),
            max(100, self.height() - 24),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.lbl_frame.setPixmap(scaled)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            p = url.toLocalFile()
            if p.lower().endswith((".mp4", ".mkv", ".mov", ".avi")) and callable(self.fileDropped):
                self.fileDropped(p)
                break


class StudioMainWindow(QMainWindow):
    def __init__(self, settings: SettingsService):
        super().__init__()
        self.settings = settings
        self.video_path = ""
        self.ctx: PipelineContext = None
        self.worker: PipelineWorker = None

        self.setWindowTitle(self.settings.tr("app_title"))
        self.setMinimumSize(1100, 680)
        w, h = self.settings.get("window_size", [1420, 860])
        self.resize(int(w), int(h))

        central = QWidget(self)
        self.setCentralWidget(central)
        root_v = QVBoxLayout(central)
        root_v.setContentsMargins(0, 0, 0, 0)
        root_v.setSpacing(0)

        # 1. Top Header Bar (56px)
        root_v.addWidget(self._build_top_bar())

        # 2. Body: 64px Left Rail + 3-Column Splitter
        body_h = QHBoxLayout()
        body_h.setContentsMargins(0, 0, 0, 0)
        body_h.setSpacing(0)
        body_h.addWidget(self._build_side_rail())

        self.splitter = QSplitter(Qt.Orientation.Horizontal, central)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.addWidget(self._build_col1_settings())
        self.splitter.addWidget(self._build_col2_preview())
        self.splitter.addWidget(self._build_col3_subtitles())

        # Apply 22% / 53% / 25% default or saved splitter sizes
        saved_sizes = self.settings.get("splitter_sizes", [310, 750, 350])
        self.splitter.setSizes([int(x) for x in saved_sizes])
        self.splitter.setStretchFactor(0, 22)
        self.splitter.setStretchFactor(1, 53)
        self.splitter.setStretchFactor(2, 25)

        body_h.addWidget(self.splitter, 1)
        root_v.addLayout(body_h, 1)

        # 3. Bottom Bar (Stepper + Auto Start + Cancel + Progress/ETA + Collapsible Log)
        root_v.addWidget(self._build_bottom_bar())

    # ── Top Bar (56px) ────────────────────────────────────────────────────────
    def _build_top_bar(self) -> QFrame:
        bar = QFrame(self)
        bar.setObjectName("TopBar")
        bar.setFixedHeight(56)
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(12)

        lbl_logo = QLabel("✦ Hikari Tsukimi v3.0", bar)
        lbl_logo.setObjectName("PageTitle")
        lay.addWidget(lbl_logo)

        self.lbl_engine = QLabel(f"● {self.settings.tr('engine_ready')}", bar)
        self.lbl_engine.setStyleSheet(
            f"color: {TOKENS.SUCCESS}; background: rgba(46,204,113,0.12); "
            f"border: 1px solid rgba(46,204,113,0.35); border-radius: 12px; padding: 4px 12px; font-size: 12px; font-weight: 700;"
        )
        lay.addWidget(self.lbl_engine)
        lay.addStretch(1)

        btn_out = SecondaryButton("📂 " + self.settings.tr("output_dir"), parent=bar)
        btn_out.clicked.connect(self._open_output_dir)
        lay.addWidget(btn_out)

        btn_PRO = PrimaryButton("PRO STUDIO", tooltip="Phiên bản AI Studio Offline đầy đủ", parent=bar)
        lay.addWidget(btn_PRO)
        return bar

    # ── 64px Left Icon Navigation Rail ────────────────────────────────────────
    def _build_side_rail(self) -> QFrame:
        rail = QFrame(self)
        rail.setObjectName("SideRail")
        rail.setFixedWidth(64)
        lay = QVBoxLayout(rail)
        lay.setContentsMargins(8, 12, 8, 12)
        lay.setSpacing(10)

        for idx, (ico, tip) in enumerate([
            ("🏠", "Trang chủ"),
            ("🎞️", "Dự án"),
            ("🎙️", "Thư viện giọng"),
            ("📋", "Hàng đợi"),
            ("⚙️", "Cài đặt"),
        ]):
            btn = GhostButton(ico, checkable=True, tooltip=tip, parent=rail)
            btn.setChecked(idx == 0)
            btn.setFixedHeight(42)
            lay.addWidget(btn)
        lay.addStretch(1)
        return rail

    # ── Column 1: Project & Voice (5 Collapsible Cards) ──────────────────────
    def _build_col1_settings(self) -> QWidget:
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setMinimumWidth(260)

        container = QWidget(scroll)
        lay = QVBoxLayout(container)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(10)

        # Card 1: Nguồn & Đầu ra
        c_src = CollapsibleCard(self.settings.tr("card_source"), expanded=True, parent=container)
        btn_pick = PrimaryButton("📁 " + self.settings.tr("select_video"), parent=c_src)
        btn_pick.clicked.connect(self._pick_video)
        c_src.body_layout.addWidget(btn_pick)

        self.lbl_video_meta = ElidedLabel(self.settings.tr("no_video"), c_src)
        self.lbl_video_meta.setObjectName("SubLabel")
        c_src.body_layout.addWidget(self.lbl_video_meta)

        out_row = QHBoxLayout()
        self.line_out_dir = QLineEdit(self.settings.get("output_dir", ""), c_src)
        btn_browse_out = SecondaryButton("Đổi...", tooltip="Chọn thư mục xuất video", parent=c_src)
        btn_browse_out.clicked.connect(self._browse_output_dir)
        out_row.addWidget(self.line_out_dir, 1)
        out_row.addWidget(btn_browse_out)
        c_src.body_layout.addLayout(out_row)
        lay.addWidget(c_src)

        # Card 2: Nhận dạng giọng nói (Whisper)
        c_stt = CollapsibleCard(self.settings.tr("card_stt"), expanded=True, parent=container)
        self.combo_whisper = QComboBox(c_stt)
        for label, val in [
            ("Tiny — Siêu tốc (~10x, tốn ít VRAM)", "tiny"),
            ("Base — Nhanh (~6x, độ chính xác khá)", "base"),
            ("Small — Cân bằng (Khuyên dùng)", "small"),
            ("Medium — Độ chính xác cao", "medium"),
        ]:
            self.combo_whisper.addItem(label, userData=val)
        self.combo_whisper.setCurrentIndex(2)
        self.combo_whisper.currentIndexChanged.connect(
            lambda i: self.settings.set("whisper_model", self.combo_whisper.itemData(i))
        )
        c_stt.body_layout.addWidget(self.combo_whisper)

        self.combo_src_lang = QComboBox(c_stt)
        for lbl, code in [("Ngôn ngữ nguồn: Tự động nhận diện", "auto"), ("Tiếng Trung (zh)", "zh"), ("Tiếng Anh (en)", "en"), ("Tiếng Nhật (ja)", "ja")]:
            self.combo_src_lang.addItem(lbl, userData=code)
        c_stt.body_layout.addWidget(self.combo_src_lang)
        lay.addWidget(c_stt)

        # Card 3: Giọng đọc AI
        c_tts = CollapsibleCard(self.settings.tr("card_tts"), expanded=True, parent=container)
        self.combo_voice = QComboBox(c_tts)
        for lbl, vid in [
            ("Ban Mai (Nữ · Piper Offline)", "piper:banmai"),
            ("Mạnh Dũng (Nam · Piper Offline)", "piper:manhdung"),
            ("Chiêu Thanh (Nữ · Piper Offline)", "piper:chieuthanh"),
            ("Lạc Phi (Nữ · Piper Offline)", "piper:lacphi"),
            ("Ngọc Huyền (Nữ · Piper Offline)", "piper:ngochuyen"),
            ("Vais1000 (Nữ tự nhiên · Piper Offline)", "piper:vais1000"),
            ("TikTok VN — Nữ 01 (SessionID)", "tiktok:BV074_streaming"),
            ("TikTok VN — Nam 01 (SessionID)", "tiktok:BV075_streaming"),
            ("TikTok US — Jessie (SessionID)", "tiktok:en_us_002"),
            ("TikTok JP — Nữ 01 (SessionID)", "tiktok:jp_001"),
        ]:
            self.combo_voice.addItem(lbl, userData=vid)
        self.combo_voice.currentIndexChanged.connect(self._on_voice_changed)
        c_tts.body_layout.addWidget(self.combo_voice)

        # Masked Session ID stored in keyring (never logged)
        self.pw_session = PasswordInput("TikTok Session ID (ẩn an toàn qua Keyring)...", c_tts)
        self.pw_session.setText(self.settings.secrets.get_secret("tiktok_session_id"))
        self.pw_session.textChanged.connect(lambda v: self.settings.secrets.set_secret("tiktok_session_id", v))
        self.pw_session.hide()
        c_tts.body_layout.addWidget(self.pw_session)

        self.slider_speed = LabeledSlider("Tốc độ:", 70, 160, int(self.settings.get("voice_speed", 100)), "%", c_tts)
        self.slider_speed.valueChanged.connect(lambda v: self.settings.set("voice_speed", v))
        c_tts.body_layout.addWidget(self.slider_speed)

        self.slider_pitch = LabeledSlider("Cao độ:", -12, 12, int(self.settings.get("voice_pitch", 0)), " st", c_tts)
        self.slider_pitch.valueChanged.connect(lambda v: self.settings.set("voice_pitch", v))
        c_tts.body_layout.addWidget(self.slider_pitch)
        lay.addWidget(c_tts)

        # Card 4: Dịch thuật & Phong cách
        c_tr = CollapsibleCard(self.settings.tr("card_translate"), expanded=True, parent=container)
        self.combo_target_lang = QComboBox(c_tr)
        self.combo_target_lang.addItems(["Tiếng Việt", "English", "日本語", "한국어", "中文"])
        c_tr.body_layout.addWidget(self.combo_target_lang)

        self.combo_style = QComboBox(c_tr)
        self.combo_style.addItems(["Tự nhiên / Đời thường", "Trang trọng / Thuyết minh", "Hài hước / Giải trí", "Review Phim / Anime", "Tiên hiệp / Cổ trang"])
        c_tr.body_layout.addWidget(self.combo_style)

        self.txt_prompt = QPlainTextEdit(c_tr)
        self.txt_prompt.setPlaceholderText("Ghi chú phong cách dịch tùy chọn...")
        self.txt_prompt.setMaximumHeight(54)
        c_tr.body_layout.addWidget(self.txt_prompt)
        lay.addWidget(c_tr)

        # Card 5: Âm thanh & Lọc giọng
        c_aud = CollapsibleCard(self.settings.tr("card_audio"), expanded=True, parent=container)
        self.chk_vocal_sep = QCheckBox("Tách lời thoại / Giữ nhạc nền BGM", c_aud)
        self.chk_vocal_sep.setChecked(bool(self.settings.get("vocal_sep", False)))
        self.chk_vocal_sep.stateChanged.connect(lambda _: self.settings.set("vocal_sep", self.chk_vocal_sep.isChecked()))
        c_aud.body_layout.addWidget(self.chk_vocal_sep)

        self.slider_orig_vol = LabeledSlider("Âm gốc:", 0, 100, int(self.settings.get("orig_volume", 35)), "%", c_aud)
        self.slider_orig_vol.valueChanged.connect(lambda v: self.settings.set("orig_volume", v))
        c_aud.body_layout.addWidget(self.slider_orig_vol)

        self.slider_voice_vol = LabeledSlider("Giọng AI:", 50, 200, int(self.settings.get("voice_volume", 100)), "%", c_aud)
        self.slider_voice_vol.valueChanged.connect(lambda v: self.settings.set("voice_volume", v))
        c_aud.body_layout.addWidget(self.slider_voice_vol)
        lay.addWidget(c_aud)

        lay.addStretch(1)
        scroll.setWidget(container)
        return scroll

    # ── Column 2: Video Preview, Waveform Timeline & Overlay Toolbar ──────────
    def _build_col2_preview(self) -> QWidget:
        panel = QWidget(self)
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)

        # Top Canvas Toolbar (Aspect Ratio, Fit/Fill, Zoom, Transform Popover)
        tbar = QFrame(panel)
        tbar.setObjectName("Card")
        tb_lay = QHBoxLayout(tbar)
        tb_lay.setContentsMargins(10, 6, 10, 6)
        tb_lay.setSpacing(8)

        tb_lay.addWidget(QLabel("Tỉ lệ:", tbar))
        self.combo_aspect = QComboBox(tbar)
        for lbl, ratio in [("16:9 (Ngang)", (16, 9)), ("9:16 (Dọc Shorts/TikTok)", (9, 16)), ("1:1 (Vuông)", (1, 1)), ("4:5 (Feed)", (4, 5))]:
            self.combo_aspect.addItem(lbl, userData=ratio)
        self.combo_aspect.currentIndexChanged.connect(
            lambda i: self.preview_stage.set_aspect_ratio(*(self.combo_aspect.itemData(i) or (16, 9)))
        )
        tb_lay.addWidget(self.combo_aspect)

        tb_lay.addWidget(GhostButton("Vừa khung", checkable=True, parent=tbar))
        tb_lay.addWidget(GhostButton("Lấp đầy", checkable=True, parent=tbar))

        self.btn_transform_pop = SecondaryButton("Vị trí X/Y & Xoay ▾", parent=tbar)
        self.btn_transform_pop.clicked.connect(self._show_transform_popover)
        tb_lay.addWidget(self.btn_transform_pop)
        tb_lay.addStretch(1)
        lay.addWidget(tbar)

        # Video Stage (with Drag & Drop empty state + live QMediaPlayer frames)
        self.preview_stage = VideoPreviewStage(self.settings.tr("drop_hint"), self._pick_video, panel)
        self.preview_stage.fileDropped = self._load_video_file
        lay.addWidget(self.preview_stage, 1)

        # Playback Bar + Waveform Timeline
        self._init_media_player()
        pbar = QFrame(panel)
        pbar.setObjectName("Card")
        pb_v = QVBoxLayout(pbar)
        pb_v.setContentsMargins(10, 8, 10, 8)
        pb_v.setSpacing(6)

        ctrl_h = QHBoxLayout()
        self.btn_play = SecondaryButton("▶ Phát", parent=pbar)
        self.btn_play.clicked.connect(self._toggle_play)
        self.lbl_time = QLabel("00:00 / 00:00", pbar)
        self.lbl_time.setObjectName("SubLabel")
        ctrl_h.addWidget(self.btn_play)
        ctrl_h.addWidget(self.lbl_time)
        ctrl_h.addStretch(1)

        # Overlay compact icon tabs
        for ico_lbl, tip, handler in [
            ("▭ Vùng che", "Thêm vùng làm mờ phụ đề gốc", lambda: self._append_log("INFO", "Đã bật công cụ Vùng che trên khung hình.")),
            ("🖼️ Logo", "Chèn ảnh Logo lên video", lambda: self._append_log("INFO", "Đã mở công cụ chèn Logo.")),
            ("✒️ Watermark", "Đặt chữ Watermark", lambda: self._append_log("INFO", "Đã bật lớp phủ Watermark.")),
            ("📋 Dán kịch bản", "Dán nhanh văn bản kịch bản", self._import_srt_dialog),
            ("📂 Nạp SRT", "Nạp file phụ đề .srt", self._import_srt_dialog),
        ]:
            b = GhostButton(ico_lbl, tooltip=tip, parent=pbar)
            b.clicked.connect(handler)
            ctrl_h.addWidget(b)
        pb_v.addLayout(ctrl_h)

        self.timeline = WaveformTimeline(pbar)
        self.timeline.seekRequested.connect(self.media_player.setPosition)
        pb_v.addWidget(self.timeline)
        lay.addWidget(pbar)
        return panel

    # ── Column 3: Side-by-Side Editable Subtitle Editor ───────────────────────
    def _build_col3_subtitles(self) -> QWidget:
        card = QFrame(self)
        card.setObjectName("Card")
        card.setMinimumWidth(270)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)

        lbl = QLabel("📝 " + self.settings.tr("col3_title"), card)
        lbl.setObjectName("CardTitle")
        lay.addWidget(lbl)

        # Find & Replace Row
        fr_h = QHBoxLayout()
        fr_h.setSpacing(6)
        self.line_find = QLineEdit(card)
        self.line_find.setPlaceholderText("Tìm từ...")
        self.line_replace = QLineEdit(card)
        self.line_replace.setPlaceholderText("Thay bằng...")
        btn_repl = SecondaryButton("Thay tất cả", tooltip="Thay thế toàn bộ từ khớp trong cột Dịch", parent=card)
        btn_repl.clicked.connect(self._replace_all_subtitles)
        fr_h.addWidget(self.line_find, 1)
        fr_h.addWidget(self.line_replace, 1)
        fr_h.addWidget(btn_repl)
        lay.addLayout(fr_h)

        # Editable Table: # | Thời gian | Văn bản gốc | Bản dịch
        self.table_subs = QTableWidget(0, 3, card)
        self.table_subs.setHorizontalHeaderLabels(["Thời gian", "Phụ đề gốc", "Phụ đề dịch (Sửa trực tiếp)"])
        self.table_subs.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table_subs.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table_subs.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.table_subs.verticalHeader().setVisible(False)
        self.table_subs.cellClicked.connect(self._on_subtitle_row_clicked)
        lay.addWidget(self.table_subs, 1)

        act_h = QHBoxLayout()
        btn_save_srt = SecondaryButton("💾 Lưu SRT", parent=card)
        btn_save_srt.clicked.connect(self._save_edited_srt)
        btn_export_srt = PrimaryButton("📤 Xuất SRT", parent=card)
        btn_export_srt.clicked.connect(self._export_srt_as)
        act_h.addWidget(btn_save_srt, 1)
        act_h.addWidget(btn_export_srt, 1)
        lay.addLayout(act_h)
        return card

    # ── Bottom Action Bar (Stepper + Auto Start + Cancel + Progress + Log) ────
    def _build_bottom_bar(self) -> QFrame:
        bar = QFrame(self)
        bar.setObjectName("BottomBar")
        v = QVBoxLayout(bar)
        v.setContentsMargins(16, 10, 16, 10)
        v.setSpacing(8)

        top_h = QHBoxLayout()
        top_h.setSpacing(12)

        self.stepper = StepperBar([
            self.settings.tr("step_1"),
            self.settings.tr("step_2"),
            self.settings.tr("step_3"),
            self.settings.tr("step_4"),
        ], bar)
        self.stepper.stepClicked.connect(self._start_single_step)
        top_h.addWidget(self.stepper, 3)

        self.progress_bar = QProgressBar(bar)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        top_h.addWidget(self.progress_bar, 1)

        self.lbl_eta = QLabel("Sẵn sàng", bar)
        self.lbl_eta.setObjectName("SubLabel")
        self.lbl_eta.setMinimumWidth(140)
        top_h.addWidget(self.lbl_eta)

        self.btn_toggle_log = GhostButton("Nhật ký ▾", checkable=True, parent=bar)
        self.btn_toggle_log.toggled.connect(lambda c: self.txt_log.setVisible(c))
        top_h.addWidget(self.btn_toggle_log)

        self.btn_cancel = DangerButton(self.settings.tr("cancel"), parent=bar)
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self._cancel_pipeline)
        top_h.addWidget(self.btn_cancel)

        self.btn_start = PrimaryButton(self.settings.tr("start_auto"), parent=bar)
        self.btn_start.clicked.connect(lambda: self._start_pipeline(None))
        top_h.addWidget(self.btn_start)
        v.addLayout(top_h)

        self.txt_log = QPlainTextEdit(bar)
        self.txt_log.setReadOnly(True)
        self.txt_log.setMaximumHeight(95)
        self.txt_log.hide()
        v.addWidget(self.txt_log)
        return bar

    # ── Controller / Event Handlers ───────────────────────────────────────────
    def _init_media_player(self):
        self.media_player = QMediaPlayer(self)
        self.audio_out = QAudioOutput(self)
        self.media_player.setAudioOutput(self.audio_out)
        self.video_sink = QVideoSink(self)
        self.media_player.setVideoSink(self.video_sink)
        self.video_sink.videoFrameChanged.connect(self._on_video_frame)
        self.media_player.positionChanged.connect(self._on_pos_changed)
        self.media_player.durationChanged.connect(self._on_dur_changed)

    def _on_video_frame(self, frame):
        if frame and frame.isValid():
            img = frame.toImage()
            if not img.isNull():
                self.preview_stage.set_frame(img)

    def _on_pos_changed(self, pos: int):
        dur = max(1, self.media_player.duration())
        self.timeline.set_position(pos, dur)
        self.lbl_time.setText(f"{pos // 60000:02d}:{(pos // 1000) % 60:02d} / {dur // 60000:02d}:{(dur // 1000) % 60:02d}")

    def _on_dur_changed(self, dur: int):
        self.timeline.set_position(self.media_player.position(), max(1, dur))

    def _toggle_play(self):
        if not self.video_path:
            return
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.btn_play.setText("▶ Phát")
        else:
            self.media_player.play()
            self.btn_play.setText("⏸ Tạm dừng")

    def _on_voice_changed(self, idx: int):
        vid = str(self.combo_voice.itemData(idx) or "piper:banmai")
        self.settings.set("voice_id", vid)
        self.pw_session.setVisible(vid.startswith("tiktok:"))

    def _show_transform_popover(self):
        menu = QMenu(self)
        menu.addAction("Căn giữa khung hình (X=0, Y=0)")
        menu.addAction("Xoay ngang 90°")
        menu.addAction("Đặt lại Zoom 100%")
        menu.exec(self.btn_transform_pop.mapToGlobal(self.btn_transform_pop.rect().bottomLeft()))

    def _pick_video(self):
        p, _ = QFileDialog.getOpenFileName(self, "Chọn Video Nguồn", "", "Video Files (*.mp4 *.mkv *.mov *.avi)")
        if p:
            self._load_video_file(p)

    def _load_video_file(self, path: str):
        if not path or not os.path.exists(path):
            return
        self.video_path = path
        size_mb = os.path.getsize(path) / (1024 * 1024)
        self.lbl_video_meta.set_full_text(f"{os.path.basename(path)} ({size_mb:.1f} MB)")
        self.media_player.setSource(QUrl.fromLocalFile(path))
        self.media_player.play()
        self.media_player.pause()
        self.stepper.reset_all()
        self._append_log("INFO", f"Đã nạp video: {os.path.basename(path)}")

    def _browse_output_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Chọn thư mục xuất", self.line_out_dir.text())
        if d:
            self.line_out_dir.setText(d)
            self.settings.set("output_dir", d)

    def _open_output_dir(self):
        d = self.line_out_dir.text().strip() or self.settings.get("output_dir")
        os.makedirs(d, exist_ok=True)
        if hasattr(os, "startfile"):
            os.startfile(d)

    def _build_context(self) -> PipelineContext:
        cfg = {
            "whisper_model": self.combo_whisper.currentData(),
            "source_lang": self.combo_src_lang.currentData(),
            "target_lang": self.combo_target_lang.currentText(),
            "translate_style": self.combo_style.currentText(),
            "custom_prompt": self.txt_prompt.toPlainText().strip(),
            "voice_id": self.combo_voice.currentData(),
            "voice_speed": self.slider_speed.value(),
            "voice_pitch": self.slider_pitch.value(),
            "vocal_sep": self.chk_vocal_sep.isChecked(),
            "orig_volume": self.slider_orig_vol.value(),
            "voice_volume": self.slider_voice_vol.value(),
            "tiktok_session_id": self.pw_session.text().strip(),
        }
        out_dir = self.line_out_dir.text().strip() or self.settings.get("output_dir")
        if self.ctx and self.ctx.video_path == self.video_path:
            self.ctx.config.update(cfg)
            self.ctx.output_dir = out_dir
            return self.ctx
        self.ctx = PipelineContext(self.video_path, out_dir, cfg)
        return self.ctx

    def _start_single_step(self, step_idx: int):
        self._start_pipeline(step_idx)

    def _start_pipeline(self, single_step: int = None):
        if self.worker and self.worker.isRunning():
            return
        ctx = self._build_context()
        self.btn_start.setEnabled(False)
        self.btn_cancel.setEnabled(True)

        self.worker = PipelineWorker(ctx, single_step=single_step, parent=self)
        self.worker.stepStateChanged.connect(self.stepper.set_step_state)
        self.worker.progressUpdated.connect(self._on_progress)
        self.worker.logMessage.connect(self._append_log)
        self.worker.subtitlesReady.connect(self._on_subtitles_ready)
        self.worker.pipelineFinished.connect(self._on_pipeline_finished)
        self.worker.start()

    def _cancel_pipeline(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()

    def _on_progress(self, pct: int, eta: str):
        self.progress_bar.setValue(pct)
        self.lbl_eta.setText(eta)

    def _append_log(self, level: str, msg: str):
        color = {
            "INFO": TOKENS.TEXT_SECONDARY,
            "SUCCESS": TOKENS.SUCCESS,
            "WARN": TOKENS.WARNING,
            "ERROR": TOKENS.ERROR,
        }.get(level, TOKENS.TEXT_PRIMARY)
        self.txt_log.appendHtml(f'<span style="color:{color};">[{level}] {msg}</span>')

    def _on_subtitles_ready(self, kind: str, srt_path: str):
        if not os.path.exists(srt_path):
            return
        subs = pysrt.open(srt_path, encoding="utf-8")
        if kind == "orig" or self.table_subs.rowCount() != len(subs):
            self.table_subs.setRowCount(len(subs))
        tl_items = []
        for row, s in enumerate(subs):
            t_item = QTableWidgetItem(f"{s.start} → {s.end}")
            t_item.setData(Qt.ItemDataRole.UserRole, s.start.ordinal)
            t_item.setFlags(t_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table_subs.setItem(row, 0, t_item)
            col = 1 if kind == "orig" else 2
            self.table_subs.setItem(row, col, QTableWidgetItem(s.text))
            if kind == "orig" and not self.table_subs.item(row, 2):
                self.table_subs.setItem(row, 2, QTableWidgetItem(""))
            tl_items.append((s.start.ordinal, s.end.ordinal, s.text))
        self.timeline.set_subtitles(tl_items)

    def _on_subtitle_row_clicked(self, row: int, _col: int):
        item = self.table_subs.item(row, 0)
        if item:
            ms = item.data(Qt.ItemDataRole.UserRole)
            if ms is not None:
                self.media_player.setPosition(int(ms))

    def _replace_all_subtitles(self):
        f_txt = self.line_find.text()
        r_txt = self.line_replace.text()
        if not f_txt:
            return
        count = 0
        for row in range(self.table_subs.rowCount()):
            it = self.table_subs.item(row, 2) or self.table_subs.item(row, 1)
            if it and f_txt in it.text():
                it.setText(it.text().replace(f_txt, r_txt))
                count += 1
        self._append_log("SUCCESS", f"Đã thay thế {count} dòng phụ đề.")

    def _save_edited_srt(self) -> str:
        if not self.ctx:
            return ""
        target = self.ctx.trans_srt if os.path.exists(self.ctx.trans_srt) else self.ctx.orig_srt
        if not target or not os.path.exists(target):
            return ""
        subs = pysrt.open(target, encoding="utf-8")
        for row in range(min(len(subs), self.table_subs.rowCount())):
            it_tr = self.table_subs.item(row, 2)
            it_or = self.table_subs.item(row, 1)
            txt = (it_tr.text().strip() if it_tr and it_tr.text().strip() else (it_or.text().strip() if it_or else ""))
            if txt:
                subs[row].text = txt
        subs.save(target, encoding="utf-8")
        self._append_log("SUCCESS", f"Đã lưu phụ đề: {os.path.basename(target)}")
        return target

    def _export_srt_as(self):
        saved = self._save_edited_srt()
        if not saved:
            return
        dest, _ = QFileDialog.getSaveFileName(self, "Xuất File SRT", saved, "Subtitle Files (*.srt)")
        if dest:
            import shutil
            shutil.copy2(saved, dest)
            self._append_log("SUCCESS", f"Đã xuất SRT tới: {dest}")

    def _import_srt_dialog(self):
        p, _ = QFileDialog.getOpenFileName(self, "Nạp File SRT", "", "Subtitle Files (*.srt)")
        if p and os.path.exists(p):
            ctx = self._build_context()
            import shutil
            shutil.copy2(p, ctx.orig_srt)
            self._on_subtitles_ready("orig", ctx.orig_srt)
            self._append_log("SUCCESS", f"Đã nạp SRT: {os.path.basename(p)}")

    def _on_pipeline_finished(self, ok: bool, msg: str):
        self.btn_start.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        if not ok:
            self.btn_toggle_log.setChecked(True)

    def closeEvent(self, event):
        self.settings.set("splitter_sizes", self.splitter.sizes())
        self.settings.set("window_size", [self.width(), self.height()])
        super().closeEvent(event)

"""
Setting Interface Module - Pure Python Edition (Hikari Tsukimi Studio).
Manages Gemini API keys, AI model selection, Whisper/Piper model downloads, and output settings.
"""

import os
import sys
import subprocess
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog,
    QStackedWidget, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from qfluentwidgets import (
    Pivot, ComboBox, PushButton, PrimaryPushButton, LineEdit,
    PlainTextEdit, ProgressBar, InfoBar, InfoBarPosition, FluentIcon as FIF
)

from app.common.design_system import Colors, Gradients
from app.common.config_manager import get_config, set_config, load_config, save_config


class ModelDownloaderWorker(QThread):
    """Runs download_all_models.py in a subprocess with full environment access."""

    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        try:
            proj_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            script = os.path.join(proj_root, "download_all_models.py")
            if not os.path.exists(script):
                self.finished.emit(False, "Không tìm thấy download_all_models.py")
                return

            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            env["PYTHONPATH"] = proj_root + os.pathsep + env.get("PYTHONPATH", "")
            env["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

            proc = subprocess.Popen(
                [sys.executable, script],
                cwd=proj_root,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            for line in proc.stdout:
                self.log.emit(line.rstrip())
            proc.wait()
            if proc.returncode == 0:
                self.progress.emit(100)
                self.finished.emit(True, "Đã tải và kiểm tra tất cả model AI thành công!")
            else:
                self.finished.emit(False, f"Quá trình tải model kết thúc với mã {proc.returncode}")
        except Exception as e:
            self.finished.emit(False, str(e))


class SettingInterface(QWidget):
    """System Settings & AI Models Interface."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingInterface")
        self.config = load_config()
        self._is_loading = True
        self._dl_worker = None
        self._initWidget()
        self._loadConfigToUI()
        self._is_loading = False

    def _initWidget(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 16, 24, 16)
        root.setSpacing(12)

        # Header + license badge
        top = QHBoxLayout()
        lbl_title = QLabel("⚙️ Cài Đặt Hệ Thống & Mô Hình AI", self)
        lbl_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 16px; font-weight: 800;")
        top.addWidget(lbl_title)
        top.addStretch(1)
        self.lbl_license_status = QLabel("✦ HIKARI TSUKIMI • AI Dubbing Studio", self)
        self.lbl_license_status.setStyleSheet("color: #34D399; font-weight: bold; font-size: 13px; letter-spacing: 0.5px;")
        top.addWidget(self.lbl_license_status)
        root.addLayout(top)

        # Pivot tabs
        self.pivot = Pivot(self)
        self.stackedWidget = QStackedWidget(self)
        root.addWidget(self.pivot)
        root.addWidget(self.stackedWidget, 1)

        # Page 1: Translation & API
        self.page_trans = QWidget(self)
        trans_lay = QVBoxLayout(self.page_trans)
        trans_lay.setContentsMargins(0, 8, 0, 0)
        trans_lay.setSpacing(12)

        self.group_trans = QFrame(self.page_trans)
        self.group_trans.setStyleSheet(f"QFrame {{ background: {Colors.BG_DARK}; border: 1px solid {Colors.BORDER}; border-radius: 12px; }}")
        gt_lay = QVBoxLayout(self.group_trans)
        gt_lay.setContentsMargins(16, 14, 16, 14)
        gt_lay.setSpacing(10)

        lbl_api_sub = QLabel("Cấu hình Gemini API & Mô hình Dịch thuật AI", self.group_trans)
        lbl_api_sub.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 700; font-size: 14px; border: none;")
        gt_lay.addWidget(lbl_api_sub)

        # Model Selector Box
        model_box = QWidget(self.group_trans)
        model_box.setObjectName("hikariApiModelBox")
        model_box.setStyleSheet("""
            QWidget#hikariApiModelBox {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(99, 102, 241, 0.12), stop:1 rgba(6, 182, 212, 0.10));
                border: 1px solid rgba(99, 102, 241, 0.35);
                border-radius: 10px;
            }
        """)
        mv = QVBoxLayout(model_box)
        mv.setContentsMargins(14, 10, 14, 12)
        mv.setSpacing(8)

        top_row = QHBoxLayout()
        lbl_m_title = QLabel("🧠 Mô hình AI Dịch thuật (Model API):", model_box)
        lbl_m_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 700; font-size: 13px; background: transparent; border: none;")
        top_row.addWidget(lbl_m_title)

        self.lbl_active_model_badge = QLabel("Đang dùng: Gemini 4 Argon", model_box)
        self.lbl_active_model_badge.setStyleSheet(f"""
            color: {Colors.ACCENT_BRIGHT};
            background: rgba(6, 182, 212, 0.16);
            border: 1px solid rgba(6, 182, 212, 0.45);
            border-radius: 6px;
            padding: 2px 10px;
            font-size: 11px;
            font-weight: 700;
        """)
        top_row.addWidget(self.lbl_active_model_badge)
        top_row.addStretch(1)
        mv.addLayout(top_row)

        ctrl_row = QHBoxLayout()
        self.combo_gemini_model = ComboBox(model_box)
        self.combo_gemini_model.setMinimumWidth(340)
        self._gemini_model_options = [
            ("⚡ Gemini 4 Argon (gemini-4-argon — Cần bật thanh toán)", "gemini-4-argon"),
            ("🚀 Gemini 3.5 Flash (Nhanh ~2s — Dịch hay, có Free)", "gemini-3.5-flash"),
            ("💨 Gemini 3.5 Flash Lite (Siêu tốc ~1s — có Free)", "gemini-3.5-flash-lite"),
            ("🆕 Gemini Flash Latest (Luôn dùng bản Flash mới nhất)", "gemini-flash-latest"),
            ("🛡 Gemini 2.5 Flash (Tương thích ngược)", "gemini-2.5-flash"),
            ("🔄 Tự động xoay vòng mô hình (Auto Fallback)", "auto"),
        ]
        for label_txt, model_id in self._gemini_model_options:
            self.combo_gemini_model.addItem(label_txt, userData=model_id)
        ctrl_row.addWidget(self.combo_gemini_model, 1)

        self._quick_model_btns = {}
        for btn_txt, m_id in [
            ("⚡ Argon", "gemini-4-argon"),
            ("🚀 3.5 Flash", "gemini-3.5-flash"),
            ("💨 3.5 Lite", "gemini-3.5-flash-lite"),
            ("🆕 Latest", "gemini-flash-latest"),
            ("🔄 Auto", "auto"),
        ]:
            qb = PushButton(btn_txt, model_box)
            qb.setCursor(Qt.CursorShape.PointingHandCursor)
            qb.setFixedHeight(32)
            qb.clicked.connect(lambda checked=False, mid=m_id: self._select_gemini_model(mid, save_now=True))
            self._quick_model_btns[m_id] = qb
            ctrl_row.addWidget(qb)
        mv.addLayout(ctrl_row)

        self.combo_gemini_model.currentIndexChanged.connect(self._on_combo_model_changed)
        gt_lay.addWidget(model_box)

        lbl_keys = QLabel("Danh sách Gemini API Key (mỗi dòng 1 key — để trống sẽ dùng dịch miễn phí Google Web):", self.group_trans)
        lbl_keys.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; border: none;")
        gt_lay.addWidget(lbl_keys)

        self.txt_api_keys = PlainTextEdit(self.group_trans)
        self.txt_api_keys.setPlaceholderText("AIzaSy... (tùy chọn, có thể để trống)")
        self.txt_api_keys.setMaximumHeight(110)
        gt_lay.addWidget(self.txt_api_keys)

        trans_lay.addWidget(self.group_trans)

        # TikTok TTS Session ID Card
        self.group_tiktok = QFrame(self.page_trans)
        self.group_tiktok.setStyleSheet(f"QFrame {{ background: {Colors.BG_DARK}; border: 1px solid {Colors.BORDER}; border-radius: 12px; }}")
        tk_lay = QVBoxLayout(self.group_tiktok)
        tk_lay.setContentsMargins(16, 14, 16, 14)
        tk_lay.setSpacing(8)

        lbl_tk_title = QLabel("🎙️ Cấu hình TikTok TTS Session ID", self.group_tiktok)
        lbl_tk_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 700; font-size: 14px; border: none;")
        tk_lay.addWidget(lbl_tk_title)

        lbl_tk_hint = QLabel("Nhập cookie `sessionid` của tài khoản TikTok để dùng 18 giọng đọc TikTok (BV074, BV075, en_us_002...):", self.group_tiktok)
        lbl_tk_hint.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; border: none;")
        tk_lay.addWidget(lbl_tk_hint)

        self.line_tiktok_session = LineEdit(self.group_tiktok)
        self.line_tiktok_session.setPlaceholderText("Dán TikTok Session ID vào đây rồi nhấn Lưu Cài Đặt...")
        tk_lay.addWidget(self.line_tiktok_session)

        trans_lay.addWidget(self.group_tiktok)
        trans_lay.addStretch(1)

        # Page 2: General & Models
        self.page_general = QWidget(self)
        gen_lay = QVBoxLayout(self.page_general)
        gen_lay.setContentsMargins(0, 8, 0, 0)
        gen_lay.setSpacing(12)

        lbl_out = QLabel("Thư mục lưu file mặc định:", self.page_general)
        lbl_out.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 600;")
        gen_lay.addWidget(lbl_out)

        out_row = QHBoxLayout()
        self.line_output_dir = LineEdit(self.page_general)
        self.btn_browse_out = PushButton(FIF.FOLDER, "Chọn Thư Mục", self.page_general)
        self.btn_browse_out.clicked.connect(self._browse_out_dir)
        out_row.addWidget(self.line_output_dir, 1)
        out_row.addWidget(self.btn_browse_out)
        gen_lay.addLayout(out_row)

        dl_row = QHBoxLayout()
        self.btn_download_models = PrimaryPushButton(FIF.DOWNLOAD, "Tải / Sửa lỗi Tất cả Model AI", self.page_general)
        self.btn_download_models.clicked.connect(self._start_model_download)
        dl_row.addWidget(self.btn_download_models)
        dl_row.addStretch(1)
        gen_lay.addLayout(dl_row)

        self.dl_progress = ProgressBar(self.page_general)
        self.dl_progress.setValue(0)
        gen_lay.addWidget(self.dl_progress)

        self.dl_log = PlainTextEdit(self.page_general)
        self.dl_log.setReadOnly(True)
        self.dl_log.setPlaceholderText("Nhật ký tải model...")
        gen_lay.addWidget(self.dl_log, 1)

        # Add pages to Pivot
        self.stackedWidget.addWidget(self.page_trans)
        self.stackedWidget.addWidget(self.page_general)
        self.pivot.addItem("trans", "AI & Dịch Thuật", lambda: self.stackedWidget.setCurrentWidget(self.page_trans))
        self.pivot.addItem("general", "Hệ Thống & Model", lambda: self.stackedWidget.setCurrentWidget(self.page_general))
        self.pivot.setCurrentItem("trans")

        # Save button
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self.btn_save = PrimaryPushButton(FIF.SAVE, "Lưu Cài Đặt", self)
        self.btn_save.clicked.connect(lambda: self._saveConfig(True))
        btn_row.addWidget(self.btn_save)
        root.addLayout(btn_row)

    def _on_combo_model_changed(self, idx: int):
        if 0 <= idx < len(self._gemini_model_options):
            self._select_gemini_model(self._gemini_model_options[idx][1], save_now=True)

    def _select_gemini_model(self, model_id: str, save_now: bool = False):
        _legacy_map = {
            "argon": "gemini-4-argon",
            "gemini-argon": "gemini-4-argon",
            "gemini-2.0-flash": "gemini-3.5-flash",
            "gemini-2.0-flash-lite": "gemini-3.5-flash-lite",
            "gemini-1.5-flash": "gemini-flash-latest",
        }
        model_id = _legacy_map.get((model_id or "").strip().lower(), model_id)
        idx_found = 0
        label_found = "Gemini 4 Argon"
        for i, (lbl_opt, mid_opt) in enumerate(self._gemini_model_options):
            if mid_opt == model_id:
                idx_found = i
                label_found = lbl_opt.split("(")[0].strip()
                break
        self.combo_gemini_model.blockSignals(True)
        self.combo_gemini_model.setCurrentIndex(idx_found)
        self.combo_gemini_model.blockSignals(False)
        self.lbl_active_model_badge.setText(f"Đang dùng: {label_found}")
        active_id = self._gemini_model_options[idx_found][1]
        for mid, btn in self._quick_model_btns.items():
            if mid == active_id:
                btn.setStyleSheet(f"PushButton {{ background: {Gradients.BLUE_PURPLE}; color: #FFFFFF; font-weight: 700; font-size: 11px; border: 1px solid #C4B5FD; border-radius: 7px; padding: 4px 10px; }}")
            else:
                btn.setStyleSheet(f"PushButton {{ background: #151B2E; color: {Colors.TEXT_SECONDARY}; font-weight: 600; font-size: 11px; border: 1px solid {Colors.BORDER}; border-radius: 7px; padding: 4px 10px; }}")
        if save_now and not self._is_loading:
            self.config["gemini_model"] = active_id
            set_config("gemini_model", active_id)

    def _loadConfigToUI(self):
        self.config = load_config()
        saved_model = self.config.get("gemini_model") or "gemini-4-argon"
        self._select_gemini_model(saved_model, save_now=False)
        keys = self.config.get("gemini_keys") or []
        self.txt_api_keys.setPlainText("\n".join(keys))
        self.line_tiktok_session.setText(self.config.get("tiktok_session_id") or "")
        self.line_output_dir.setText(self.config.get("output_dir") or os.path.join(os.getcwd(), "Output"))

    def _saveConfig(self, show_msg: bool = True):
        idx = self.combo_gemini_model.currentIndex()
        if 0 <= idx < len(self._gemini_model_options):
            self.config["gemini_model"] = self._gemini_model_options[idx][1]
        keys = [k.strip() for k in self.txt_api_keys.toPlainText().splitlines() if k.strip()]
        self.config["gemini_keys"] = keys
        self.config["tiktok_session_id"] = self.line_tiktok_session.text().strip()
        out_dir = self.line_output_dir.text().strip()
        if out_dir:
            self.config["output_dir"] = out_dir
        save_config(self.config)
        if show_msg:
            InfoBar.success("Đã lưu", "Cài đặt hệ thống đã được cập nhật.", parent=self, position=InfoBarPosition.TOP)

    def _browse_out_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Chọn thư mục lưu mặc định", self.line_output_dir.text().strip())
        if folder:
            self.line_output_dir.setText(folder)

    def _start_model_download(self):
        self.btn_download_models.setEnabled(False)
        self.dl_log.clear()
        self.dl_progress.setValue(10)
        self._dl_worker = ModelDownloaderWorker(self)
        self._dl_worker.progress.connect(self.dl_progress.setValue)
        self._dl_worker.log.connect(self.dl_log.appendPlainText)
        self._dl_worker.finished.connect(self._on_dl_finished)
        self._dl_worker.start()

    def _on_dl_finished(self, ok: bool, msg: str):
        self.btn_download_models.setEnabled(True)
        if ok:
            InfoBar.success("Hoàn tất", msg, parent=self, position=InfoBarPosition.TOP)
        else:
            InfoBar.warning("Thông báo", msg, parent=self, position=InfoBarPosition.TOP)

    def setLicenseInfo(self, status="premium", msg="Hikari Tsukimi — AI Dubbing Studio"):
        if hasattr(self, "lbl_license_status"):
            self.lbl_license_status.setText("✦ HIKARI TSUKIMI • AI Dubbing Studio")
            self.lbl_license_status.setStyleSheet("color: #34D399; font-weight: bold; font-size: 13px; letter-spacing: 0.5px;")

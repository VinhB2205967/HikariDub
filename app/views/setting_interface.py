"""
Setting Interface Module - Free Forever & Local-First Edition
Wraps SettingInterface and patches ModelDownloaderWorker to ensure
all child download subprocesses run with full PYTHONPATH and environment access.
"""

import os
import sys
import importlib.util

# Find base setting_interface.pyc
_pyc_path = None
for cand in [
    os.path.join(os.path.dirname(__file__), "setting_interface.pyc"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "pyc_dump", "app", "views", "setting_interface.pyc"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pyc_dump", "app", "views", "setting_interface.pyc"),
    r"D:\HikariDub\pyc_dump\app\views\setting_interface.pyc",
    r"D:\Hikari_Dub\pyc_dump\app\views\setting_interface.pyc",
]:
    if os.path.exists(cand):
        _pyc_path = cand
        break

if not _pyc_path:
    raise FileNotFoundError("Could not find base setting_interface.pyc")

_spec = importlib.util.spec_from_file_location("app.views.setting_interface_base", _pyc_path)
_base_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base_mod)

# Export all symbols from base module
for attr in dir(_base_mod):
    if not attr.startswith('__'):
        globals()[attr] = getattr(_base_mod, attr)

# 1. Hide the account page and show neutral product information.
_original_init_widget = _base_mod.SettingInterface._initWidget

def _init_widget_without_account(self):
    _original_init_widget(self)

    pivot = getattr(self, "pivot", None)
    if pivot is not None:
        acc_item = getattr(pivot, "items", {}).get("account")
        pivot.removeWidget("account")
        if acc_item is not None:
            acc_item.hide()
            acc_item.setParent(None)
            acc_item.deleteLater()

    stacked_widget = getattr(self, "stackedWidget", None)
    account_page = getattr(self, "page_account", None)
    if stacked_widget is not None and account_page is not None:
        stacked_widget.removeWidget(account_page)
        account_page.hide()
        account_page.setParent(None)

    # Ensure active tab indicator is synced to the first visible page
    if pivot is not None and getattr(pivot, "items", None):
        first_key = next(iter(pivot.items.keys()), None)
        if first_key:
            pivot.setCurrentItem(first_key)

    # Inject AI / Argon Model Selector into group_trans (API Settings section)
    try:
        from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
        from PyQt6.QtCore import Qt
        from qfluentwidgets import ComboBox, PushButton, BodyLabel
        from app.common.design_system import Colors, Gradients
        from app.common.config_manager import get_config, set_config, load_config, save_config

        gt = getattr(self, "group_trans", None)
        if gt is not None and gt.layout() is not None and not hasattr(self, "combo_gemini_model"):
            lay = gt.layout()

            model_box = QWidget(gt)
            model_box.setObjectName("hikariApiModelBox")
            model_box.setStyleSheet(f"""
                QWidget#hikariApiModelBox {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(99, 102, 241, 0.12), stop:1 rgba(6, 182, 212, 0.10));
                    border: 1px solid rgba(99, 102, 241, 0.35);
                    border-radius: 10px;
                }}
            """)
            mv = QVBoxLayout(model_box)
            mv.setContentsMargins(14, 10, 14, 12)
            mv.setSpacing(8)

            # Row 1: Title + Active Model Badge
            top_row = QHBoxLayout()
            top_row.setContentsMargins(0, 0, 0, 0)
            top_row.setSpacing(10)

            lbl_m_title = QLabel("🧠 Mô hình AI Dịch thuật (Model API):")
            lbl_m_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 700; font-size: 13px; background: transparent; border: none;")
            top_row.addWidget(lbl_m_title)

            self.lbl_active_model_badge = QLabel("Đang chọn: Gemini 4 Argon")
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

            # Row 2: Model Dropdown + Quick Select Model Buttons
            ctrl_row = QHBoxLayout()
            ctrl_row.setContentsMargins(0, 0, 0, 0)
            ctrl_row.setSpacing(8)

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

            # Quick-select buttons ("nút chọn mô hình")
            self._quick_model_btns = {}
            quick_specs = [
                ("⚡ Argon", "gemini-4-argon"),
                ("🚀 3.5 Flash", "gemini-3.5-flash"),
                ("💨 3.5 Lite", "gemini-3.5-flash-lite"),
                ("🆕 Latest", "gemini-flash-latest"),
                ("🔄 Auto", "auto"),
            ]
            for btn_txt, m_id in quick_specs:
                qb = PushButton(btn_txt, model_box)
                qb.setCursor(Qt.CursorShape.PointingHandCursor)
                qb.setFixedHeight(32)
                qb.clicked.connect(lambda checked=False, mid=m_id: self._select_gemini_model(mid, save_now=True))
                self._quick_model_btns[m_id] = qb
                ctrl_row.addWidget(qb)

            mv.addLayout(ctrl_row)

            lbl_hint = QLabel("💡 Hỗ trợ mô hình Argon và hệ sinh thái Gemini. Nếu mô hình đang chọn hết hạn mức RPM, hệ thống sẽ tự động chuyển đổi dự phòng để không làm gián đoạn bản dịch.")
            lbl_hint.setWordWrap(True)
            lbl_hint.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 11px; background: transparent; border: none;")
            mv.addWidget(lbl_hint)

            # Insert model_box right after SubtitleLabel (index 1) so it sits cleanly above API keys box
            insert_idx = 1 if lay.count() >= 1 else 0
            lay.insertWidget(insert_idx, model_box)

            def _update_quick_btn_styles(active_id: str):
                for mid, btn in getattr(self, "_quick_model_btns", {}).items():
                    if mid == active_id:
                        btn.setStyleSheet(f"""
                            PushButton {{
                                background: {Gradients.BLUE_PURPLE};
                                color: #FFFFFF;
                                font-weight: 700;
                                font-size: 11px;
                                border: 1px solid #C4B5FD;
                                border-radius: 7px;
                                padding: 4px 10px;
                            }}
                        """)
                    else:
                        btn.setStyleSheet(f"""
                            PushButton {{
                                background: #151B2E;
                                color: {Colors.TEXT_SECONDARY};
                                font-weight: 600;
                                font-size: 11px;
                                border: 1px solid {Colors.BORDER};
                                border-radius: 7px;
                                padding: 4px 10px;
                            }}
                            PushButton:hover {{
                                background: #1E2942;
                                color: {Colors.TEXT_PRIMARY};
                                border: 1px solid {Colors.PRIMARY};
                            }}
                        """)

            self._update_quick_btn_styles = _update_quick_btn_styles

            def _select_gemini_model(model_id: str, save_now: bool = False):
                _legacy_map = {
                    "argon": "gemini-4-argon", "gemini-argon": "gemini-4-argon",
                    "gemini-2.0-flash": "gemini-3.5-flash", "gemini-2.0-flash-lite": "gemini-3.5-flash-lite",
                    "gemini-1.5-flash": "gemini-flash-latest",
                }
                model_id = _legacy_map.get((model_id or "").strip().lower(), model_id)
                idx_found = 0
                label_found = "Argon"
                for idx_opt, (lbl_opt, mid_opt) in enumerate(self._gemini_model_options):
                    if mid_opt == model_id:
                        idx_found = idx_opt
                        label_found = lbl_opt.split("(")[0].strip()
                        break
                self.combo_gemini_model.blockSignals(True)
                self.combo_gemini_model.setCurrentIndex(idx_found)
                self.combo_gemini_model.blockSignals(False)
                if hasattr(self, "lbl_active_model_badge"):
                    self.lbl_active_model_badge.setText(f"Đang dùng: {label_found}")
                self._update_quick_btn_styles(self._gemini_model_options[idx_found][1])
                if save_now and not getattr(self, "_is_loading", False):
                    try:
                        chosen = self._gemini_model_options[idx_found][1]
                        if hasattr(self, "config") and isinstance(self.config, dict):
                            self.config["gemini_model"] = chosen
                        set_config("gemini_model", chosen)
                    except Exception:
                        pass

            self._select_gemini_model = _select_gemini_model

            def _on_combo_model_changed(idx: int):
                if 0 <= idx < len(self._gemini_model_options):
                    mid = self._gemini_model_options[idx][1]
                    self._select_gemini_model(mid, save_now=True)

            self.combo_gemini_model.currentIndexChanged.connect(_on_combo_model_changed)

            # Initialize with saved config (default 'argon')
            saved_model = get_config("gemini_model", "argon") or "argon"
            self._select_gemini_model(saved_model, save_now=False)
    except Exception as e:
        print(f"Lỗi khởi tạo bộ chọn mô hình API: {e}")

_base_mod.SettingInterface._initWidget = _init_widget_without_account

# Wrap _loadConfigToUI and _saveConfig so gemini_model is always loaded & saved with settings
_orig_load_config_ui = getattr(_base_mod.SettingInterface, "_loadConfigToUI", None)
if callable(_orig_load_config_ui):
    def _patched_load_config_ui(self, *args, **kwargs):
        res = _orig_load_config_ui(self)
        try:
            from app.common.config_manager import get_config
            saved_model = (getattr(self, "config", {}) or {}).get("gemini_model") or get_config("gemini_model", "argon") or "argon"
            if hasattr(self, "_select_gemini_model"):
                self._select_gemini_model(saved_model, save_now=False)
        except Exception:
            pass
        return res
    _base_mod.SettingInterface._loadConfigToUI = _patched_load_config_ui

_orig_save_config_ui = getattr(_base_mod.SettingInterface, "_saveConfig", None)
if callable(_orig_save_config_ui):
    def _patched_save_config_ui(self, show_msg=True, *args, **kwargs):
        try:
            if hasattr(self, "combo_gemini_model") and hasattr(self, "_gemini_model_options"):
                idx = self.combo_gemini_model.currentIndex()
                if 0 <= idx < len(self._gemini_model_options):
                    chosen = self._gemini_model_options[idx][1]
                    if hasattr(self, "config") and isinstance(self.config, dict):
                        self.config["gemini_model"] = chosen
                    from app.common.config_manager import set_config
                    set_config("gemini_model", chosen)
        except Exception:
            pass
        if isinstance(show_msg, bool):
            return _orig_save_config_ui(self, show_msg=show_msg)
        return _orig_save_config_ui(self)
    _base_mod.SettingInterface._saveConfig = _patched_save_config_ui

def _setLicenseInfo_patched(self, status="premium", msg="Hikari Tsukimi — AI Dubbing Studio"):
    if hasattr(self, 'lbl_license_status'):
        self.lbl_license_status.setText("✦ HIKARI TSUKIMI • AI Dubbing Studio")
        self.lbl_license_status.setStyleSheet("color: #34D399; font-weight: bold; font-size: 13px; letter-spacing: 0.5px;")

_base_mod.SettingInterface.setLicenseInfo = _setLicenseInfo_patched

# 2. Patch ModelDownloaderWorker._run_script to ensure child processes inherit PYTHONPATH & PATH
def _patched_run_script(self, python_exe, script):
    import subprocess
    import sys
    import os

    env = os.environ.copy()

    # Determine project root and _internal directory
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(curr_dir))
    if not os.path.exists(os.path.join(project_root, "_internal")):
        project_root = os.environ.get("HIKARI_ROOT", r"D:\HikariDub" if os.path.exists(r"D:\HikariDub") else (r"D:\Hikari_Dub" if os.path.exists(r"D:\Hikari_Dub") else curr_dir))
    internal_dir = os.path.join(project_root, "_internal")

    # Inject project root and _internal into PYTHONPATH
    py_paths = [project_root, internal_dir]
    if env.get("PYTHONPATH"):
        py_paths.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(py_paths)

    # Inject ffmpeg and DLL directories into PATH
    ffmpeg_dir = os.path.join(internal_dir, "ffmpeg")
    torch_lib = os.path.join(internal_dir, "torch", "lib")
    cuda_dirs = [
        os.path.join(internal_dir, "nvidia", "cublas", "bin"),
        os.path.join(internal_dir, "nvidia", "cudnn", "bin"),
        torch_lib,
        ffmpeg_dir,
    ]
    extra_paths = [p for p in cuda_dirs if os.path.exists(p)]
    if os.path.exists(ffmpeg_dir):
        env["BUNDLE_FFMPEG_DIR"] = ffmpeg_dir

    if extra_paths:
        env["PATH"] = os.pathsep.join(extra_paths) + os.pathsep + env.get("PATH", "")

    # Force UTF-8 encoding for child process streams
    env["PYTHONIOENCODING"] = "utf-8"

    # Inject cache directories
    models_dir = os.path.join(project_root, "models")
    env["HF_HOME"] = os.path.join(models_dir, "whisper")
    env["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
    env["HF_HUB_DISABLE_TELEMETRY"] = "1"
    env["KMP_DUPLICATE_LIB_OK"] = "TRUE"

    # Prepend numba safe caching to child script to prevent 'no locator available'
    numba_preamble = (
        "try:\n"
        "    import numba.core.dispatcher as ncd\n"
        "    _orig_ec = ncd.Dispatcher.enable_caching\n"
        "    def _safe_ec(self):\n"
        "        try: _orig_ec(self)\n"
        "        except Exception: self._cache = None\n"
        "    ncd.Dispatcher.enable_caching = _safe_ec\n"
        "except Exception: pass\n"
    )
    script = numba_preamble + script

    creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    process = subprocess.Popen(
        [python_exe, "-c", script],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        creationflags=creationflags
    )
    for line in process.stdout:
        if line:
            self.progress.emit(line.strip())
    process.wait()

_base_mod.ModelDownloaderWorker._run_script = _patched_run_script

# Re-assign patched classes to globals
SettingInterface = _base_mod.SettingInterface
ModelDownloaderWorker = _base_mod.ModelDownloaderWorker

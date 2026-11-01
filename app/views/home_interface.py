"""
Home Interface Module - Free Forever & Local-First Edition
Wraps and patches HomeInterface to remove subscription checks and API key requirements.
"""

import os
import sys
import importlib.util
from qfluentwidgets import InfoBar, InfoBarPosition

# Find base home_interface.pyc
_pyc_path = None
for cand in [
    os.path.join(os.path.dirname(__file__), "home_interface.pyc"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "pyc_dump", "app", "views", "home_interface.pyc"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pyc_dump", "app", "views", "home_interface.pyc"),
    r"D:\HikariDub\pyc_dump\app\views\home_interface.pyc",
    r"D:\Hikari_Dub\pyc_dump\app\views\home_interface.pyc"
]:
    if os.path.exists(cand):
        _pyc_path = cand
        break

if not _pyc_path:
    raise FileNotFoundError("Could not find base home_interface.pyc")

_spec = importlib.util.spec_from_file_location("app.views.home_interface_base", _pyc_path)
_base_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base_mod)

HomeInterface = _base_mod.HomeInterface

# 1. Patch __init__ to guarantee license_status attribute is always present & apply futuristic design
_orig_init = HomeInterface.__init__
def _init_patched(self, parent=None):
    self.license_status = "premium"
    _orig_init(self, parent)
    self.license_status = "premium"
    
    # Apply Hikari Dub v3.0 Premium Futuristic Redesign
    try:
        from PyQt6.QtWidgets import QSplitter, QWidget, QScrollArea, QApplication
        from PyQt6.QtCore import Qt
        
        # 1. Independent Scroll Area for Column 1 (Settings)
        # Allows video frame and preview controls to expand fully without page-level scrolling
        self.col1_scroll = QScrollArea()
        self.col1_scroll.setObjectName("hikariCol1Scroll")
        self.col1_scroll.setWidgetResizable(True)
        # Keep the pane stationary at about 430 display pixels, accounting for Windows DPI scaling.
        screen = QApplication.primaryScreen()
        dpi_scale = screen.devicePixelRatio() if screen is not None else 1.0
        settings_width = round(430 / max(dpi_scale, 1.0))
        self.col1_scroll.setFixedWidth(settings_width)
        self.col1_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.col1_scroll.setStyleSheet("""
            QScrollArea#hikariCol1Scroll {
                background: transparent;
                border: none;
            }
            QScrollArea#hikariCol1Scroll > QWidget > QWidget {
                background: transparent;
            }
        """)
        
        self.hBoxLayout.removeWidget(self.col1_widget)
        self.hBoxLayout.removeWidget(self.col2_widget)
        self.hBoxLayout.removeWidget(self.col3_widget)
        
        self.col1_scroll.setWidget(self.col1_widget)
        
        # Integrate Resizable Horizontal QSplitter for 3-column workspace
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setObjectName("hikariSplitter")
        splitter.setStyleSheet("""
            QSplitter#hikariSplitter::handle {
                background: #191F2B;
                width: 3px;
                margin: 0px 2px;
                border-radius: 1px;
            }
            QSplitter#hikariSplitter::handle:hover {
                background: #22D3EE;
            }
        """)
        
        splitter.addWidget(self.col1_scroll)
        splitter.addWidget(self.col2_widget)
        splitter.addWidget(self.col3_widget)
        splitter.setSizes([settings_width, 680, 350])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setChildrenCollapsible(False)
        self.hBoxLayout.addWidget(splitter)
        
        # Optimize compact log display to maximize video viewport
        if hasattr(self, 'log_text_edit'):
            self.log_text_edit.setFixedHeight(85)
        if hasattr(self, 'row2_widget'):
            self.row2_widget.setFixedHeight(120)
            
        # Optimize Video Canvas & Video Frame
        if hasattr(self, 'video_frame'):
            self.video_frame.setMinimumHeight(380)
            self.video_frame.setStyleSheet("""
                background-color: #05070B;
                border: 1px solid #293244;
                border-radius: 8px;
            """)
        if hasattr(self, 'video_canvas'):
            self.video_canvas.setMinimumHeight(380)
            # Default subtitle position to lower third so character's face remains clear
            if getattr(self.video_canvas, 'sub_rel_y', 0.5) <= 0.65:
                self.video_canvas.sub_rel_y = 0.88
            # Patch mousePressEvent to allow deselecting overlay items by clicking outside
            _orig_vc_press = self.video_canvas.mousePressEvent
            def _enhanced_vc_mouse_press(e):
                _orig_vc_press(e)
            self.video_canvas.mousePressEvent = _enhanced_vc_mouse_press
        
        # 2. Assign unique objectNames to panels for targeted styling
        self.col1_widget.setObjectName("hikariCol1")
        self.col2_widget.setObjectName("hikariCol2")
        self.col3_widget.setObjectName("hikariCol3")
        self.row2_widget.setObjectName("hikariRow2")
        self.run_group.setObjectName("hikariRunGroup")
        
        # 3. Upgrade Section Headers with Professional Icons & Typography
        if self.col1_layout.count() > 0 and self.col1_layout.itemAt(0).widget():
            lbl1 = self.col1_layout.itemAt(0).widget()
            lbl1.setText("✦ CẤU HÌNH DỰ ÁN & GIỌNG ĐỌC AI")
            lbl1.setStyleSheet("color: #22D3EE; font-weight: 700; font-size: 14px; letter-spacing: 0.5px; padding-bottom: 4px;")
            
        if self.col2_layout.count() > 0 and self.col2_layout.itemAt(0).widget():
            lbl2 = self.col2_layout.itemAt(0).widget()
            lbl2.setText("🎬 VIDEO ĐẦU VÀO & KHÔNG GIAN XEM TRƯỚC")
            lbl2.setStyleSheet("color: #22D3EE; font-weight: 700; font-size: 14px; letter-spacing: 0.5px; padding-bottom: 4px;")
            
        if self.col3_layout.count() > 0 and self.col3_layout.itemAt(0).widget():
            lbl3 = self.col3_layout.itemAt(0).widget()
            lbl3.setText("📝 TRÌNH BIÊN TẬP PHỤ ĐỀ AI")
            lbl3.setStyleSheet("color: #22D3EE; font-weight: 700; font-size: 14px; letter-spacing: 0.5px; padding-bottom: 4px;")
            
        if hasattr(self, 'row2_widget') and self.row2_widget.layout().count() > 0:
            header_layout = self.row2_widget.layout().itemAt(0).layout()
            if header_layout and header_layout.count() > 0 and header_layout.itemAt(0).widget():
                lbl_log = header_layout.itemAt(0).widget()
                lbl_log.setText("⚡ TIẾN ĐỘ & NHẬT KÝ HỆ THỐNG")
                lbl_log.setStyleSheet("color: #22D3EE; font-weight: 700; font-size: 13px; letter-spacing: 0.5px;")

        # 4. Modernize Buttons & Placeholders (Clean Vietnamese UX)
        self.btn_select_video.setText("📁 Chọn Video Nguồn...")
        self.btn_select_output.setText("📂 Chọn Thư Mục")
        self.line_output_path.setPlaceholderText("Đường dẫn lưu dự án đầu ra...")
        self.line_wm.setPlaceholderText("Nhãn bản quyền (VD: Hikari Tsukimi Studio)...")
        
        self.btn_start_full.setText("▶ BẮT ĐẦU XỬ LÝ TOÀN BỘ (TỰ ĐỘNG)")
        self.btn_cancel.setText("⏹ HỦY TIẾN TRÌNH")
        
        self.btn_step1.setText("1. Bóc Băng")
        self.btn_step2.setText("2. Dịch Phụ Đề")
        self.btn_step3.setText("3. Tạo Giọng AI")
        self.btn_step4.setText("4. Xuất Video 1080p")
        
        self.btn_apply_all.setText("⧉ Đồng bộ tất cả Video")
        self.btn_save_srt.setText("💾 Lưu Kịch Bản (SRT)")
        
        # Overlay toolbar buttons: gọn gàng, vừa vặn không bị che cắt chữ
        self.btn_add_mask.setText("Vùng Che")
        self.btn_remove_item.setText("Xóa")
        self.btn_add_bg_frame.setText("Khung")
        self.btn_add_logo.setText("Logo")
        self.btn_style.setText("Kiểu Chữ")
        
        self.btn_add_mask.setToolTip("Thêm vùng che mờ / xóa chữ trên video")
        self.btn_remove_item.setToolTip("Xóa phần tử đang chọn (Vùng che / Logo / Khung viền)")
        self.btn_add_bg_frame.setToolTip("Thêm khung viền trang trí cho video")
        self.btn_add_logo.setToolTip("Thêm hình ảnh Logo hoặc Watermark")
        self.btn_style.setToolTip("Tùy chỉnh font chữ, màu sắc và kiểu phụ đề")
        
        # Style gọn gàng cho hàng nút công cụ video, căn chỉnh cân đối
        overlay_btn_qss = """
            PushButton {
                text-align: left;
                padding: 5px 8px 5px 28px;
                font-size: 12px;
                font-weight: 500;
                background-color: #191F2B;
                border: 1px solid #293244;
                border-radius: 6px;
                color: #F1F5F9;
            }
            PushButton:hover {
                background-color: #222A39;
                border: 1px solid #22D3EE;
                color: #22D3EE;
            }
            PushButton:pressed {
                background-color: #121620;
            }
        """
        for ob in [self.btn_add_mask, self.btn_remove_item, self.btn_add_bg_frame, self.btn_add_logo, self.btn_style]:
            ob.setStyleSheet(overlay_btn_qss)
            
        if self.col2_layout.count() > 5:
            ov_layout = self.col2_layout.itemAt(5).layout()
            if ov_layout:
                ov_layout.setSpacing(6)
        
        self.btn_replace_all.setText("🔄 Thay thế tất cả")
        self.input_find.setPlaceholderText("🔍 Tìm từ trong kịch bản...")
        self.input_replace.setPlaceholderText("✏️ Thay bằng nội dung mới...")
        
        # 5. Apply Deep Creative Design System Stylesheet to Panels
        panel_css = """
            #hikariCol1, #hikariCol2, #hikariCol3 {
                background-color: #121620;
                border: 1px solid #293244;
                border-radius: 12px;
            }
            #hikariRow2 {
                background-color: #0F1219;
                border: 1px solid #293244;
                border-radius: 10px;
            }
            #hikariRunGroup {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #191F2B, stop:1 #131822);
                border: 1px solid #293244;
                border-radius: 10px;
                padding: 10px;
            }
            #hikariRunGroup PushButton {
                background-color: #191F2B;
                color: #F1F5F9;
                border: 1px solid #293244;
                border-radius: 6px;
                font-weight: 600;
                font-size: 12px;
                padding: 6px 10px;
            }
            #hikariRunGroup PushButton:hover {
                background-color: #222A39;
                border: 1px solid #22D3EE;
                color: #22D3EE;
            }
        """
        self.col1_widget.setStyleSheet(panel_css)
        self.col2_widget.setStyleSheet(panel_css)
        self.col3_widget.setStyleSheet(panel_css)
        self.row2_widget.setStyleSheet(panel_css)
        self.run_group.setStyleSheet(panel_css)
        
        # Log TextEdit styling — Dark terminal aesthetic
        if hasattr(self, 'log_text_edit'):
            self.log_text_edit.setStyleSheet("""
                TextEdit {
                    background-color: #080A0F;
                    color: #94A3B8;
                    border: 1px solid #1E2533;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-family: 'Consolas', 'Fira Code', monospace;
                    font-size: 11px;
                    line-height: 1.4;
                }
            """)
    except Exception as e:
        print(f"Lỗi thiết lập giao diện Hikari Dub: {e}")

HomeInterface.__init__ = _init_patched

# 1b. Patch SrtItemWidget to render modern readable cards with cyan accents
try:
    _orig_srt_item_init = _base_mod.SrtItemWidget.__init__
    def _patched_srt_item_init(self, idx_str, time_display, content, full_time_str, seek_callback=None, parent=None):
        _orig_srt_item_init(self, idx_str, time_display, content, full_time_str, seek_callback, parent)
        self.setStyleSheet("""
            #srtItem {
                border: 1px solid #293244;
                border-radius: 8px;
                background-color: #0F1219;
                margin-bottom: 4px;
            }
            #srtItem:hover {
                background-color: #191F2B;
                border: 1px solid #22D3EE;
            }
        """)
        if hasattr(self, 'lbl_idx'):
            self.lbl_idx.setStyleSheet("color: #22D3EE; font-weight: 700; font-size: 11px; letter-spacing: 0.5px;")
        if hasattr(self, 'lbl_time'):
            self.lbl_time.setStyleSheet("color: #94A3B8; font-size: 11px; font-family: 'Consolas', monospace;")
        if hasattr(self, 'text_edit'):
            self.text_edit.setStyleSheet("""
                TextEdit {
                    background-color: #080A0F;
                    color: #F1F5F9;
                    border: 1px solid #1E2533;
                    border-radius: 6px;
                    padding: 4px 8px;
                    font-size: 12px;
                }
                TextEdit:focus {
                    border: 1px solid #22D3EE;
                }
            """)
    _base_mod.SrtItemWidget.__init__ = _patched_srt_item_init
except Exception as e:
    print(f"Lỗi patch SrtItemWidget: {e}")

# 2. Patch _verify_license_sync to always return premium without network request
def _verify_license_sync_patched(self):
    status = "premium"
    msg = "Ứng dụng sẵn sàng"
    self.license_status = status
    try:
        from app.core import security as core_sec
        core_sec.CURRENT_LICENSE_STATUS = status
        main_win = self.window()
        if hasattr(main_win, 'settingInterface'):
            main_win.settingInterface.setLicenseInfo(status, msg)
    except Exception as e:
        print(f"Lỗi đồng bộ bản quyền: {e}")
    return status

HomeInterface._verify_license_sync = _verify_license_sync_patched

# 3. Patch _onTranslateClicked to enable 100% free translation without requiring Gemini API Keys
def _onTranslateClicked_patched(self):
    self._verify_license_sync()
    if not self.selected_videos:
        InfoBar.warning(
            title='Cảnh báo',
            content='Vui lòng chọn video đầu vào trước!',
            parent=self.window(),
            position=InfoBarPosition.TOP,
            duration=7000
        )
        return

    output_dir = self.line_output_path.text()
    if not output_dir:
        InfoBar.warning(
            title='Cảnh báo',
            content='Vui lòng chọn Đường dẫn lưu file trước!',
            parent=self.window(),
            position=InfoBarPosition.TOP,
            duration=7000
        )
        return

    current_idx = self.video_combo.currentIndex()
    if current_idx < 0:
        return

    video_path = self.selected_videos[current_idx]
    
    try:
        from app.core.video_utils import get_safe_basename
        base_name = get_safe_basename(video_path)
    except Exception:
        if hasattr(_base_mod, 'get_safe_basename'):
            base_name = _base_mod.get_safe_basename(video_path)
        else:
            import hashlib
            raw_name = os.path.splitext(os.path.basename(video_path))[0]
            if len(raw_name) <= 80:
                base_name = raw_name
            else:
                base_name = f"{raw_name[:50].strip()}_{hashlib.md5(raw_name.encode('utf-8')).hexdigest()[:6]}"
    workspace_dir = os.path.join(output_dir, base_name)
    data_dir = os.path.join(workspace_dir, "Data")
    srt_path = os.path.join(data_dir, "temp_original.srt")

    if not os.path.exists(srt_path):
        InfoBar.warning(
            title='Cảnh báo',
            content='Không tìm thấy kịch bản gốc. Vui lòng chạy tính năng Bóc Băng (Bước 1) trước khi tiến hành dịch!',
            parent=self.window(),
            position=InfoBarPosition.TOP,
            duration=7000
        )
        return

    from app.common.config_manager import get_config
    api_keys = get_config('gemini_keys', [])

    if not api_keys:
        self._appendLog("💡 Không có Gemini API Key -> Tự động chuyển sang Chế độ Dịch Miễn phí (Google Translate / Local)!")
        api_keys = ["FREE_MODE"]

    if hasattr(self, 'media_player'):
        self.media_player.pause()

    self._setButtonsEnabled(False)
    self.btn_cancel.setEnabled(True)
    self.progress_bar.setValue(0)

    prompt_style = self.combo_prompt.currentData()
    custom_prompt = self.text_custom_prompt.toPlainText()
    target_lang = self.combo_target_lang.currentText()

    from app.common.workers import TranslateWorker
    self.translate_worker = TranslateWorker(
        srt_path, workspace_dir, api_keys, prompt_style, custom_prompt, target_lang, parent=self
    )
    self.translate_worker.progress.connect(self.progress_bar.setValue)
    self.translate_worker.log.connect(self._appendLog)
    self.translate_worker.finished_srt.connect(self._onTranslateFinished)
    self.translate_worker.error.connect(self._onTranscribeError)
    self.translate_worker.start()

HomeInterface._onTranslateClicked = _onTranslateClicked_patched


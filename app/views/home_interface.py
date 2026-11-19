"""
Home Interface Module - Free Forever & Local-First Edition
Wraps and patches HomeInterface to remove subscription checks and API key requirements.
Includes Canvas Aspect Ratio, Zoom & Video Transform controls (v3.1).
"""

import os
import sys
import importlib.util
from qfluentwidgets import InfoBar, InfoBarPosition

# Load pure-Python base HomeInterface (no .pyc dependency)
import app.views.home_interface_base as _base_mod

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
        # Compact, sleek sidebar width so all buttons and labels fit without wasting space
        settings_width = 330
        self.col1_scroll.setFixedWidth(settings_width)
        self.col1_widget.setMinimumWidth(0)
        self.col1_widget.setMaximumWidth(settings_width)
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

        # Pin run_group at the bottom of Column 1 outside col1_scroll so CTA buttons are always visible
        from PyQt6.QtWidgets import QVBoxLayout, QSizePolicy
        self.col1_container = QWidget()
        self.col1_container.setObjectName("hikariCol1Container")
        self.col1_container.setFixedWidth(settings_width)
        self.col1_container.setStyleSheet("#hikariCol1Container { background: transparent; border: none; }")
        col1_vbox = QVBoxLayout(self.col1_container)
        col1_vbox.setContentsMargins(0, 0, 0, 0)
        col1_vbox.setSpacing(6)

        self.col1_scroll.setWidget(self.col1_widget)
        col1_vbox.addWidget(self.col1_scroll, 1)

        if hasattr(self, 'run_group'):
            self.col1_layout.removeWidget(self.run_group)
            rg_lay = self.run_group.layout()
            if rg_lay:
                rg_lay.setContentsMargins(12, 10, 12, 10)
                rg_lay.setSpacing(6)
            col1_vbox.addWidget(self.run_group, 0)

            # Style start button to ensure prominent gradient CTA that never clips
            btn_start = rg_lay.itemAt(0).widget() if rg_lay else None
            if btn_start:
                btn_start.setFixedHeight(38)
                btn_start.setStyleSheet("""
                    QPushButton, PrimaryPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366F1, stop:0.5 #8B5CF6, stop:1 #EC4899);
                        color: #FFFFFF;
                        font-weight: 800;
                        font-size: 12px;
                        letter-spacing: 0.4px;
                        border: 1px solid #C084FC;
                        border-radius: 8px;
                        padding: 6px 12px;
                        text-align: center;
                    }
                    QPushButton:hover, PrimaryPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #818CF8, stop:0.5 #A78BFA, stop:1 #F472B6);
                        border: 1px solid #F9A8D4;
                        color: #FFFFFF;
                    }
                    QPushButton:pressed, PrimaryPushButton:pressed {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4F46E5, stop:0.5 #7C3AED, stop:1 #DB2777);
                    }
                    QPushButton:disabled, PrimaryPushButton:disabled {
                        background: #141B2D;
                        color: #475569;
                        border: 1px solid #1E2942;
                    }
                """)

            # Style the 4 manual step buttons in the 2x2 grid for generous width and zero clipping
            grid_item = rg_lay.itemAt(2) if rg_lay else None
            if grid_item and grid_item.layout():
                gl = grid_item.layout()
                gl.setHorizontalSpacing(8)
                gl.setVerticalSpacing(6)
                for bi in range(gl.count()):
                    w = gl.itemAt(bi).widget()
                    if w:
                        w.setFixedHeight(32)
                        w.setStyleSheet("""
                            QPushButton, PushButton {
                                background: #141C2E;
                                border: 1px solid #25334D;
                                border-radius: 6px;
                                color: #E2E8F0;
                                font-weight: 700;
                                font-size: 11.5px;
                                padding: 4px 8px;
                            }
                            QPushButton:hover, PushButton:hover {
                                background: #1E2942;
                                border-color: #22D3EE;
                                color: #FFFFFF;
                            }
                            QPushButton:pressed, PushButton:pressed {
                                background: #0F172A;
                            }
                        """)

            # Style cancel button
            btn_cancel = rg_lay.itemAt(4).widget() if rg_lay and rg_lay.count() > 4 else None
            if btn_cancel:
                btn_cancel.setFixedHeight(28)
                btn_cancel.setStyleSheet("""
                    QPushButton, PushButton {
                        background: rgba(239, 68, 68, 0.12);
                        border: 1px solid rgba(239, 68, 68, 0.35);
                        border-radius: 6px;
                        color: #F87171;
                        font-weight: 700;
                        font-size: 11px;
                        padding: 4px 8px;
                    }
                    QPushButton:hover, PushButton:hover {
                        background: rgba(239, 68, 68, 0.22);
                        border-color: #EF4444;
                        color: #FEF2F2;
                    }
                """)

        # Integrate Resizable Horizontal QSplitter for 3-column workspace with prioritized center
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

        splitter.addWidget(self.col1_container)
        splitter.addWidget(self.col2_widget)
        splitter.addWidget(self.col3_widget)
        splitter.setSizes([settings_width, 740, 280])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setChildrenCollapsible(False)
        self.hBoxLayout.addWidget(splitter)
        self.workspace_splitter = splitter

        # Optimize log display & viewport heights: clearly visible (150px) with smooth vertical scroll
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        if hasattr(self, 'vBoxLayout'):
            self.vBoxLayout.setContentsMargins(10, 4, 10, 4)
            self.vBoxLayout.setSpacing(6)
        if hasattr(self, 'log_text_edit'):
            self.log_text_edit.setFixedHeight(105)
            self.log_text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.log_text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            if hasattr(self.log_text_edit, 'scrollDelegate'):
                self.log_text_edit.scrollDelegate.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.log_text_edit.setStyleSheet("""
                QTextEdit, QPlainTextEdit, TextEdit {
                    background-color: #080D1A;
                    border: 1px solid #1E293B;
                    border-radius: 6px;
                    color: #94A3B8;
                    font-family: 'Consolas', 'Segoe UI', monospace;
                    font-size: 11.5px;
                    line-height: 1.45;
                    padding: 6px 8px;
                }
                QTextEdit:focus, QPlainTextEdit:focus, TextEdit:focus {
                    border: 1px solid #6366F1;
                }
                QScrollBar:vertical {
                    background: #080D1A;
                    width: 10px;
                    margin: 2px 2px 2px 0px;
                    border-radius: 5px;
                }
                QScrollBar::handle:vertical {
                    background: #334155;
                    min-height: 24px;
                    border-radius: 5px;
                }
                QScrollBar::handle:vertical:hover {
                    background: #22D3EE;
                }
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    height: 0px;
                    background: none;
                }
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                    background: none;
                }
            """)
        if hasattr(self, 'row2_widget'):
            self.row2_widget.setFixedHeight(150)
            if self.row2_widget.layout():
                r2_lay = self.row2_widget.layout()
                r2_lay.setContentsMargins(12, 6, 12, 6)
                r2_lay.setSpacing(5)

        # Optimize Video Workspace & Canvas for MAXIMUM viewing area
        if hasattr(self, 'video_frame'):
            self.video_frame.setMinimumHeight(220)
            self.video_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.video_frame.setStyleSheet("""
                background: transparent;
                border: none;
            """)
            if self.video_frame.layout():
                self.video_frame.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Optimize col2 vertical stretch so video_frame expands to fill available height
        if hasattr(self, 'col2_widget') and self.col2_widget.layout():
            c2_lay = self.col2_widget.layout()
            c2_lay.setSpacing(4)
            c2_lay.setContentsMargins(10, 6, 10, 6)
            for i in range(c2_lay.count()):
                it = c2_lay.itemAt(i)
                if it and it.widget() is getattr(self, 'video_frame', None):
                    c2_lay.setStretch(i, 50)
                else:
                    c2_lay.setStretch(i, 0)

        if hasattr(self, 'video_canvas'):
            self.video_canvas.setStyleSheet("""
                background-color: #000000;
                border: 1px solid #293244;
                border-radius: 8px;
            """)
            # Default subtitle position to lower third so character's face remains clear
            if getattr(self.video_canvas, 'sub_rel_y', 0.5) <= 0.65:
                self.video_canvas.sub_rel_y = 0.88
            _orig_vc_press = self.video_canvas.mousePressEvent
            def _enhanced_vc_mouse_press(e):
                _orig_vc_press(e)
            self.video_canvas.mousePressEvent = _enhanced_vc_mouse_press
        
        # 2. Assign unique objectNames to panels for targeted styling & hover glow
        self.col1_widget.setObjectName("hikariCol1")
        self.col2_widget.setObjectName("hikariCol2")
        self.col3_widget.setObjectName("hikariCol3")
        self.row2_widget.setObjectName("hikariRow2")
        self.run_group.setObjectName("hikariRunGroup")

        from app.common.design_system import Colors, Gradients
        from app.components.modern_effects import (
            attach_hover_glow, install_stacked_fade_transition, AnimatedStatusBadge
        )

        for card_w in (self.col1_widget, self.col2_widget, self.col3_widget, self.row2_widget, self.run_group):
            attach_hover_glow(card_w)

        if hasattr(self, 'srt_stacked_widget'):
            install_stacked_fade_transition(self.srt_stacked_widget)

        # Upgrade Splitter handle with Electric Blue -> Cyan hover glow
        splitter.setStyleSheet(f"""
            QSplitter#hikariSplitter::handle {{
                background: {Colors.BORDER};
                width: 3px;
                margin: 4px 2px;
                border-radius: 1px;
            }}
            QSplitter#hikariSplitter::handle:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {Colors.ACCENT_BRIGHT}, stop:0.5 {Colors.PRIMARY}, stop:1 {Colors.HIGHLIGHT});
            }}
        """)

        # 3. Upgrade Section Headers with Modern SaaS Typography & Accent Styling
        section_header_qss = f"""
            color: {Colors.TEXT_PRIMARY};
            font-weight: 800;
            font-size: 13px;
            letter-spacing: 0.6px;
            padding-bottom: 4px;
            border-bottom: 1px solid {Colors.BORDER_SUBTLE};
        """
        if self.col1_layout.count() > 0 and self.col1_layout.itemAt(0).widget():
            lbl1 = self.col1_layout.itemAt(0).widget()
            lbl1.setText("✦ CẤU HÌNH DỰ ÁN & GIỌNG ĐỌC AI")
            lbl1.setStyleSheet(section_header_qss)

        if self.col2_layout.count() > 0 and self.col2_layout.itemAt(0).widget():
            lbl2 = self.col2_layout.itemAt(0).widget()
            lbl2.setText("🎬 VIDEO ĐẦU VÀO & KHÔNG GIAN XEM TRƯỚC")
            lbl2.setStyleSheet(section_header_qss)

        if self.col3_layout.count() > 0 and self.col3_layout.itemAt(0).widget():
            lbl3 = self.col3_layout.itemAt(0).widget()
            lbl3.setText("📝 TRÌNH BIÊN TẬP PHỤ ĐỀ AI")
            lbl3.setStyleSheet(section_header_qss)

        if hasattr(self, 'row2_widget') and self.row2_widget.layout().count() > 0:
            header_layout = self.row2_widget.layout().itemAt(0).layout()
            if header_layout and header_layout.count() > 0 and header_layout.itemAt(0).widget():
                lbl_log = header_layout.itemAt(0).widget()
                lbl_log.setText("⚡ TIẾN ĐỘ & NHẬT KÝ HỆ THỐNG")
                lbl_log.setStyleSheet(f"color: {Colors.ACCENT_BRIGHT}; font-weight: 800; font-size: 12px; letter-spacing: 0.5px;")
                # Add Live Status Pill Badge to the Progress/Log header row
                if not hasattr(self, '_log_status_badge'):
                    self._log_status_badge = AnimatedStatusBadge("Sẵn sàng xử lý", "ready", self.row2_widget)
                    header_layout.insertWidget(1, self._log_status_badge)

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

        # Upgrade Phong cách Dịch (combo_prompt) with rich Vietnamese dubbing presets
        if hasattr(self, 'combo_prompt'):
            try:
                from app.common.config_manager import get_config
                cur_style = get_config('prompt_style', 'Mặc định') or 'Mặc định'
                self.combo_prompt.blockSignals(True)
                self.combo_prompt.clear()
                style_items = [
                    ("✨ Tự nhiên / Đời thường (Khuyên dùng)", "Mặc định"),
                    ("🔥 Khẩu ngữ Viral TikTok / Douyin", "Đời thường"),
                    ("😂 Tấu hài / Cà khịa / Lầy lội", "Tấu hài"),
                    ("🎬 Kể chuyện / Review Phim kịch tính", "Review"),
                    ("🎭 Điện ảnh / Chính kịch chuẩn xác", "Nghiêm túc"),
                    ("⚔️ Cổ trang / Tiên hiệp / Kiếm hiệp", "Cổ trang"),
                    ("✍️ Tùy chỉnh (Tự nhập yêu cầu riêng)", "Tùy chỉnh"),
                ]
                sel_idx = 0
                for idx_s, (label_s, data_s) in enumerate(style_items):
                    self.combo_prompt.addItem(label_s, userData=data_s)
                    if data_s == cur_style:
                        sel_idx = idx_s
                self.combo_prompt.setCurrentIndex(sel_idx)
                self.combo_prompt.blockSignals(False)
            except Exception:
                try:
                    self.combo_prompt.blockSignals(False)
                except Exception:
                    pass

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

        # Style gọn gàng cho hàng nút công cụ video, căn chỉnh cân đối với hiệu ứng Gradient Hover
        overlay_btn_qss = f"""
            PushButton {{
                text-align: left;
                padding: 5px 10px 5px 28px;
                font-size: 12px;
                font-weight: 600;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1C253E, stop:1 #141B2E);
                border: 1px solid {Colors.BORDER};
                border-radius: 7px;
                color: {Colors.TEXT_PRIMARY};
            }}
            PushButton:hover {{
                background: {Gradients.BLUE_PURPLE};
                border: 1px solid #A78BFA;
                color: #FFFFFF;
            }}
            PushButton:pressed {{
                background: {Colors.PRIMARY_PRESSED};
            }}
        """
        for ob in [self.btn_add_mask, self.btn_remove_item, self.btn_add_bg_frame, self.btn_add_logo, self.btn_style]:
            ob.setStyleSheet(overlay_btn_qss)

        # Style khusus cho nút Xóa trên thanh công cụ video (Danger hover)
        self.btn_remove_item.setStyleSheet(f"""
            PushButton {{
                text-align: left;
                padding: 5px 10px 5px 28px;
                font-size: 12px;
                font-weight: 600;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #231829, stop:1 #181322);
                border: 1px solid rgba(236, 72, 153, 0.45);
                border-radius: 7px;
                color: #F9A8D4;
            }}
            PushButton:hover {{
                background: {Gradients.DANGER_GRAD};
                border: 1px solid #F472B6;
                color: #FFFFFF;
            }}
        """)

        if self.col2_layout.count() > 5:
            ov_layout = self.col2_layout.itemAt(5).layout()
            if ov_layout:
                ov_layout.setSpacing(6)

        self.btn_replace_all.setText("🔄 Thay thế tất cả")
        self.input_find.setPlaceholderText("🔍 Tìm từ trong kịch bản...")
        self.input_replace.setPlaceholderText("✏️ Thay bằng nội dung mới...")

        # 4b. Add "Dán Transcript" & "Tải File SRT/TXT" buttons in Column 3 (Subtitle Editor)
        if not hasattr(self, 'btn_paste_transcript') and hasattr(self, 'col3_layout'):
            from PyQt6.QtWidgets import QHBoxLayout
            from qfluentwidgets import PushButton
            import_row = QHBoxLayout()
            import_row.setContentsMargins(0, 2, 0, 2)
            import_row.setSpacing(6)

            self.btn_paste_transcript = PushButton("📋 Dán Transcript", self.col3_widget)
            self.btn_paste_transcript.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn_paste_transcript.setToolTip("Dán nhanh kịch bản SRT hoặc văn bản để tạo giọng đọc AI ngay mà không cần dịch lại")
            self.btn_paste_transcript.setStyleSheet(f"""
                PushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(99, 102, 241, 0.24), stop:1 rgba(139, 92, 246, 0.24));
                    color: {Colors.TEXT_PRIMARY};
                    font-weight: 700;
                    font-size: 12px;
                    border: 1px solid {Colors.PRIMARY};
                    border-radius: 7px;
                    padding: 6px 10px;
                }}
                PushButton:hover {{
                    background: {Gradients.BLUE_PURPLE};
                    color: #FFFFFF;
                    border: 1px solid #C4B5FD;
                }}
            """)
            self.btn_paste_transcript.clicked.connect(self._open_paste_transcript_dialog)

            self.btn_upload_transcript = PushButton("📂 Tải File SRT", self.col3_widget)
            self.btn_upload_transcript.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn_upload_transcript.setToolTip("Tải file phụ đề (.srt, .txt, .vtt) từ máy tính lên trình biên tập")
            self.btn_upload_transcript.setStyleSheet(f"""
                PushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(6, 182, 212, 0.20), stop:1 rgba(99, 102, 241, 0.20));
                    color: {Colors.ACCENT_BRIGHT};
                    font-weight: 700;
                    font-size: 12px;
                    border: 1px solid rgba(6, 182, 212, 0.55);
                    border-radius: 7px;
                    padding: 6px 10px;
                }}
                PushButton:hover {{
                    background: {Gradients.CYAN_BLUE};
                    color: #FFFFFF;
                    border: 1px solid #67E8F9;
                }}
            """)
            self.btn_upload_transcript.clicked.connect(self._open_upload_transcript_dialog)

            import_row.addWidget(self.btn_paste_transcript, 1)
            import_row.addWidget(self.btn_upload_transcript, 1)

            # Insert right above SegmentedWidget (Kịch bản Gốc | Kịch bản Dịch)
            insert_pos = 2 if self.col3_layout.count() >= 2 else self.col3_layout.count()
            self.col3_layout.insertLayout(insert_pos, import_row)

        # 5. Apply Modern SaaS Gradient Hierarchy to Action Buttons
        # Hero CTA: Indigo -> Violet -> Pink
        self.btn_start_full.setStyleSheet(f"""
            PrimaryPushButton, PushButton {{
                background: {Gradients.INDIGO_VIOLET_PINK};
                color: #FFFFFF;
                font-weight: 800;
                font-size: 12px;
                letter-spacing: 0.4px;
                border: 1px solid #C084FC;
                border-radius: 8px;
                padding: 8px 14px;
            }}
            PrimaryPushButton:hover, PushButton:hover {{
                background: {Gradients.INDIGO_VIOLET_PINK_HOVER};
                border: 1px solid #F9A8D4;
                color: #FFFFFF;
            }}
            PrimaryPushButton:pressed, PushButton:pressed {{
                background: {Gradients.INDIGO_VIOLET_PINK_PRESSED};
            }}
            PrimaryPushButton:disabled, PushButton:disabled {{
                background: #141B2D;
                color: #475569;
                border: 1px solid #1E2942;
            }}
        """)

        # Step 1-4 Buttons: Surface -> Blue/Purple Gradient on Hover
        step_btn_qss = f"""
            PushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1D2640, stop:1 #151C30);
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid #2A3759;
                border-radius: 7px;
                font-weight: 700;
                font-size: 12px;
                padding: 6px 10px;
            }}
            PushButton:hover {{
                background: {Gradients.CYAN_BLUE};
                border: 1px solid #38BDF8;
                color: #FFFFFF;
            }}
            PushButton:pressed {{
                background: {Colors.PRIMARY_PRESSED};
            }}
            PushButton:disabled {{
                background: #121726;
                color: #475569;
                border: 1px solid #1C243B;
            }}
        """
        for sb in [self.btn_step1, self.btn_step2, self.btn_step3, self.btn_step4]:
            sb.setStyleSheet(step_btn_qss)

        # Cancel Button: Rose -> Pink Danger Gradient
        self.btn_cancel.setStyleSheet(f"""
            PushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(239, 68, 68, 0.28), stop:1 rgba(236, 72, 153, 0.28));
                color: #FDA4AF;
                font-weight: 700;
                font-size: 12px;
                border: 1px solid rgba(244, 63, 94, 0.6);
                border-radius: 7px;
                padding: 6px 12px;
            }}
            PushButton:hover {{
                background: {Gradients.DANGER_GRAD};
                color: #FFFFFF;
                border: 1px solid #F472B6;
            }}
            PushButton:disabled {{
                background: #121726;
                color: #475569;
                border: 1px solid #1C243B;
            }}
        """)

        # Save SRT & Select Video Featured Buttons
        self.btn_save_srt.setStyleSheet(f"""
            PrimaryPushButton, PushButton {{
                background: {Gradients.BLUE_PURPLE};
                color: #FFFFFF;
                font-weight: 700;
                font-size: 12px;
                border: 1px solid #818CF8;
                border-radius: 8px;
                padding: 7px 14px;
            }}
            PrimaryPushButton:hover, PushButton:hover {{
                background: {Gradients.BLUE_PURPLE_HOVER};
                border: 1px solid #C4B5FD;
                color: #FFFFFF;
            }}
        """)

        self.btn_select_video.setStyleSheet(f"""
            PushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(99, 102, 241, 0.22), stop:1 rgba(6, 182, 212, 0.22));
                color: {Colors.TEXT_PRIMARY};
                font-weight: 700;
                border: 1px solid {Colors.PRIMARY};
                border-radius: 8px;
                padding: 6px 12px;
            }}
            PushButton:hover {{
                background: {Gradients.CYAN_BLUE};
                color: #FFFFFF;
                border: 1px solid #38BDF8;
            }}
        """)

        # Clear old inline panel stylesheet so patched CardWidget.paintEvent renders glassmorphic surface
        for panel_w in (self.col1_widget, self.col2_widget, self.col3_widget, self.row2_widget, self.run_group):
            panel_w.setStyleSheet("")

        # Value Badges for Audio Volume & Speed sliders
        badge_val_qss = f"""
            color: {Colors.ACCENT_BRIGHT};
            font-weight: 700;
            font-size: 12px;
            font-family: 'Consolas', monospace;
        """
        for val_lbl in ('lbl_voice_val', 'lbl_speed_val', 'lbl_extra_bgm_val', 'lbl_bgm_val', 'lbl_time', 'lbl_page_info'):
            if hasattr(self, val_lbl):
                getattr(self, val_lbl).setStyleSheet(badge_val_qss)

        # Log TextEdit styling — Deep Dark Navy Console aesthetic with visible smooth scrollbar
        if hasattr(self, 'log_text_edit'):
            self.log_text_edit.setStyleSheet(f"""
                TextEdit, QTextEdit, QPlainTextEdit {{
                    background-color: {Colors.BG_DEEP};
                    color: {Colors.TEXT_SECONDARY};
                    border: 1px solid {Colors.BORDER};
                    border-radius: 8px;
                    padding: 6px 10px;
                    font-family: 'Consolas', 'Fira Code', 'Segoe UI Mono', monospace;
                    font-size: 11.5px;
                    line-height: 1.45;
                }}
                TextEdit:focus, QTextEdit:focus {{
                    border: 1px solid {Colors.PRIMARY};
                }}
                QScrollBar:vertical {{
                    background: {Colors.BG_DEEP};
                    width: 10px;
                    margin: 2px 2px 2px 0px;
                    border-radius: 5px;
                }}
                QScrollBar::handle:vertical {{
                    background: #334155;
                    min-height: 24px;
                    border-radius: 5px;
                }}
                QScrollBar::handle:vertical:hover {{
                    background: #22D3EE;
                }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                    height: 0px;
                    background: none;
                }}
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                    background: none;
                }}
            """)
    except Exception as e:
        print(f"Lỗi thiết lập giao diện Hikari Dub: {e}")

HomeInterface.__init__ = _init_patched

# 1b. Patch SrtItemWidget to render modern SaaS cards with Electric Blue & Cyan accents
try:
    _orig_srt_item_init = _base_mod.SrtItemWidget.__init__
    def _patched_srt_item_init(self, idx_str, time_display, content, full_time_str, seek_callback=None, parent=None):
        _orig_srt_item_init(self, idx_str, time_display, content, full_time_str, seek_callback, parent)
        self.setStyleSheet("""
            #srtItem {
                border: 1px solid #242F4B;
                border-radius: 9px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #161E33, stop:1 #111728);
                margin-bottom: 5px;
            }
            #srtItem:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1D2744, stop:1 #221F44);
                border: 1px solid #6366F1;
            }
        """)
        if hasattr(self, 'lbl_idx'):
            self.lbl_idx.setStyleSheet("""
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(99, 102, 241, 0.28), stop:1 rgba(139, 92, 246, 0.28));
                color: #22D3EE;
                font-weight: 800;
                font-size: 11px;
                padding: 2px 7px;
                border-radius: 5px;
                border: 1px solid rgba(99, 102, 241, 0.5);
            """)
        if hasattr(self, 'lbl_time'):
            self.lbl_time.setStyleSheet("color: #94A3B8; font-size: 11px; font-family: 'Consolas', monospace; font-weight: 600;")
        if hasattr(self, 'text_edit'):
            self.text_edit.setStyleSheet("""
                TextEdit {
                    background-color: #070B16;
                    color: #F8FAFC;
                    border: 1px solid #1E2942;
                    border-radius: 7px;
                    padding: 5px 9px;
                    font-size: 12px;
                }
                TextEdit:hover {
                    border: 1px solid #6366F1;
                }
                TextEdit:focus {
                    border: 1px solid #06B6D4;
                    background-color: #050811;
                }
            """)
    _base_mod.SrtItemWidget.__init__ = _patched_srt_item_init

    # Patch SrtListWidget.paintEvent to render a Modern SaaS Empty State when no SRT blocks are loaded
    _orig_srt_list_paint = _base_mod.SrtListWidget.paintEvent
    def _patched_srt_list_paint(self, event):
        _orig_srt_list_paint(self, event)
        try:
            has_items = bool(getattr(self, 'srt_data', None) or getattr(self, 'blocks', None) or (self.layout() and self.layout().count() > 1))
            if not has_items:
                from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QLinearGradient, QBrush
                from PyQt6.QtCore import QRectF, Qt
                p = QPainter(self)
                p.setRenderHint(QPainter.RenderHint.Antialiasing)
                w, h = float(self.width()), float(self.height())
                if w > 120 and h > 120:
                    card_w = min(w - 24.0, 280.0)
                    card_h = 136.0
                    rx = (w - card_w) / 2.0
                    ry = max(24.0, (h - card_h) / 2.0 - 10.0)
                    rect = QRectF(rx, ry, card_w, card_h)

                    bg = QLinearGradient(rx, ry, rx, ry + card_h)
                    bg.setColorAt(0.0, QColor(24, 32, 56, 210))
                    bg.setColorAt(1.0, QColor(15, 21, 38, 210))
                    p.setPen(QPen(QColor(99, 102, 241, 90), 1.0, Qt.PenStyle.DashLine))
                    p.setBrush(QBrush(bg))
                    p.drawRoundedRect(rect, 12.0, 12.0)

                    p.setPen(QColor("#22D3EE"))
                    f_icon = QFont("Segoe UI Emoji", 18)
                    p.setFont(f_icon)
                    p.drawText(QRectF(rx, ry + 14, card_w, 32), Qt.AlignmentFlag.AlignCenter, "📝")

                    p.setPen(QColor("#F8FAFC"))
                    f_title = QFont("Segoe UI Variable Text", 10)
                    f_title.setWeight(QFont.Weight.Bold)
                    p.setFont(f_title)
                    p.drawText(QRectF(rx + 12, ry + 50, card_w - 24, 22), Qt.AlignmentFlag.AlignCenter, "Chưa có kịch bản phụ đề")

                    p.setPen(QColor("#94A3B8"))
                    f_sub = QFont("Segoe UI Variable Text", 8)
                    p.setFont(f_sub)
                    p.drawText(
                        QRectF(rx + 14, ry + 74, card_w - 28, 48),
                        Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap,
                        "Chọn video nguồn và nhấn '1. Bóc Băng' hoặc 'Bắt đầu xử lý' để AI tạo kịch bản."
                    )
                p.end()
        except Exception:
            pass
    _base_mod.SrtListWidget.paintEvent = _patched_srt_list_paint
except Exception as e:
    print(f"Lỗi patch SrtItemWidget: {e}")

# 1c. Patch _setButtonsEnabled & _onTranscribeError for Live Status Badge & Non-Blocking Navigation
try:
    _orig_set_buttons_enabled = HomeInterface._setButtonsEnabled
    def _patched_set_buttons_enabled(self, enabled: bool = True, *args, **kwargs):
        _orig_set_buttons_enabled(self, enabled, *args, **kwargs)
        # Keep sidebar navigation and non-conflicting UI controls ALWAYS clickable during background processing
        try:
            main_win = self.window()
            if main_win and hasattr(main_win, 'navigationInterface') and main_win.navigationInterface:
                main_win.navigationInterface.setEnabled(True)
            for always_on_attr in (
                'btn_style', 'btn_add_mask', 'btn_add_bg_frame', 'btn_add_logo',
                'btn_remove_item', 'btn_save_srt', 'btn_select_output', 'btn_apply_all',
                'btn_paste_transcript', 'btn_upload_transcript',
            ):
                w_btn = getattr(self, always_on_attr, None)
                if w_btn is not None:
                    w_btn.setEnabled(True)
        except Exception:
            pass
        try:
            from PyQt6.QtCore import QTimer
            if not hasattr(self, '_shimmer_timer'):
                self._shimmer_timer = QTimer(self)
                self._shimmer_timer.setInterval(50)
                self._shimmer_timer.timeout.connect(lambda: self.progress_bar.update() if hasattr(self, 'progress_bar') else None)

            state = "ready" if enabled else "processing"
            txt_local = "Sẵn sàng xử lý" if enabled else "Đang xử lý tác vụ AI..."
            txt_header = "AI Engine Sẵn sàng" if enabled else "Đang xử lý AI..."

            if not enabled:
                self._shimmer_timer.start()
            else:
                self._shimmer_timer.stop()
                if hasattr(self, 'progress_bar') and self.progress_bar.value() >= 100:
                    state = "success"
                    txt_local = "Hoàn tất xử lý ✓"
                    txt_header = "Hoàn tất tác vụ ✓"

            if hasattr(self, '_log_status_badge'):
                self._log_status_badge.set_state(state, txt_local)
            main_win = self.window()
            if hasattr(main_win, 'modernHeader') and hasattr(main_win.modernHeader, 'status_badge'):
                main_win.modernHeader.status_badge.set_state(state, txt_header)
        except Exception:
            pass
    HomeInterface._setButtonsEnabled = _patched_set_buttons_enabled

    _orig_on_transcribe_error = HomeInterface._onTranscribeError
    def _patched_on_transcribe_error(self, err_msg="", *args, **kwargs):
        _orig_on_transcribe_error(self, err_msg, *args, **kwargs)
        try:
            if hasattr(self, '_log_status_badge'):
                self._log_status_badge.set_state("error", "Cảnh báo / Lỗi xử lý")
            main_win = self.window()
            if hasattr(main_win, 'modernHeader') and hasattr(main_win.modernHeader, 'status_badge'):
                main_win.modernHeader.status_badge.set_state("error", "Cần kiểm tra tác vụ")
        except Exception:
            pass
    HomeInterface._onTranscribeError = _patched_on_transcribe_error
except Exception as e:
    print(f"Lỗi patch status feedback: {e}")

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
def _onTranslateClicked_patched(self, *args, **kwargs):
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

# ─────────────────────────────────────────────────────────────────────────────
# Canvas Controls Integration (Aspect Ratio + Video Zoom + Video Transform)
# ─────────────────────────────────────────────────────────────────────────────
_orig_init_canvas = HomeInterface.__init__

def _init_canvas_controls(self, parent=None):
    """
    Runs after _init_patched. Inserts CanvasControlsWidget above the video
    preview area in col2 and wires all signals and real-time canvas rendering.
    """
    _orig_init_canvas(self, parent)
    try:
        from PyQt6.QtWidgets import QVBoxLayout, QWidget
        from app.views.canvas_controls_widget import CanvasControlsWidget
        from app.core.canvas_transform import CanvasTransform

        # Build the controls bar
        self._canvas_controls = CanvasControlsWidget()
        self._canvas_controls.setObjectName("hikariCanvasControls")

        # Locate video_frame in col2 layout and insert controls above it
        inserted = False
        for i in range(self.col2_layout.count()):
            item = self.col2_layout.itemAt(i)
            if item and item.widget() and item.widget() is getattr(self, 'video_frame', None):
                self.col2_layout.insertWidget(i, self._canvas_controls)
                inserted = True
                break

        if not inserted:
            self.col2_layout.insertWidget(1, self._canvas_controls)

        # ── Wire signals ──────────────────────────────────────────────────────
        self._canvas_controls.transform_changed.connect(self._on_canvas_transform_changed)
        self._canvas_controls.fill_requested.connect(self._on_fill_requested)

        # ── Setup real-time Video Canvas rendering and interaction ────────────
        self._setup_video_canvas_transform()

        # Always reset Video Zoom to 100% (X=0, Y=0, Rot=0) on startup and when adding/selecting videos
        self._canvas_controls._reset_all()

        # Kick off initial transform sync
        t = self._canvas_controls.get_transform()
        self._on_canvas_transform_changed(t)

    except Exception as e:
        print(f"[HikariDub] Canvas controls init error: {e}")
        import traceback; traceback.print_exc()

HomeInterface.__init__ = _init_canvas_controls


def _setup_video_canvas_transform(self):
    """
    Patches self.video_canvas to physically resize to the chosen Aspect Ratio,
    center inside video_frame workspace, and render video clipped to Canvas.
    """
    vc = getattr(self, 'video_canvas', None)
    vf = getattr(self, 'video_frame', None)
    if not vc or not vf:
        return

    from PyQt6.QtGui import QPainter, QColor, QPen, QFont
    from PyQt6.QtCore import QRectF, Qt, QPointF
    from app.core.canvas_transform import CanvasTransform

    vc._canvas_transform = self._canvas_controls.get_transform()

    # Workspace setup - completely transparent container so ONLY the Canvas itself is the black box
    vf.setStyleSheet("""
        background: transparent;
        border: none;
    """)
    if vf.layout():
        vf.layout().setAlignment(Qt.AlignmentFlag.AlignCenter)

    vc.setStyleSheet("""
        background-color: #000000;
        border: 1px solid #293244;
        border-radius: 8px;
    """)

    def recalc_and_apply_canvas_size():
        t = getattr(vc, '_canvas_transform', None) or CanvasTransform()
        pad = 4
        avail_w = max(120, vf.width() - pad * 2)
        avail_h = max(120, vf.height() - pad * 2)

        cw_nom = float(t.canvas_w) if t.canvas_w > 0 else 1920.0
        ch_nom = float(t.canvas_h) if t.canvas_h > 0 else 1080.0
        ar = cw_nom / ch_nom

        if (avail_w / float(avail_h)) > ar:
            ch_disp = avail_h
            cw_disp = ch_disp * ar
        else:
            cw_disp = avail_w
            ch_disp = cw_disp / ar

        w_int = max(50, int(round(cw_disp)))
        h_int = max(50, int(round(ch_disp)))
        vc.setFixedSize(w_int, h_int)
        vc.update()
        if hasattr(_self, '_popout_dialog') and _self._popout_dialog and _self._popout_dialog.isVisible():
            _self._popout_dialog.canvas_view.update()

    self.recalc_and_apply_canvas_size = recalc_and_apply_canvas_size

    # Hook vf.resizeEvent so canvas size adjusts on window resize
    orig_vf_resize = vf.resizeEvent
    def patched_vf_resize(event):
        orig_vf_resize(event)
        recalc_and_apply_canvas_size()
    vf.resizeEvent = patched_vf_resize

    def get_video_rect():
        t = getattr(vc, '_canvas_transform', None) or CanvasTransform()
        W = float(vc.width())
        H = float(vc.height())

        nvw = float(getattr(vc, 'native_vw', 0)) or 1920.0
        nvh = float(getattr(vc, 'native_vh', 0)) or 1080.0

        fit_ratio = min(W / nvw, H / nvh)
        scale = max(0.05, float(getattr(t, 'video_scale', 1.0)))
        vw = nvw * fit_ratio * scale
        vh = nvh * fit_ratio * scale

        cw_nominal = float(t.canvas_w) if t.canvas_w > 0 else 1920.0
        screen_scale = W / cw_nominal
        off_x = float(getattr(t, 'pos_x', 0.0)) * screen_scale
        off_y = float(getattr(t, 'pos_y', 0.0)) * screen_scale

        vx = (W - vw) / 2.0 + off_x
        vy = (H - vh) / 2.0 + off_y
        return (vx, vy, vw, vh)

    vc.get_video_rect = get_video_rect
    vc._getVideoRect = get_video_rect

    # ── Wrap paintEvent ───────────────────────────────────────────────────────
    orig_paintEvent = vc.paintEvent

    def patched_paintEvent(event):
        W = float(vc.width())
        H = float(vc.height())
        vx, vy, vw, vh = get_video_rect()

        p = QPainter(vc)
        try:
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

            # 1. Fill Canvas area with deep true black
            p.fillRect(0, 0, int(W), int(H), QColor("#000000"))

            # 2. Draw video strictly clipped to Canvas (overflow hidden)
            t = getattr(vc, '_canvas_transform', None)
            if vc.current_image and not vc.current_image.isNull():
                p.save()
                p.setClipRect(0, 0, int(W), int(H))
                if t and abs(getattr(t, 'rotation', 0.0)) > 0.01:
                    p.translate(vx + vw / 2.0, vy + vh / 2.0)
                    p.rotate(t.rotation)
                    p.drawImage(QRectF(-vw / 2.0, -vh / 2.0, vw, vh), vc.current_image)
                else:
                    p.drawImage(QRectF(vx, vy, vw, vh), vc.current_image)

                # 2a. Real-time Mask / Blur Rendering for Vùng Che (masks_rel)
                masks_rel = getattr(vc, 'masks_rel', None) or []
                if masks_rel and vw > 4 and vh > 4:
                    img_w = vc.current_image.width()
                    img_h = vc.current_image.height()
                    mask_mode = str(getattr(vc, 'config', {}).get('mask_mode', 'Làm mờ tự nhiên (Khuyên dùng)')).lower()
                    v_bounds = QRectF(vx, vy, vw, vh).intersected(QRectF(0, 0, W, H))

                    for m_idx, m in enumerate(masks_rel):
                        try:
                            try:
                                mrect = vc._getMaskRect(m)
                            except TypeError:
                                rx, ry, rw, rh = float(m[0]), float(m[1]), float(m[2]), float(m[3])
                                mrect = QRectF(vx + rx * vw, vy + ry * vh, rw * vw, rh * vh)

                            draw_rect = mrect.intersected(v_bounds)
                            if draw_rect.width() <= 2 or draw_rect.height() <= 2:
                                continue

                            sx = int(max(0, min(img_w - 1, (draw_rect.x() - vx) / vw * img_w)))
                            sy = int(max(0, min(img_h - 1, (draw_rect.y() - vy) / vh * img_h)))
                            sw = int(max(1, min(img_w - sx, draw_rect.width() / vw * img_w)))
                            sh = int(max(1, min(img_h - sy, draw_rect.height() / vh * img_h)))

                            sub_img = vc.current_image.copy(sx, sy, sw, sh)
                            dw_i = max(2, int(round(draw_rect.width())))
                            dh_i = max(2, int(round(draw_rect.height())))

                            if 'ô vuông' in mask_mode or 'pixelate' in mask_mode:
                                px_w = max(4, int(dw_i / 14))
                                px_h = max(2, int(dh_i / 14))
                                small = sub_img.scaled(px_w, px_h, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.FastTransformation)
                                pix_img = small.scaled(dw_i, dh_i, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.FastTransformation)
                                p.drawImage(draw_rect, pix_img)
                            else:
                                # Multi-pass Gaussian-like smooth downscale/upscale + edge background inpainting
                                # so high-contrast hardcoded subtitles are 100% covered and unreadable
                                s1_w = max(3, int(dw_i / 16))
                                s1_h = max(2, int(dh_i / 14))
                                s2_w = max(2, int(dw_i / 32))
                                s2_h = max(1, int(dh_i / 24))
                                pass1 = sub_img.scaled(s1_w, s1_h, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
                                pass2 = pass1.scaled(s2_w, s2_h, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
                                blurred_img = pass2.scaled(dw_i, dh_i, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
                                p.drawImage(draw_rect, blurred_img)

                                # Sample top & bottom border strips (background outside text glyphs) for natural cover
                                strip_h = max(1, min(5, int(sh * 0.14)))
                                top_strip = sub_img.copy(0, 0, sw, strip_h).scaled(
                                    max(3, int(dw_i / 12)), 2, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation
                                ).scaled(
                                    dw_i, max(1, int(round(dh_i / 2.0))), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation
                                )
                                bot_strip = sub_img.copy(0, max(0, sh - strip_h), sw, strip_h).scaled(
                                    max(3, int(dw_i / 12)), 2, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation
                                ).scaled(
                                    dw_i, max(1, int(round(dh_i / 2.0))), Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation
                                )
                                p.save()
                                p.setOpacity(0.82)
                                half_h = draw_rect.height() / 2.0
                                p.drawImage(QRectF(draw_rect.x(), draw_rect.y(), draw_rect.width(), half_h), top_strip)
                                p.drawImage(QRectF(draw_rect.x(), draw_rect.y() + half_h, draw_rect.width(), half_h), bot_strip)
                                p.restore()
                        except Exception:
                            pass
                p.restore()

            # 2b. Empty state guide when no video frame is loaded
            if not vc.current_image or vc.current_image.isNull():
                # Still show frosted fill for any active masks on empty canvas
                for m in (getattr(vc, 'masks_rel', None) or []):
                    try:
                        mrect = vc._getMaskRect(m)
                        p.fillRect(mrect, QColor(30, 41, 59, 190))
                    except Exception:
                        pass
                p.setPen(QColor("#64748B"))
                font_empty = QFont("Segoe UI Variable Text", 10)
                font_empty.setWeight(QFont.Weight.DemiBold)
                p.setFont(font_empty)
                p.drawText(
                    QRectF(0, 0, W, H),
                    Qt.AlignmentFlag.AlignCenter,
                    "🎬 Chưa chọn Video nguồn\nNhấn 'Chọn Video Nguồn...' ở cột trái để bắt đầu"
                )

            # 2c. Draw interactive overlay frames & resize handles (Masks, Logo, Watermark)
            for m in (getattr(vc, 'masks_rel', None) or []):
                try:
                    mr = vc._getMaskRect(m)
                    p.setPen(QPen(QColor("#F43F5E"), 1.5, Qt.PenStyle.DashLine))
                    p.setBrush(Qt.BrushStyle.NoBrush)
                    p.drawRect(mr)
                    p.fillRect(QRectF(mr.right() - 8, mr.bottom() - 8, 8, 8), QColor("#F43F5E"))
                except Exception:
                    pass

            if getattr(vc, 'logo_image', None) is not None and getattr(vc, 'logo_rel', None):
                try:
                    lr = vc._getMaskRect(vc.logo_rel)
                    p.drawImage(lr, vc.logo_image)
                    p.setPen(QPen(QColor("#38BDF8"), 1.2, Qt.PenStyle.DashLine))
                    p.setBrush(Qt.BrushStyle.NoBrush)
                    p.drawRect(lr)
                    p.fillRect(QRectF(lr.right() - 8, lr.bottom() - 8, 8, 8), QColor("#38BDF8"))
                except Exception:
                    pass

            if getattr(vc, 'watermark_text', '') and getattr(vc, 'wm_rel', None):
                try:
                    wr = vc._getMaskRect(vc.wm_rel)
                    p.fillRect(wr, QColor(0, 0, 0, 115))
                    p.setPen(QColor("#FFFFFF"))
                    f_wm = QFont("Segoe UI", max(9, int(wr.height() * 0.45)), QFont.Weight.Bold)
                    p.setFont(f_wm)
                    p.drawText(wr, Qt.AlignmentFlag.AlignCenter, vc.watermark_text)
                    p.setPen(QPen(QColor("#A78BFA"), 1.2, Qt.PenStyle.DashLine))
                    p.setBrush(Qt.BrushStyle.NoBrush)
                    p.drawRect(wr)
                    p.fillRect(QRectF(wr.right() - 8, wr.bottom() - 8, 8, 8), QColor("#A78BFA"))
                except Exception:
                    pass

            # 3. Canvas Outer Border (Subtle Modern SaaS Gradient Border)
            from PyQt6.QtGui import QLinearGradient, QBrush
            b_grad = QLinearGradient(0, 0, W, H)
            b_grad.setColorAt(0.0, QColor(99, 102, 241, 150))    # Electric Blue #6366F1
            b_grad.setColorAt(0.5, QColor(139, 92, 246, 130))    # Violet #8B5CF6
            b_grad.setColorAt(1.0, QColor(6, 182, 212, 150))     # Cyan #06B6D4
            pen_border = QPen(QBrush(b_grad), 1.2, Qt.PenStyle.SolidLine)
            p.setPen(pen_border)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRect(QRectF(0.6, 0.6, W - 1.2, H - 1.2))

        finally:
            p.end()

        # 7. Draw overlay elements (subtitles, watermark, masks, logo) on the Canvas
        saved_img = vc.current_image
        vc.current_image = None
        try:
            orig_paintEvent(event)
        finally:
            vc.current_image = saved_img

    vc.paintEvent = patched_paintEvent

    # ── Mouse Interaction (Drag Video & Wheel Zoom) ───────────────────────────
    orig_mousePress = vc.mousePressEvent
    orig_mouseMove = vc.mouseMoveEvent
    orig_mouseRelease = vc.mouseReleaseEvent

    _drag_state = {'active': False, 'pos': None}
    _self = self

    def patched_mousePress(event):
        orig_mousePress(event)
        # If user did not click on an overlay item (selected_item is None), they're dragging the video
        if getattr(vc, 'selected_item', None) is None and event.button() == Qt.MouseButton.LeftButton:
            _drag_state['active'] = True
            _drag_state['pos'] = event.position()
            vc.setCursor(Qt.CursorShape.ClosedHandCursor)
        else:
            _drag_state['active'] = False

    def patched_mouseMove(event):
        if _drag_state['active'] and _drag_state['pos'] is not None:
            cur_pos = event.position()
            dx = cur_pos.x() - _drag_state['pos'].x()
            dy = cur_pos.y() - _drag_state['pos'].y()
            _drag_state['pos'] = cur_pos

            W = float(vc.width())
            t = getattr(vc, '_canvas_transform', None)
            if t and W > 0:
                scale_to_screen = W / float(t.canvas_w)
                dx_canvas = dx / scale_to_screen
                dy_canvas = dy / scale_to_screen
                if hasattr(_self, '_canvas_controls'):
                    _self._canvas_controls.update_pos_from_drag(dx_canvas, dy_canvas)
        else:
            orig_mouseMove(event)

    def patched_mouseRelease(event):
        if _drag_state['active']:
            _drag_state['active'] = False
            _drag_state['pos'] = None
            vc.setCursor(Qt.CursorShape.ArrowCursor)
        orig_mouseRelease(event)
        try:
            vc.saveConfig()
            _self._sync_current_overlay_and_transform()
        except Exception:
            pass
        vc.update()

    def patched_wheel(event):
        delta = event.angleDelta().y()
        if hasattr(_self, '_canvas_controls'):
            _self._canvas_controls.update_zoom_from_scroll(delta)
        event.accept()

    def patched_mouseDoubleClick(event):
        _self._toggle_theater_mode()
        event.accept()

    vc.mousePressEvent = patched_mousePress
    vc.mouseMoveEvent = patched_mouseMove
    vc.mouseReleaseEvent = patched_mouseRelease
    vc.mouseDoubleClickEvent = patched_mouseDoubleClick
    vc.wheelEvent = patched_wheel
    vc.setToolTip("Bấm đúp để Bật/Tắt chế độ xem rộng (Theater Mode) | Kéo để di chuyển | Lăn chuột để Zoom")

    # Connect Theater & Popout signals from controls
    if hasattr(_self, '_canvas_controls'):
        try:
            _self._canvas_controls.theater_toggled.connect(_self._toggle_theater_mode)
            _self._canvas_controls.popout_requested.connect(_self._open_popout_preview)
        except Exception:
            pass

    # Initial sizing
    recalc_and_apply_canvas_size()

HomeInterface._setup_video_canvas_transform = _setup_video_canvas_transform


def _toggle_theater_mode(self):
    """Expands center video canvas to full window width and height by collapsing side panels."""
    theater = not getattr(self, '_theater_active', False)
    self._theater_active = theater

    if hasattr(self, 'col1_container'):
        self.col1_container.setVisible(not theater)
    if hasattr(self, 'col3_widget'):
        self.col3_widget.setVisible(not theater)
    if hasattr(self, 'row2_widget'):
        self.row2_widget.setVisible(not theater)

    if hasattr(self, '_canvas_controls'):
        self._canvas_controls.set_theater_active(theater)

    from PyQt6.QtCore import QTimer
    QTimer.singleShot(30, self.recalc_and_apply_canvas_size)

    if theater:
        InfoBar.info(
            title="Chế Độ Xem Rộng (Theater Mode)",
            content="Đã phóng to tối đa khung xem trước! Bấm đúp vào video hoặc bấm lại nút để quay về giao diện 3 cột.",
            parent=self.window(),
            position=InfoBarPosition.TOP,
            duration=3500
        )


def _open_popout_preview(self):
    """Opens a separate floating HD window for multi-monitor or massive preview."""
    try:
        from app.views.canvas_popout_dialog import CanvasPopoutDialog
        if not hasattr(self, '_popout_dialog') or not self._popout_dialog:
            self._popout_dialog = CanvasPopoutDialog(self)
        self._popout_dialog.show()
        self._popout_dialog.raise_()
        self._popout_dialog.activateWindow()
    except Exception as e:
        print(f"[HikariDub] Popout preview error: {e}")


HomeInterface._toggle_theater_mode = _toggle_theater_mode
HomeInterface._open_popout_preview = _open_popout_preview


# ─── Transform signal handlers ────────────────────────────────────────────────
def _on_canvas_transform_changed(self, transform):
    """
    Called when user changes aspect ratio, scale, position, or rotation.
    Instantly updates the visual canvas in VideoCanvasWidget and syncs state.
    """
    try:
        self._current_canvas_transform = transform
        if hasattr(self, 'video_canvas') and self.video_canvas:
            self.video_canvas._canvas_transform = transform
            if hasattr(self, 'recalc_and_apply_canvas_size'):
                self.recalc_and_apply_canvas_size()
            else:
                self.video_canvas.update()

        # Log major ratio changes
        ratio_lbl = transform.aspect_ratio.upper()
        canvas_sz = f"{transform.canvas_w}×{transform.canvas_h}"
        scale_pct = int(round(transform.video_scale * 100))
        log_key = f"{ratio_lbl}|{canvas_sz}"
        if getattr(self, '_last_canvas_log_key', None) != log_key:
            self._last_canvas_log_key = log_key
            self._appendLog(
                f"🎨 Canvas: {ratio_lbl} ({canvas_sz}) · Zoom {scale_pct}% "
                f"· X={int(transform.pos_x)}px Y={int(transform.pos_y)}px "
                f"· Rot={transform.rotation:.1f}°"
            )
    except Exception as e:
        print(f"[HikariDub] transform_changed handler error: {e}")

HomeInterface._on_canvas_transform_changed = _on_canvas_transform_changed


def _on_fill_requested(self):
    """Calculate zoom scale to fill Canvas completely with zero black bars."""
    try:
        vc = getattr(self, 'video_canvas', None)
        if not vc:
            return
        nvw = float(getattr(vc, 'native_vw', 0)) or 1920.0
        nvh = float(getattr(vc, 'native_vh', 0)) or 1080.0
        t = getattr(self, '_current_canvas_transform', None)
        if not t:
            return
        cw = float(t.canvas_w) or 1920.0
        ch = float(t.canvas_h) or 1080.0

        fit_ratio = min(cw / nvw, ch / nvh)
        fill_ratio = max(cw / nvw, ch / nvh)
        scale = fill_ratio / fit_ratio if fit_ratio > 0 else 1.0

        if hasattr(self, '_canvas_controls'):
            self._canvas_controls.set_zoom_scale(scale)
        self._appendLog(f"⊞ Lấp đầy (Fill / Crop): Zoom tự động đặt thành {int(round(scale * 100))}%")
    except Exception as e:
        print(f"[HikariDub] fill_requested error: {e}")

HomeInterface._on_fill_requested = _on_fill_requested


# ─── Expose transform & masks_rel to video_renderer (video_config injection) ───
def _sync_current_overlay_and_transform(self):
    """Ensures video_canvas.saveConfig(), config.json, and per_video_configs[video_path] have latest masks & transform."""
    try:
        from app.common.config_manager import set_config
        vc = getattr(self, 'video_canvas', None)
        if vc is not None:
            try:
                vc.saveConfig()
            except Exception:
                pass
            cfg = dict(getattr(vc, 'config', {}) or {})
            cfg['mask_logos'] = [list(m) for m in (getattr(vc, 'masks_rel', None) or [])]
            if hasattr(self, '_current_canvas_transform') and self._current_canvas_transform:
                t = self._current_canvas_transform
                cfg['canvas_w']     = t.canvas_w
                cfg['canvas_h']     = t.canvas_h
                cfg['video_scale']  = t.video_scale
                cfg['pos_x']        = t.pos_x
                cfg['pos_y']        = t.pos_y
                cfg['rotation']     = t.rotation
                cfg['aspect_ratio'] = t.aspect_ratio
            try:
                set_config('video_overlay', cfg)
            except Exception:
                pass
            if not hasattr(self, 'per_video_configs') or self.per_video_configs is None:
                self.per_video_configs = {}
            idx = self.video_combo.currentIndex() if hasattr(self, 'video_combo') else -1
            if 0 <= idx < len(getattr(self, 'selected_videos', [])):
                v_path = self.selected_videos[idx]
                merged = dict(self.per_video_configs.get(v_path) or {})
                merged.update(cfg)
                self.per_video_configs[v_path] = merged
    except Exception as e:
        print(f"[HikariDub] sync overlay error: {e}")

HomeInterface._sync_current_overlay_and_transform = _sync_current_overlay_and_transform

def _call_orig_slot(fn, self, *args, **kwargs):
    """Safely invokes an original slot, stripping excess Qt signal args (such as clicked(bool))."""
    try:
        code = getattr(fn, '__code__', None)
        if code is not None and not (code.co_flags & 4):
            max_pos = max(0, code.co_argcount - 1)
            args = args[:max_pos]
    except Exception:
        pass
    return fn(self, *args, **kwargs)

_orig_on_render_clicked = getattr(HomeInterface, '_onRenderClicked', None)
if callable(_orig_on_render_clicked):
    def _patched_on_render_clicked(self, *args, **kwargs):
        self._sync_current_overlay_and_transform()
        if hasattr(self, '_sync_srt_lists_to_disk'):
            self._sync_srt_lists_to_disk()
        return _call_orig_slot(_orig_on_render_clicked, self, *args, **kwargs)
    HomeInterface._onRenderClicked = _patched_on_render_clicked

_orig_on_start_full_clicked = getattr(HomeInterface, '_onStartFullClicked', None)
if callable(_orig_on_start_full_clicked):
    def _patched_on_start_full_clicked(self, *args, **kwargs):
        self._sync_current_overlay_and_transform()
        if hasattr(self, '_sync_srt_lists_to_disk'):
            self._sync_srt_lists_to_disk()
        return _call_orig_slot(_orig_on_start_full_clicked, self, *args, **kwargs)
    HomeInterface._onStartFullClicked = _patched_on_start_full_clicked

def _build_video_config_with_transform(self):
    """Returns a video_config dict enriched with canvas transform data."""
    base_cfg = {}
    try:
        base_build = getattr(super(HomeInterface, self), '_build_video_config', None)
        if callable(base_build):
            base_cfg = base_build() or {}
    except Exception:
        pass

    if hasattr(self, '_current_canvas_transform'):
        t = self._current_canvas_transform
        base_cfg['canvas_w']     = t.canvas_w
        base_cfg['canvas_h']     = t.canvas_h
        base_cfg['video_scale']  = t.video_scale
        base_cfg['pos_x']        = t.pos_x
        base_cfg['pos_y']        = t.pos_y
        base_cfg['rotation']     = t.rotation
        base_cfg['aspect_ratio'] = t.aspect_ratio
    return base_cfg

HomeInterface._build_video_config_with_transform = _build_video_config_with_transform


# ─── Always reset Video Zoom to 100% when adding or switching videos ──────────
_orig_on_select_video = getattr(HomeInterface, '_onSelectVideo', None)
if callable(_orig_on_select_video):
    def _patched_on_select_video(self, *args, **kwargs):
        if hasattr(self, '_canvas_controls') and self._canvas_controls:
            self._canvas_controls._reset_all()
        res = _call_orig_slot(_orig_on_select_video, self, *args, **kwargs)
        if hasattr(self, '_canvas_controls') and self._canvas_controls:
            self._canvas_controls._reset_all()
        try:
            self._restore_cached_transcript_if_needed()
        except Exception:
            pass
        return res
    HomeInterface._onSelectVideo = _patched_on_select_video

_orig_on_video_combo_changed = getattr(HomeInterface, '_onVideoComboChanged', None)
if callable(_orig_on_video_combo_changed):
    def _patched_on_video_combo_changed(self, *args, **kwargs):
        if hasattr(self, '_canvas_controls') and self._canvas_controls:
            self._canvas_controls._reset_all()
        res = _call_orig_slot(_orig_on_video_combo_changed, self, *args, **kwargs)
        if hasattr(self, '_canvas_controls') and self._canvas_controls:
            self._canvas_controls._reset_all()
        # If user pasted/uploaded a transcript before choosing a video, restore it for the new video if no SRT exists yet
        try:
            self._restore_cached_transcript_if_needed()
        except Exception:
            pass
        return res
    HomeInterface._onVideoComboChanged = _patched_on_video_combo_changed


# ─────────────────────────────────────────────────────────────────────────────
# Transcript Paste & File Upload Integration (SRT / TXT -> Direct Voice AI)
# ─────────────────────────────────────────────────────────────────────────────
import re
import tempfile

_SRT_TIME_RE = re.compile(
    r'(\d{1,2}:\d{2}:\d{2}[,\.]\d{1,3}|\d{1,2}:\d{2}[,\.]\d{1,3})\s*-->\s*(\d{1,2}:\d{2}:\d{2}[,\.]\d{1,3}|\d{1,2}:\d{2}[,\.]\d{1,3})'
)

def _format_srt_timestamp(ts_raw: str) -> str:
    """Normalizes timestamp like '00:12.800' or '0:00:12,80' to standard '00:00:12,800'."""
    s = ts_raw.strip().replace('.', ',')
    if ',' in s:
        main_part, ms_part = s.split(',', 1)
    else:
        main_part, ms_part = s, '000'
    ms_part = (ms_part + '000')[:3]
    parts = [p.strip() for p in main_part.split(':')]
    if len(parts) == 2:
        hh, mm, ss = 0, int(parts[0]), int(parts[1])
    elif len(parts) >= 3:
        hh, mm, ss = int(parts[0]), int(parts[1]), int(parts[2])
    else:
        hh, mm, ss = 0, 0, int(parts[0] or 0)
    return f"{hh:02d}:{mm:02d}:{ss:02d},{ms_part}"


def _seconds_to_srt_ts(sec: float) -> str:
    total_ms = max(0, int(round(sec * 1000)))
    hh = total_ms // 3600000
    rem = total_ms % 3600000
    mm = rem // 60000
    rem %= 60000
    ss = rem // 1000
    ms = rem % 1000
    return f"{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}"


def _normalize_srt_content(raw_text: str, ref_blocks: list = None):
    """
    Parses and normalizes pasted or uploaded transcript text into canonical SRT format.
    Supports:
    - Standard SRT with/without blank lines and with leading spaces (e.g. '   1\\n00:00:12,800 --> ...')
    - VTT timestamps (dots instead of commas)
    - Plain text lines (mapped to ref_blocks timestamps if available, or auto-timed 2.5s per line)
    Returns (canonical_srt_string, block_count).
    """
    if not raw_text or not raw_text.strip():
        return "", 0

    cleaned = raw_text.lstrip('\ufeff').replace('\r\n', '\n').replace('\r', '\n')
    lines = [ln.strip() for ln in cleaned.split('\n')]

    # Find all lines containing '-->' timestamps
    ts_line_indices = []
    for i, ln in enumerate(lines):
        m = _SRT_TIME_RE.search(ln)
        if m:
            ts_line_indices.append((i, m.group(1), m.group(2)))

    blocks_out = []

    if ts_line_indices:
        for k, (line_idx, start_raw, end_raw) in enumerate(ts_line_indices):
            ts_norm = f"{_format_srt_timestamp(start_raw)} --> {_format_srt_timestamp(end_raw)}"
            next_ts_line = ts_line_indices[k + 1][0] if (k + 1) < len(ts_line_indices) else len(lines)

            # Collect candidate text lines between this timestamp and the next timestamp
            cand_lines = [ln for ln in lines[line_idx + 1:next_ts_line] if ln]
            # If the last non-empty line before the next timestamp is a pure block number (e.g. '2', '3'), drop it
            if (k + 1) < len(ts_line_indices) and len(cand_lines) >= 2 and cand_lines[-1].isdigit():
                cand_lines.pop()
            elif (k + 1) < len(ts_line_indices) and len(cand_lines) == 1 and cand_lines[0].isdigit():
                cand_lines = []

            content_text = "\n".join(cand_lines).strip()
            if content_text:
                idx_num = len(blocks_out) + 1
                blocks_out.append(f"{idx_num}\n{ts_norm}\n{content_text}")
    else:
        # Plain text mode: pair with ref_blocks timestamps if available, else auto-generate timestamps
        non_empty = [ln for ln in lines if ln and not ln.isdigit() and ln.upper() != 'WEBVTT']
        ref_ts_list = []
        if ref_blocks:
            for b in ref_blocks:
                b_lines = [x.strip() for x in str(b).split('\n') if x.strip()]
                if len(b_lines) >= 2 and '-->' in b_lines[1]:
                    ref_ts_list.append(b_lines[1])

        cur_t = 0.0
        for idx_zero, ln in enumerate(non_empty):
            clean_ln = re.sub(r'^\d+[\.\)\:\-]\s*', '', ln).strip() or ln
            if idx_zero < len(ref_ts_list):
                ts_norm = ref_ts_list[idx_zero]
            else:
                dur = max(1.8, min(5.0, len(clean_ln.split()) * 0.38))
                ts_norm = f"{_seconds_to_srt_ts(cur_t)} --> {_seconds_to_srt_ts(cur_t + dur)}"
                cur_t += dur + 0.15
            blocks_out.append(f"{idx_zero + 1}\n{ts_norm}\n{clean_ln}")

    return "\n\n".join(blocks_out), len(blocks_out)


def _get_current_video_data_dir(self):
    """Returns (workspace_dir, data_dir) for the currently selected video, or (None, None)."""
    try:
        output_dir = self.line_output_path.text().strip() if hasattr(self, 'line_output_path') else ""
        idx = self.video_combo.currentIndex() if hasattr(self, 'video_combo') else -1
        if not output_dir or idx < 0 or idx >= len(getattr(self, 'selected_videos', [])):
            return None, None
        video_path = self.selected_videos[idx]
        try:
            from app.core.video_utils import get_safe_basename
            base_name = get_safe_basename(video_path)
        except Exception:
            if hasattr(_base_mod, 'get_safe_basename'):
                base_name = _base_mod.get_safe_basename(video_path)
            else:
                base_name = os.path.splitext(os.path.basename(video_path))[0][:50].strip()
        workspace_dir = os.path.join(output_dir, base_name)
        data_dir = os.path.join(workspace_dir, "Data")
        os.makedirs(data_dir, exist_ok=True)
        return workspace_dir, data_dir
    except Exception:
        return None, None

HomeInterface._get_current_video_data_dir = _get_current_video_data_dir


def _apply_imported_transcript(self, raw_text: str, target_mode: str = "trans", auto_run_voice: bool = False) -> bool:
    """
    Normalizes raw_text into SRT, loads it into SrtListWidget ('trans' or 'orig'),
    writes it to the active video's Data folder (or caches it until a video is chosen),
    and optionally triggers Step 3 (Tạo Giọng AI) immediately.
    """
    ref_blocks = getattr(getattr(self, 'srt_orig_list', None), 'all_blocks', None) or \
                 getattr(getattr(self, 'srt_trans_list', None), 'all_blocks', None)
    norm_srt, count = _normalize_srt_content(raw_text, ref_blocks=ref_blocks)
    if count == 0 or not norm_srt.strip():
        InfoBar.warning(
            title="Nội dung trống hoặc không hợp lệ",
            content="Vui lòng dán hoặc chọn file chứa kịch bản phụ đề (SRT hoặc văn bản).",
            parent=self.window(),
            position=InfoBarPosition.TOP,
            duration=5000
        )
        return False

    # Always write a staging file so SrtListWidget.load_srt(path) works even before selecting a video
    staging_path = os.path.join(tempfile.gettempdir(), f"hikari_imported_{target_mode}.srt")
    with open(staging_path, "w", encoding="utf-8") as f:
        f.write(norm_srt)

    self._cached_imported_srt = (norm_srt, target_mode)

    # Also write directly to active video's Data directory if a video is selected
    _, data_dir = self._get_current_video_data_dir()
    if data_dir:
        trans_path = os.path.join(data_dir, "temp_translated.srt")
        orig_path = os.path.join(data_dir, "temp_original.srt")
        if target_mode == "trans":
            with open(trans_path, "w", encoding="utf-8") as f:
                f.write(norm_srt)
            # If temp_original.srt doesn't exist yet, also populate it so all steps work seamlessly
            if not os.path.exists(orig_path):
                with open(orig_path, "w", encoding="utf-8") as f:
                    f.write(norm_srt)
                if hasattr(self, 'srt_orig_list'):
                    self.srt_orig_list.load_srt(orig_path)
        else:
            with open(orig_path, "w", encoding="utf-8") as f:
                f.write(norm_srt)

    # Load into SrtListWidget UI and switch tab
    p_keys = list(getattr(getattr(self, 'srt_pivot', None), 'items', {}).keys())
    if target_mode == "trans":
        if hasattr(self, 'srt_trans_list'):
            self.srt_trans_list.load_srt(staging_path)
        if hasattr(self, 'srt_pivot') and len(p_keys) >= 2:
            self.srt_pivot.setCurrentItem(p_keys[1])
        if hasattr(self, 'srt_stacked_widget'):
            self.srt_stacked_widget.setCurrentIndex(1)
        tab_name = "Kịch bản Dịch"
    else:
        if hasattr(self, 'srt_orig_list'):
            self.srt_orig_list.load_srt(staging_path)
        if hasattr(self, 'srt_pivot') and len(p_keys) >= 1:
            self.srt_pivot.setCurrentItem(p_keys[0])
        if hasattr(self, 'srt_stacked_widget'):
            self.srt_stacked_widget.setCurrentIndex(0)
        tab_name = "Kịch bản Gốc"

    self._appendLog(f"📋 Đã nạp thành công {count} câu phụ đề vào [{tab_name}]! Sẵn sàng tạo giọng đọc AI.")
    InfoBar.success(
        title="Đã nạp kịch bản thành công",
        content=f"Đã đưa {count} câu phụ đề vào {tab_name}. Bạn có thể bấm '3. Tạo Giọng AI' ngay!",
        parent=self.window(),
        position=InfoBarPosition.TOP,
        duration=5000
    )

    if auto_run_voice and hasattr(self, '_onVoiceClicked'):
        self._onVoiceClicked()
    return True

HomeInterface._apply_imported_transcript = _apply_imported_transcript


def _restore_cached_transcript_if_needed(self):
    """If the user imported a transcript before selecting a video, copy it into the newly selected video's Data dir."""
    cached = getattr(self, '_cached_imported_srt', None)
    if not cached:
        return
    norm_srt, target_mode = cached
    _, data_dir = self._get_current_video_data_dir()
    if not data_dir:
        return
    trans_path = os.path.join(data_dir, "temp_translated.srt")
    orig_path = os.path.join(data_dir, "temp_original.srt")
    p_keys = list(getattr(getattr(self, 'srt_pivot', None), 'items', {}).keys())
    if target_mode == "trans" and not os.path.exists(trans_path):
        with open(trans_path, "w", encoding="utf-8") as f:
            f.write(norm_srt)
        if not os.path.exists(orig_path):
            with open(orig_path, "w", encoding="utf-8") as f:
                f.write(norm_srt)
        if hasattr(self, 'srt_trans_list'):
            self.srt_trans_list.load_srt(trans_path)
        if hasattr(self, 'srt_pivot') and len(p_keys) >= 2:
            self.srt_pivot.setCurrentItem(p_keys[1])
        if hasattr(self, 'srt_stacked_widget'):
            self.srt_stacked_widget.setCurrentIndex(1)
    elif target_mode == "orig" and not os.path.exists(orig_path):
        with open(orig_path, "w", encoding="utf-8") as f:
            f.write(norm_srt)
        if hasattr(self, 'srt_orig_list'):
            self.srt_orig_list.load_srt(orig_path)

HomeInterface._restore_cached_transcript_if_needed = _restore_cached_transcript_if_needed


def _sync_srt_lists_to_disk(self):
    """Ensures any in-memory blocks in srt_trans_list / srt_orig_list are written to Data/ before Voice or Render."""
    try:
        _, data_dir = self._get_current_video_data_dir()
        if not data_dir:
            return
        if hasattr(self, 'srt_trans_list'):
            trans_str = self.srt_trans_list.to_srt_string().strip()
            if trans_str:
                with open(os.path.join(data_dir, "temp_translated.srt"), "w", encoding="utf-8") as f:
                    f.write(trans_str)
        if hasattr(self, 'srt_orig_list'):
            orig_str = self.srt_orig_list.to_srt_string().strip()
            if orig_str:
                with open(os.path.join(data_dir, "temp_original.srt"), "w", encoding="utf-8") as f:
                    f.write(orig_str)
    except Exception as e:
        print(f"[HikariDub] sync SRT to disk error: {e}")

HomeInterface._sync_srt_lists_to_disk = _sync_srt_lists_to_disk

_orig_on_voice_clicked = getattr(HomeInterface, '_onVoiceClicked', None)
if callable(_orig_on_voice_clicked):
    def _patched_on_voice_clicked(self, *args, **kwargs):
        self._sync_srt_lists_to_disk()
        return _call_orig_slot(_orig_on_voice_clicked, self, *args, **kwargs)
    HomeInterface._onVoiceClicked = _patched_on_voice_clicked


def _open_upload_transcript_dialog(self, *args, **kwargs):
    """Opens file dialog to import an external .srt / .txt / .vtt file into the Subtitle Editor."""
    from PyQt6.QtWidgets import QFileDialog
    file_path, _ = QFileDialog.getOpenFileName(
        self.window(),
        "Chọn File Kịch Bản Phụ Đề (SRT / TXT / VTT)",
        "",
        "Subtitle & Text Files (*.srt *.txt *.vtt);;All Files (*.*)"
    )
    if not file_path or not os.path.exists(file_path):
        return
    try:
        raw_content = None
        for enc in ("utf-8-sig", "utf-8", "utf-16", "cp1258", "latin-1"):
            try:
                with open(file_path, "r", encoding=enc) as f:
                    raw_content = f.read()
                break
            except Exception:
                continue
        if not raw_content:
            return
        # Default to Kịch bản Dịch ('trans') so user can immediately generate AI Voice
        target_mode = "orig" if (hasattr(self, 'srt_stacked_widget') and self.srt_stacked_widget.currentIndex() == 0 and getattr(self.srt_trans_list, 'all_blocks', None)) else "trans"
        self._apply_imported_transcript(raw_content, target_mode=target_mode, auto_run_voice=False)
    except Exception as e:
        InfoBar.error(
            title="Lỗi đọc file kịch bản",
            content=str(e),
            parent=self.window(),
            position=InfoBarPosition.TOP,
            duration=5000
        )

HomeInterface._open_upload_transcript_dialog = _open_upload_transcript_dialog


def _open_paste_transcript_dialog(self, *args, **kwargs):
    """Opens a Modern SaaS Dialog allowing the user to paste an SRT transcript or load a file and create AI Voice."""
    from PyQt6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPlainTextEdit, QApplication, QFileDialog
    )
    from PyQt6.QtCore import Qt
    from qfluentwidgets import PushButton, PrimaryPushButton, ComboBox
    from app.common.design_system import Colors, Gradients

    dlg = QDialog(self.window())
    dlg.setWindowTitle("Dán Kịch Bản Phụ Đề (Transcript / SRT) — Hikari Tsukimi Studio")
    dlg.resize(720, 560)
    dlg.setStyleSheet(f"""
        QDialog {{
            background-color: {Colors.BG_DARK};
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.BORDER};
            border-radius: 12px;
        }}
    """)

    vbox = QVBoxLayout(dlg)
    vbox.setContentsMargins(20, 18, 20, 18)
    vbox.setSpacing(12)

    # Header
    lbl_title = QLabel("📋 DÁN HOẶC TẢI LÊN KỊCH BẢN PHỤ ĐỀ (SRT / TRANSCRIPT)")
    lbl_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 800; font-size: 15px; letter-spacing: 0.4px;")
    vbox.addWidget(lbl_title)

    lbl_desc = QLabel(
        "Dán trực tiếp nội dung SRT có mốc thời gian (ví dụ: 1 → 00:00:12,800 --> 00:00:14,520 → Lời thoại) "
        "hoặc danh sách câu thoại vào ô bên dưới để nạp thẳng vào Kịch bản Dịch và tạo Giọng đọc AI."
    )
    lbl_desc.setWordWrap(True)
    lbl_desc.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
    vbox.addWidget(lbl_desc)

    # Top Action Toolbar (Clipboard Paste, File Browse, Clear, Target Tab Selector)
    tool_row = QHBoxLayout()
    tool_row.setSpacing(8)

    btn_clip = PushButton("📋 Dán từ Clipboard", dlg)
    btn_clip.setCursor(Qt.CursorShape.PointingHandCursor)

    btn_file = PushButton("📂 Chọn File .SRT / .TXT...", dlg)
    btn_file.setCursor(Qt.CursorShape.PointingHandCursor)

    btn_clear = PushButton("🗑 Xóa trắng", dlg)
    btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)

    combo_target = ComboBox(dlg)
    combo_target.addItem("🎯 Nạp vào: Kịch bản Dịch (Để Tạo Giọng AI ngay)", userData="trans")
    combo_target.addItem("📝 Nạp vào: Kịch bản Gốc (Để Dịch AI tiếp)", userData="orig")
    combo_target.setCurrentIndex(0)

    tool_row.addWidget(btn_clip)
    tool_row.addWidget(btn_file)
    tool_row.addWidget(btn_clear)
    tool_row.addStretch(1)
    tool_row.addWidget(combo_target)
    vbox.addLayout(tool_row)

    # Text Editor
    editor = QPlainTextEdit(dlg)
    editor.setPlaceholderText(
        "1\n"
        "00:00:12,800 --> 00:00:14,520\n"
        "Đã bảo mua xe bản tiêu chuẩn thôi mà!\n\n"
        "2\n"
        "00:00:14,520 --> 00:00:15,260\n"
        "Anh cứ nhất quyết không nghe!\n\n"
        "3\n"
        "00:00:15,260 --> 00:00:16,420\n"
        "Giờ thì hay rồi!"
    )
    editor.setStyleSheet(f"""
        QPlainTextEdit {{
            background-color: {Colors.BG_DEEP};
            color: {Colors.TEXT_PRIMARY};
            border: 1px solid {Colors.BORDER};
            border-radius: 10px;
            padding: 12px;
            font-family: 'Consolas', 'Segoe UI', monospace;
            font-size: 13px;
            selection-background-color: {Colors.PRIMARY};
        }}
        QPlainTextEdit:focus {{
            border: 1px solid {Colors.ACCENT};
        }}
    """)

    # Pre-fill with current translated or original SRT if available
    existing_txt = ""
    if hasattr(self, 'srt_trans_list'):
        existing_txt = self.srt_trans_list.to_srt_string().strip()
    if not existing_txt and hasattr(self, 'srt_orig_list'):
        existing_txt = self.srt_orig_list.to_srt_string().strip()
    if existing_txt:
        editor.setPlainText(existing_txt)

    vbox.addWidget(editor, 1)

    # Live Block Counter + Footer Actions
    foot_row = QHBoxLayout()
    foot_row.setSpacing(10)

    lbl_count = QLabel("✨ Phát hiện: 0 câu phụ đề")
    lbl_count.setStyleSheet(f"color: {Colors.ACCENT_BRIGHT}; font-weight: 700; font-size: 12px;")
    foot_row.addWidget(lbl_count)
    foot_row.addStretch(1)

    def _update_count():
        _, c = _normalize_srt_content(editor.toPlainText())
        lbl_count.setText(f"✨ Phát hiện: {c} câu phụ đề hợp lệ")

    editor.textChanged.connect(_update_count)
    _update_count()

    def _on_paste_clip():
        clip_txt = QApplication.clipboard().text()
        if clip_txt:
            editor.setPlainText(clip_txt)

    def _on_pick_file():
        fp, _ = QFileDialog.getOpenFileName(
            dlg,
            "Chọn File Phụ Đề (SRT / TXT / VTT)",
            "",
            "Subtitle & Text Files (*.srt *.txt *.vtt);;All Files (*.*)"
        )
        if fp and os.path.exists(fp):
            for enc in ("utf-8-sig", "utf-8", "utf-16", "cp1258", "latin-1"):
                try:
                    with open(fp, "r", encoding=enc) as f:
                        editor.setPlainText(f.read())
                    break
                except Exception:
                    continue

    btn_clip.clicked.connect(_on_paste_clip)
    btn_file.clicked.connect(_on_pick_file)
    btn_clear.clicked.connect(editor.clear)

    btn_cancel_dlg = PushButton("Đóng", dlg)
    btn_cancel_dlg.setFixedWidth(90)
    btn_cancel_dlg.clicked.connect(dlg.reject)

    btn_apply_only = PrimaryPushButton("✓ Nạp Kịch Bản", dlg)
    btn_apply_only.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_apply_only.setStyleSheet(f"""
        PrimaryPushButton, PushButton {{
            background: {Gradients.BLUE_PURPLE};
            color: #FFFFFF;
            font-weight: 700;
            border: 1px solid #818CF8;
            border-radius: 8px;
            padding: 7px 16px;
        }}
        PrimaryPushButton:hover, PushButton:hover {{
            background: {Gradients.BLUE_PURPLE_HOVER};
            border: 1px solid #C4B5FD;
        }}
    """)

    btn_apply_and_voice = PrimaryPushButton("🎙️ Nạp & Tạo Giọng AI Ngay", dlg)
    btn_apply_and_voice.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_apply_and_voice.setStyleSheet(f"""
        PrimaryPushButton, PushButton {{
            background: {Gradients.INDIGO_VIOLET_PINK};
            color: #FFFFFF;
            font-weight: 800;
            border: 1px solid #F472B6;
            border-radius: 8px;
            padding: 7px 18px;
        }}
        PrimaryPushButton:hover, PushButton:hover {{
            background: {Gradients.INDIGO_VIOLET_PINK_HOVER};
            border: 1px solid #F9A8D4;
        }}
    """)

    def _do_submit(run_voice: bool):
        t_mode = "trans" if combo_target.currentIndex() == 0 else "orig"
        if run_voice:
            t_mode = "trans"
        ok = self._apply_imported_transcript(editor.toPlainText(), target_mode=t_mode, auto_run_voice=run_voice)
        if ok:
            dlg.accept()

    btn_apply_only.clicked.connect(lambda: _do_submit(False))
    btn_apply_and_voice.clicked.connect(lambda: _do_submit(True))

    foot_row.addWidget(btn_cancel_dlg)
    foot_row.addWidget(btn_apply_only)
    foot_row.addWidget(btn_apply_and_voice)
    vbox.addLayout(foot_row)

    dlg.exec()

HomeInterface._open_paste_transcript_dialog = _open_paste_transcript_dialog


# ─── Auto-clean & Polish any legacy/corrupted 'zh-CN' subtitles on load ──────
SrtListWidget = getattr(_base_mod, 'SrtListWidget', None)
if SrtListWidget is not None and hasattr(SrtListWidget, 'load_srt'):
    _orig_srt_list_load = SrtListWidget.load_srt

    def _patched_srt_list_load(self, srt_path):
        try:
            if srt_path and os.path.exists(srt_path):
                with open(srt_path, 'r', encoding='utf-8') as f:
                    raw = f.read()
                if re.search(r'(?:zh-CN|zh-TW|zh-HK|en-US|ja-JP|ko-KR)', raw, flags=re.IGNORECASE):
                    import pysrt
                    from app.core.ai_translator import (
                        strip_stray_lang_tags,
                        polish_vietnamese_dubbing,
                        harmonize_vietnamese_dialogue_batch,
                    )
                    subs = pysrt.open(srt_path, encoding='utf-8')
                    orig_lines = []
                    orig_candidate = os.path.join(os.path.dirname(srt_path), 'temp_original.srt')
                    if os.path.exists(orig_candidate) and os.path.abspath(orig_candidate) != os.path.abspath(srt_path):
                        try:
                            orig_subs = pysrt.open(orig_candidate, encoding='utf-8')
                            if len(orig_subs) == len(subs):
                                orig_lines = [s.text.replace('\n', ' ').strip() for s in orig_subs]
                        except Exception:
                            pass
                    trans_lines = [strip_stray_lang_tags(s.text.replace('\n', ' ').strip()) for s in subs]
                    if orig_lines and len(orig_lines) == len(trans_lines):
                        cleaned_lines = harmonize_vietnamese_dialogue_batch(orig_lines, trans_lines)
                    else:
                        cleaned_lines = [polish_vietnamese_dubbing(t, t) for t in trans_lines]
                    for idx_s, c_text in enumerate(cleaned_lines):
                        if idx_s < len(subs) and c_text:
                            subs[idx_s].text = c_text
                    subs.save(srt_path, encoding='utf-8')
        except Exception as e:
            print(f"[HikariDub] auto-clean srt load error: {e}")
        return _orig_srt_list_load(self, srt_path)

    SrtListWidget.load_srt = _patched_srt_list_load




"""
Hikari Tsukimi — Universal View Enhancer
Unifies all 10 application views, cards, and dialogs under the
Modern SaaS • Premium UI • Creative Technology design system without
modifying any underlying business logic or event handlers.
"""

from __future__ import annotations
from PyQt6.QtWidgets import QWidget, QStackedWidget, QLabel, QPushButton
from qfluentwidgets import CardWidget, SimpleCardWidget, PushButton, PrimaryPushButton

from app.common.design_system import Colors, Gradients
from app.components.modern_effects import (
    attach_hover_glow, install_stacked_fade_transition, install_dialog_entrance
)


HERO_CTA_QSS = f"""
    PrimaryPushButton, PushButton, QPushButton {{
        background: {Gradients.INDIGO_VIOLET_PINK};
        color: #FFFFFF;
        font-weight: 800;
        font-size: 13px;
        letter-spacing: 0.4px;
        border: 1px solid #C084FC;
        border-radius: 9px;
        padding: 8px 16px;
    }}
    PrimaryPushButton:hover, PushButton:hover, QPushButton:hover {{
        background: {Gradients.INDIGO_VIOLET_PINK_HOVER};
        border: 1px solid #F472B6;
        color: #FFFFFF;
    }}
    PrimaryPushButton:pressed, PushButton:pressed, QPushButton:pressed {{
        background: {Gradients.INDIGO_VIOLET_PINK_PRESSED};
        border: 1px solid {Colors.PRIMARY};
    }}
    PrimaryPushButton:disabled, PushButton:disabled, QPushButton:disabled {{
        background: #161D31;
        color: #475569;
        border: 1px solid #222D48;
    }}
"""

PRIMARY_GRAD_QSS = f"""
    PrimaryPushButton, PushButton {{
        background: {Gradients.BLUE_PURPLE};
        color: #FFFFFF;
        font-weight: 700;
        font-size: 12px;
        border: 1px solid #818CF8;
        border-radius: 8px;
        padding: 6px 14px;
    }}
    PrimaryPushButton:hover, PushButton:hover {{
        background: {Gradients.BLUE_PURPLE_HOVER};
        border: 1px solid #C4B5FD;
        color: #FFFFFF;
    }}
    PrimaryPushButton:pressed, PushButton:pressed {{
        background: {Gradients.BLUE_PURPLE_PRESSED};
    }}
    PrimaryPushButton:disabled, PushButton:disabled {{
        background: #161D31;
        color: #475569;
        border: 1px solid #222D48;
    }}
"""

CYAN_BLUE_BTN_QSS = f"""
    PushButton, PrimaryPushButton {{
        background: {Gradients.CYAN_BLUE};
        color: #FFFFFF;
        font-weight: 700;
        font-size: 12px;
        border: 1px solid #38BDF8;
        border-radius: 8px;
        padding: 6px 14px;
    }}
    PushButton:hover, PrimaryPushButton:hover {{
        background: {Gradients.CYAN_BLUE_HOVER};
        border: 1px solid #7DD3FC;
        color: #FFFFFF;
    }}
    PushButton:pressed, PrimaryPushButton:pressed {{
        background: #0284C7;
    }}
    PushButton:disabled, PrimaryPushButton:disabled {{
        background: #161D31;
        color: #475569;
        border: 1px solid #222D48;
    }}
"""

DANGER_BTN_QSS = f"""
    PushButton, QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(239, 68, 68, 0.22), stop:1 rgba(236, 72, 153, 0.22));
        color: #FDA4AF;
        font-weight: 700;
        font-size: 12px;
        border: 1px solid rgba(244, 63, 94, 0.55);
        border-radius: 8px;
        padding: 6px 12px;
    }}
    PushButton:hover, QPushButton:hover {{
        background: {Gradients.DANGER_GRAD};
        color: #FFFFFF;
        border: 1px solid #F472B6;
    }}
    PushButton:pressed, QPushButton:pressed {{
        background: #BE123C;
        color: #FFFFFF;
    }}
    PushButton:disabled, QPushButton:disabled {{
        background: #141A2C;
        color: #475569;
        border: 1px solid #1E2740;
    }}
"""

PAGE_TITLE_QSS = f"""
    color: {Colors.TEXT_PRIMARY};
    font-size: 18px;
    font-weight: 800;
    letter-spacing: 0.4px;
"""


def enhance_all_views(main_window):
    """
    Applies cohesive Modern SaaS styling, gradients, and animations across all
    secondary views and dialogs attached to MainWindow.
    """
    # 1. Attach hover glow & stacked transitions across all views
    views = [
        getattr(main_window, "homeInterface", None),
        getattr(main_window, "libraryInterface", None),
        getattr(main_window, "highlightInterface", None),
        getattr(main_window, "splitterInterface", None),
        getattr(main_window, "mergerInterface", None),
        getattr(main_window, "douyinInterface", None),
        getattr(main_window, "ttsInterface", None),
        getattr(main_window, "dictInterface", None),
        getattr(main_window, "reportInterface", None),
        getattr(main_window, "settingInterface", None),
    ]

    for v in views:
        if v is None:
            continue
        _enhance_generic_containers(v)

    # 2. Specific View Polish
    _enhance_highlight_view(getattr(main_window, "highlightInterface", None))
    _enhance_splitter_view(getattr(main_window, "splitterInterface", None))
    _enhance_merger_view(getattr(main_window, "mergerInterface", None))
    _enhance_douyin_view(getattr(main_window, "douyinInterface", None))
    _enhance_tts_view(getattr(main_window, "ttsInterface", None))
    _enhance_dict_view(getattr(main_window, "dictInterface", None))
    _enhance_report_view(getattr(main_window, "reportInterface", None))
    _enhance_setting_view(getattr(main_window, "settingInterface", None))
    _enhance_dialogs()


def _enhance_generic_containers(view: QWidget):
    """Attaches smooth hover glow to cards, transparent scroll backgrounds, and fade transitions."""
    try:
        view.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        if hasattr(view, "view") and isinstance(view.view, QWidget):
            view.view.setStyleSheet("background: transparent; border: none;")
        if hasattr(view, "scrollArea") and isinstance(view.scrollArea, QWidget):
            view.scrollArea.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        for card in view.findChildren(CardWidget):
            attach_hover_glow(card)
        for sw in view.findChildren(QStackedWidget):
            install_stacked_fade_transition(sw)
    except Exception:
        pass


def _enhance_highlight_view(view):
    if not view:
        return
    try:
        if hasattr(view, "btn_start"):
            view.btn_start.setText("✦ BẮT ĐẦU CẮT HIGHLIGHT (AUTO)")
            view.btn_start.setStyleSheet(HERO_CTA_QSS)
        if hasattr(view, "btn_delete"):
            view.btn_delete.setText("🗑 Xóa mục đã chọn")
            view.btn_delete.setStyleSheet(DANGER_BTN_QSS)
    except Exception as e:
        print(f"[ViewEnhancer] Highlight warning: {e}")


def _enhance_splitter_view(view):
    if not view:
        return
    try:
        if hasattr(view, "lbl_title"):
            view.lbl_title.setText("✂️ CHIA TẬP VIDEO THÔNG MINH")
            view.lbl_title.setStyleSheet(PAGE_TITLE_QSS)
        card = getattr(view, "card", None)
        if card:
            card.setStyleSheet("")  # Let patched CardWidget paintEvent render glass surface
            attach_hover_glow(card)
            if hasattr(card, "btn_run"):
                card.btn_run.setText("▶ Bắt đầu chia tập Video")
                card.btn_run.setStyleSheet(HERO_CTA_QSS)
            if hasattr(card, "lbl_preview"):
                card.lbl_preview.setStyleSheet(f"color: {Colors.ACCENT_BRIGHT}; font-weight: 700; font-size: 13px;")
            if hasattr(card, "lbl_status"):
                card.lbl_status.setStyleSheet(f"color: {Colors.SUCCESS}; font-weight: 600;")
    except Exception as e:
        print(f"[ViewEnhancer] Splitter warning: {e}")


def _enhance_merger_view(view):
    if not view:
        return
    try:
        if hasattr(view, "lbl_title"):
            view.lbl_title.setText("🎬 GHÉP NỐI NHIỀU VIDEO CHUYÊN NGHIỆP")
            view.lbl_title.setStyleSheet(PAGE_TITLE_QSS)
        card = getattr(view, "card", None)
        if card:
            card.setStyleSheet("")
            attach_hover_glow(card)
            if hasattr(card, "btn_run"):
                card.btn_run.setText("▶ Bắt đầu Gộp Video")
                card.btn_run.setStyleSheet(HERO_CTA_QSS)
            if hasattr(card, "btn_cancel"):
                card.btn_cancel.setStyleSheet(DANGER_BTN_QSS)
            if hasattr(card, "btn_delete"):
                card.btn_delete.setStyleSheet(DANGER_BTN_QSS)
            if hasattr(card, "btn_clear"):
                card.btn_clear.setStyleSheet(DANGER_BTN_QSS)
            if hasattr(card, "lbl_progress_pct"):
                card.lbl_progress_pct.setStyleSheet(f"color: {Colors.ACCENT_BRIGHT}; font-weight: 800; min-width: 44px;")
    except Exception as e:
        print(f"[ViewEnhancer] Merger warning: {e}")


def _enhance_douyin_view(view):
    if not view:
        return
    try:
        if hasattr(view, "title_label"):
            view.title_label.setText("🌐 TẢI VIDEO DOUYIN • TIKTOK • BILIBILI")
            view.title_label.setStyleSheet(PAGE_TITLE_QSS)
        if hasattr(view, "beta_warning_label"):
            view.beta_warning_label.setText("✦ Hỗ trợ tải video chất lượng gốc không logo & xử lý đa luồng")
            view.beta_warning_label.setStyleSheet(f"""
                color: {Colors.ACCENT_BRIGHT};
                font-size: 12px;
                font-weight: 600;
            """)
        if hasattr(view, "btn_scan"):
            view.btn_scan.setText("⚡ Phân tích && Tải")
            view.btn_scan.setStyleSheet(PRIMARY_GRAD_QSS)
        if hasattr(view, "btn_download"):
            view.btn_download.setText("⬇ Tải Xuống Ngay")
            view.btn_download.setStyleSheet(HERO_CTA_QSS)
        if hasattr(view, "btn_cancel"):
            view.btn_cancel.setStyleSheet(DANGER_BTN_QSS)
        if hasattr(view, "cover_label"):
            view.cover_label.setStyleSheet(f"""
                background-color: {Colors.BG_DEEP};
                border: 1px solid {Colors.BORDER};
                border-radius: 10px;
                color: {Colors.TEXT_MUTED};
                font-weight: 600;
            """)
    except Exception as e:
        print(f"[ViewEnhancer] Douyin warning: {e}")


def _enhance_tts_view(view):
    if not view:
        return
    try:
        if hasattr(view, "btn_run"):
            view.btn_run.setText("🎙️ Tạo Giọng Đọc AI Ngay")
            view.btn_run.setStyleSheet(HERO_CTA_QSS)
        if hasattr(view, "btn_play"):
            view.btn_play.setText("▶ Phát thử")
            view.btn_play.setStyleSheet(CYAN_BLUE_BTN_QSS)
        if hasattr(view, "btn_delete"):
            view.btn_delete.setStyleSheet(DANGER_BTN_QSS)
        if hasattr(view, "char_count_lbl"):
            view.char_count_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; font-weight: 600;")
    except Exception as e:
        print(f"[ViewEnhancer] TTS warning: {e}")


def _enhance_dict_view(view):
    if not view:
        return
    try:
        if hasattr(view, "titleLabel"):
            view.titleLabel.setText("📖 TỪ ĐIỂN PHÁT ÂM TÙY CHỈNH (TTS)")
            view.titleLabel.setStyleSheet(PAGE_TITLE_QSS)
        if hasattr(view, "btnAdd"):
            view.btnAdd.setText("＋ Thêm Quy Tắc")
            view.btnAdd.setStyleSheet(PRIMARY_GRAD_QSS)
        if hasattr(view, "btnDelete"):
            view.btnDelete.setText("🗑 Xóa từ đã chọn")
            view.btnDelete.setStyleSheet(DANGER_BTN_QSS)
    except Exception as e:
        print(f"[ViewEnhancer] Dict warning: {e}")


def _enhance_report_view(view):
    if not view:
        return
    try:
        if hasattr(view, "btn_send"):
            view.btn_send.setText("🚀 Gửi Báo Cáo Lỗi")
            view.btn_send.setStyleSheet(HERO_CTA_QSS)
        if hasattr(view, "btn_chat_send"):
            view.btn_chat_send.setText("Gửi tin nhắn")
            view.btn_chat_send.setStyleSheet(PRIMARY_GRAD_QSS)
        if hasattr(view, "char_count_lbl"):
            view.char_count_lbl.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px;")
    except Exception as e:
        print(f"[ViewEnhancer] Report warning: {e}")


def _enhance_setting_view(view):
    if not view:
        return
    try:
        if hasattr(view, "btn_save"):
            view.btn_save.setText("💾 Lưu Toàn Bộ Cài Đặt")
            view.btn_save.setStyleSheet(HERO_CTA_QSS)
        if hasattr(view, "btn_download_models"):
            view.btn_download_models.setText("⬇ Tải / Kiểm Tra Tất Cả Model AI")
            view.btn_download_models.setStyleSheet(PRIMARY_GRAD_QSS)
        if hasattr(view, "btn_clean_c_drive"):
            view.btn_clean_c_drive.setText("🧹 Dọn dẹp bộ nhớ Cache")
        if hasattr(view, "text_model_log"):
            view.text_model_log.setStyleSheet(f"""
                TextEdit {{
                    background-color: {Colors.BG_DEEP};
                    color: {Colors.ACCENT_BRIGHT};
                    border: 1px solid {Colors.BORDER};
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-family: 'Consolas', 'Fira Code', monospace;
                    font-size: 12px;
                }}
            """)
        if hasattr(view, "lbl_hwid"):
            view.lbl_hwid.setStyleSheet(f"""
                color: {Colors.ACCENT_BRIGHT};
                font-family: 'Consolas', monospace;
                font-weight: 700;
                background-color: {Colors.BG_DEEP};
                border: 1px solid {Colors.BORDER};
                padding: 6px 10px;
                border-radius: 6px;
            """)
    except Exception as e:
        print(f"[ViewEnhancer] Setting warning: {e}")


def _enhance_dialogs():
    """Enhances StyleDialog and MessageBox with entrance animation & gradient actions."""
    try:
        import app.views.style_dialog as sd
        install_dialog_entrance(sd.StyleDialog)

        if not getattr(sd.StyleDialog, "_hikari_style_patched", False):
            _orig_sd_init = sd.StyleDialog.__init__

            def _patched_sd_init(self, *args, **kwargs):
                _orig_sd_init(self, *args, **kwargs)
                try:
                    self.setStyleSheet(f"background-color: {Colors.BG_DARK}; color: {Colors.TEXT_PRIMARY};")
                    if hasattr(self, "stackedWidget"):
                        install_stacked_fade_transition(self.stackedWidget)
                    if hasattr(self, "btn_save"):
                        self.btn_save.setText("✦ Lưu Tùy Chỉnh")
                        self.btn_save.setStyleSheet(HERO_CTA_QSS)
                    if hasattr(self, "btn_cancel"):
                        self.btn_cancel.setStyleSheet(DANGER_BTN_QSS)
                except Exception:
                    pass

            sd.StyleDialog.__init__ = _patched_sd_init
            sd.StyleDialog._hikari_style_patched = True
    except Exception as e:
        print(f"[ViewEnhancer] StyleDialog warning: {e}")

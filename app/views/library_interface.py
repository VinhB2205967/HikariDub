"""
Library Interface Module - Hikari Dub v3.0 AI Dubbing Studio
Wraps and patches LibraryInterface and VideoCard with the Modern SaaS
gradient & glassmorphic design system.
"""

import os
import sys
import importlib.util
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QApplication
from PyQt6.QtCore import Qt
from qfluentwidgets import PrimaryPushButton, PushButton, TransparentToolButton, FluentIcon as FIF

from app.common.design_system import Colors, Gradients
from app.components.modern_effects import attach_hover_glow, ModernEmptyState

# Find base library_interface.pyc
_pyc_path = None
for cand in [
    os.path.join(os.path.dirname(__file__), "library_interface.pyc"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "pyc_dump", "app", "views", "library_interface.pyc"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pyc_dump", "app", "views", "library_interface.pyc"),
    r"D:\HikariDub\pyc_dump\app\views\library_interface.pyc",
    r"D:\Hikari_Dub\pyc_dump\app\views\library_interface.pyc"
]:
    if os.path.exists(cand):
        _pyc_path = cand
        break

if not _pyc_path:
    raise FileNotFoundError("Could not find base library_interface.pyc")

_spec = importlib.util.spec_from_file_location("app.views.library_interface_base", _pyc_path)
_base_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base_mod)

for attr in dir(_base_mod):
    if not attr.startswith('__'):
        globals()[attr] = getattr(_base_mod, attr)

LibraryInterface = _base_mod.LibraryInterface
VideoCard = _base_mod.VideoCard

# 1. Patch LibraryInterface.__init__ to apply Modern SaaS layout & styling
_orig_lib_init = LibraryInterface.__init__
def _lib_init_patched(self, parent=None):
    _orig_lib_init(self, parent)
    try:
        self.col1_widget.setObjectName("hikariLibCard")
        self.col1_widget.setStyleSheet("")
        attach_hover_glow(self.col1_widget)

        self.btn_refresh.setText("Làm Mới Danh Sách")
        self.btn_refresh.setMinimumWidth(175)
        self.btn_open_all.setText("Mở Thư Mục Xuất")
        self.btn_open_all.setMinimumWidth(175)

        self.btn_open_all.setStyleSheet(f"""
            PrimaryPushButton, PushButton {{
                background: {Gradients.BLUE_PURPLE};
                color: #FFFFFF;
                font-weight: 700;
                border: 1px solid #818CF8;
                border-radius: 8px;
                padding: 6px 16px 6px 36px;
            }}
            PrimaryPushButton:hover, PushButton:hover {{
                background: {Gradients.BLUE_PURPLE_HOVER};
                border: 1px solid #C4B5FD;
                color: #FFFFFF;
            }}
        """)

        if hasattr(self, 'col1_layout') and self.col1_layout.count() > 0:
            hl = self.col1_layout.itemAt(0).layout()
            if hl and hl.count() > 0 and hl.itemAt(0).widget():
                lbl = hl.itemAt(0).widget()
                lbl.setText("🎬 DỰ ÁN & VIDEO ĐÃ HOÀN TẤT")
                lbl.setStyleSheet(f"""
                    color: {Colors.TEXT_PRIMARY};
                    font-weight: 800;
                    font-size: 15px;
                    letter-spacing: 0.6px;
                """)
    except Exception as e:
        print(f"Lỗi khởi tạo giao diện Library: {e}")

LibraryInterface.__init__ = _lib_init_patched

# 2. Patch VideoCard.__init__ to render modern SaaS studio cards with gradient actions
_orig_card_init = VideoCard.__init__
def _card_init_patched(self, video_path, workspace_path, status, parent=None):
    _orig_card_init(self, video_path, workspace_path, status, parent)
    try:
        attach_hover_glow(self)
        self.setStyleSheet(f"""
            VideoCard {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1A2238, stop:1 #13192B);
                border-radius: 12px;
                border: 1px solid {Colors.BORDER};
            }}
            VideoCard:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #212B46, stop:1 #171F35);
                border: 1px solid {Colors.PRIMARY};
            }}
        """)
        if hasattr(self, 'lbl_name'):
            self.lbl_name.setStyleSheet(f"font-weight: 700; font-size: 13px; color: {Colors.TEXT_PRIMARY};")

        if hasattr(self, 'btn_play') and self.status == 'completed':
            self.btn_play.setText("Phát Video")
            self.btn_play.setStyleSheet(f"""
                PrimaryPushButton, QPushButton {{
                    background: {Gradients.BLUE_PURPLE};
                    color: #FFFFFF;
                    font-weight: 700;
                    border-radius: 7px;
                    border: 1px solid #818CF8;
                    padding: 5px 12px 6px 34px;
                }}
                PrimaryPushButton:hover, QPushButton:hover {{
                    background: {Gradients.INDIGO_VIOLET_PINK_HOVER};
                    border: 1px solid #F472B6;
                }}
            """)
        elif hasattr(self, 'btn_play') and self.status == 'processing':
            self.btn_play.setText("Xóa Dữ Liệu Tạm")
            self.btn_play.setStyleSheet(f"""
                QPushButton, PushButton {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(239, 68, 68, 0.25), stop:1 rgba(236, 72, 153, 0.25));
                    color: #FDA4AF;
                    font-weight: 700;
                    border-radius: 7px;
                    border: 1px solid rgba(244, 63, 94, 0.6);
                    padding: 5px 12px 6px 34px;
                }}
                QPushButton:hover, PushButton:hover {{
                    background: {Gradients.DANGER_GRAD};
                    color: #FFFFFF;
                }}
            """)

        if hasattr(self, 'btn_title'):
            self.btn_title.setStyleSheet(f"""
                QPushButton, PushButton {{
                    background: #151B2E;
                    color: {Colors.ACCENT_BRIGHT};
                    font-weight: 600;
                    border-radius: 7px;
                    border: 1px solid {Colors.BORDER};
                    font-size: 12px;
                }}
                QPushButton:hover, PushButton:hover {{
                    background: {Gradients.CYAN_BLUE};
                    color: #FFFFFF;
                    border: 1px solid #38BDF8;
                }}
            """)
    except Exception as e:
        print(f"Lỗi khởi tạo VideoCard: {e}")

VideoCard.__init__ = _card_init_patched

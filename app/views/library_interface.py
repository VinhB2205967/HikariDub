"""
Library Interface Module - Hikari Dub v3.0 AI Dubbing Studio
Wraps and patches LibraryInterface and VideoCard with the unified creative studio design system.
"""

import os
import sys
import importlib.util
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QApplication
from PyQt6.QtCore import Qt
from qfluentwidgets import PrimaryPushButton, PushButton, TransparentToolButton, FluentIcon as FIF

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

# 1. Patch LibraryInterface.__init__ to apply creative studio layout & styling
_orig_lib_init = LibraryInterface.__init__
def _lib_init_patched(self, parent=None):
    _orig_lib_init(self, parent)
    try:
        self.col1_widget.setObjectName("hikariLibCard")
        self.col1_widget.setStyleSheet("""
            #hikariLibCard {
                background-color: #121620;
                border: 1px solid #293244;
                border-radius: 12px;
            }
        """)
        
        self.btn_refresh.setText("🔄 Làm Mới")
        self.btn_open_all.setText("📂 Mở Thư Mục Xuất")
        
        if hasattr(self, 'col1_layout') and self.col1_layout.count() > 0:
            hl = self.col1_layout.itemAt(0).layout()
            if hl and hl.count() > 0 and hl.itemAt(0).widget():
                lbl = hl.itemAt(0).widget()
                lbl.setText("🎬 DỰ ÁN & VIDEO ĐÃ HOÀN TẤT")
                lbl.setStyleSheet("color: #22D3EE; font-weight: 700; font-size: 14px; letter-spacing: 0.5px;")
    except Exception as e:
        print(f"Lỗi khởi tạo giao diện Library: {e}")

LibraryInterface.__init__ = _lib_init_patched

# 2. Patch VideoCard.__init__ to render modern studio cards with cyan highlights
_orig_card_init = VideoCard.__init__
def _card_init_patched(self, video_path, workspace_path, status, parent=None):
    _orig_card_init(self, video_path, workspace_path, status, parent)
    try:
        self.setStyleSheet("""
            VideoCard {
                background-color: #191F2B;
                border-radius: 10px;
                border: 1px solid #293244;
            }
            VideoCard:hover {
                background-color: #222A39;
                border: 1px solid #22D3EE;
            }
        """)
        if hasattr(self, 'lbl_name'):
            self.lbl_name.setStyleSheet("font-weight: 700; font-size: 13px; color: #F1F5F9;")
            
        if hasattr(self, 'btn_play') and self.status == 'completed':
            self.btn_play.setText("▶ Phát Video")
            self.btn_play.setStyleSheet("""
                PrimaryPushButton {
                    background-color: #22D3EE;
                    color: #0B0D12;
                    font-weight: 700;
                    border-radius: 6px;
                    border: none;
                }
                PrimaryPushButton:hover {
                    background-color: #38BDF8;
                }
            """)
        elif hasattr(self, 'btn_play') and self.status == 'processing':
            self.btn_play.setText("🗑 Xóa Dữ Liệu Tạm")
            self.btn_play.setStyleSheet("""
                QPushButton {
                    background-color: #7F1D1D;
                    color: #FCA5A5;
                    font-weight: 700;
                    border-radius: 6px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #991B1B;
                }
            """)
            
        if hasattr(self, 'btn_title'):
            self.btn_title.setStyleSheet("""
                QPushButton {
                    background-color: #191F2B;
                    color: #22D3EE;
                    font-weight: 600;
                    border-radius: 6px;
                    border: 1px solid #293244;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #222A39;
                    border: 1px solid #22D3EE;
                }
            """)
    except Exception as e:
        print(f"Lỗi khởi tạo VideoCard: {e}")

VideoCard.__init__ = _card_init_patched


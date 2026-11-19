"""
Library Interface Module - Pure Python Edition (Hikari Dub v3.0 AI Dubbing Studio).
Displays completed video projects with Modern SaaS cards.
"""

import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt
from qfluentwidgets import PrimaryPushButton, PushButton, FluentIcon as FIF

from app.common.design_system import Colors, Gradients
from app.common.config_manager import get_config
from app.components.modern_effects import attach_hover_glow, ModernEmptyState


class VideoCard(QFrame):
    """Card displaying a completed video project."""

    def __init__(self, video_path: str, workspace_path: str = "", status: str = "completed", parent=None):
        super().__init__(parent)
        self.video_path = video_path
        self.workspace_path = workspace_path
        self.status = status

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

        lay = QHBoxLayout(self)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(12)

        info_col = QVBoxLayout()
        self.lbl_name = QLabel(os.path.basename(video_path), self)
        self.lbl_name.setStyleSheet(f"font-weight: 700; font-size: 13px; color: {Colors.TEXT_PRIMARY}; background: transparent; border: none;")
        info_col.addWidget(self.lbl_name)

        size_mb = 0.0
        try:
            size_mb = os.path.getsize(video_path) / (1024 * 1024)
        except Exception:
            pass
        self.lbl_meta = QLabel(f"{size_mb:.1f} MB • {os.path.dirname(video_path)}", self)
        self.lbl_meta.setStyleSheet(f"font-size: 11px; color: {Colors.TEXT_SECONDARY}; background: transparent; border: none;")
        info_col.addWidget(self.lbl_meta)
        lay.addLayout(info_col, 1)

        self.btn_play = PrimaryPushButton(FIF.PLAY, "Phát Video", self)
        self.btn_play.setStyleSheet(f"""
            PrimaryPushButton, QPushButton {{
                background: {Gradients.BLUE_PURPLE};
                color: #FFFFFF;
                font-weight: 700;
                border-radius: 7px;
                border: 1px solid #818CF8;
                padding: 5px 14px;
            }}
        """)
        self.btn_play.clicked.connect(lambda: os.startfile(self.video_path) if os.path.exists(self.video_path) else None)
        lay.addWidget(self.btn_play)

        self.btn_folder = PushButton(FIF.FOLDER, "Mở Thư Mục", self)
        self.btn_folder.clicked.connect(lambda: os.startfile(os.path.dirname(self.video_path)) if os.path.exists(os.path.dirname(self.video_path)) else None)
        lay.addWidget(self.btn_folder)


class LibraryInterface(QWidget):
    """Project library interface showing rendered output videos."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("libraryInterface")

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)

        self.col1_widget = QWidget(self)
        self.col1_widget.setObjectName("hikariLibCard")
        attach_hover_glow(self.col1_widget)
        self.col1_layout = QVBoxLayout(self.col1_widget)
        self.col1_layout.setContentsMargins(16, 16, 16, 16)
        self.col1_layout.setSpacing(12)

        header = QHBoxLayout()
        lbl_title = QLabel("🎬 DỰ ÁN & VIDEO ĐÃ HOÀN TẤT", self.col1_widget)
        lbl_title.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-weight: 800; font-size: 15px; letter-spacing: 0.6px;")
        header.addWidget(lbl_title)
        header.addStretch(1)

        self.btn_refresh = PushButton(FIF.SYNC, "Làm Mới Danh Sách", self.col1_widget)
        self.btn_refresh.setMinimumWidth(175)
        self.btn_refresh.clicked.connect(self.refresh_list)
        header.addWidget(self.btn_refresh)

        self.btn_open_all = PrimaryPushButton("📂 Mở Thư Mục Xuất", self.col1_widget)
        self.btn_open_all.setMinimumWidth(180)
        self.btn_open_all.setStyleSheet(f"""
            PrimaryPushButton, PushButton {{
                background: {Gradients.BLUE_PURPLE};
                color: #FFFFFF;
                font-weight: 700;
                border: 1px solid #818CF8;
                border-radius: 8px;
                padding: 6px 16px;
            }}
            PrimaryPushButton:hover, PushButton:hover {{
                background: {Gradients.BLUE_PURPLE_HOVER};
                border: 1px solid #C4B5FD;
                color: #FFFFFF;
            }}
        """)
        self.btn_open_all.clicked.connect(self._open_output_dir)
        header.addWidget(self.btn_open_all)
        self.col1_layout.addLayout(header)

        self.scroll = QScrollArea(self.col1_widget)
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        self.list_container = QWidget()
        self.list_container.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(10)
        self.scroll.setWidget(self.list_container)
        self.col1_layout.addWidget(self.scroll, 1)

        root.addWidget(self.col1_widget, 1)
        self.refresh_list()

    def _get_output_dir(self) -> str:
        return get_config("output_dir", os.path.join(os.getcwd(), "Output"))

    def _open_output_dir(self):
        out_dir = self._get_output_dir()
        os.makedirs(out_dir, exist_ok=True)
        os.startfile(out_dir)

    def refresh_list(self):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        out_dir = self._get_output_dir()
        videos = []
        if os.path.isdir(out_dir):
            for fname in sorted(os.listdir(out_dir), reverse=True):
                if fname.lower().endswith((".mp4", ".mkv", ".mov", ".avi")):
                    videos.append(os.path.join(out_dir, fname))

        if not videos:
            empty = ModernEmptyState(
                "🎬",
                "Chưa có video đã xuất",
                "Hãy chọn video ở Bảng Điều Khiển và nhấn Render Video để xem thành quả tại đây.",
                parent=self.list_container
            )
            self.list_layout.addWidget(empty)
        else:
            for vp in videos:
                self.list_layout.addWidget(VideoCard(vp, out_dir, "completed", self.list_container))

        self.list_layout.addStretch(1)

"""
Pronunciation Dictionary Interface Module - Hikari Tsukimi Studio.
"""

import json
import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from qfluentwidgets import PrimaryPushButton, PlainTextEdit, InfoBar, InfoBarPosition, FluentIcon as FIF
from app.common.design_system import Colors


class DictionaryInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dictionaryInterface")
        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self._dict_path = os.path.join(root, "Data", "pronunciation_dict.json")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        lbl = QLabel("📖 Từ Điển Phát Âm Tùy Chỉnh (JSON)", self)
        lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 16px; font-weight: 700;")
        lay.addWidget(lbl)

        self.txt_dict = PlainTextEdit(self)
        self.txt_dict.setPlaceholderText('{\n  "AI": "ây ai",\n  "TTS": "ti ti ét"\n}')
        lay.addWidget(self.txt_dict, 1)

        row = QHBoxLayout()
        row.addStretch(1)
        btn_save = PrimaryPushButton(FIF.SAVE, "Lưu Từ Điển", self)
        btn_save.clicked.connect(self._save)
        row.addWidget(btn_save)
        lay.addLayout(row)

        self._load()

    def _load(self):
        if os.path.exists(self._dict_path):
            try:
                with open(self._dict_path, "r", encoding="utf-8") as f:
                    self.txt_dict.setPlainText(f.read())
            except Exception:
                pass

    def _save(self):
        try:
            raw = self.txt_dict.toPlainText().strip() or "{}"
            data = json.loads(raw)
            os.makedirs(os.path.dirname(self._dict_path), exist_ok=True)
            with open(self._dict_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            InfoBar.success("Đã lưu", "Từ điển phát âm đã được lưu.", parent=self, position=InfoBarPosition.TOP)
        except Exception as e:
            InfoBar.error("Lỗi JSON", str(e), parent=self, position=InfoBarPosition.TOP)

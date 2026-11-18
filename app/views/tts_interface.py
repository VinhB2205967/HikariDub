"""
TTS Studio Interface Module - Hikari Tsukimi Studio.
"""

import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog
from qfluentwidgets import PrimaryPushButton, ComboBox, PlainTextEdit, InfoBar, InfoBarPosition, FluentIcon as FIF
from app.common.design_system import Colors


class TTSInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ttsInterface")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 20, 24, 20)
        lay.setSpacing(12)

        lbl = QLabel("🎙️ Phòng Thu Giọng Đọc AI (Piper TTS Local)", self)
        lbl.setStyleSheet(f"color: {Colors.TEXT_PRIMARY}; font-size: 16px; font-weight: 700;")
        lay.addWidget(lbl)

        row = QHBoxLayout()
        row.addWidget(QLabel("Giọng đọc:", self))
        self.combo_voice = ComboBox(self)
        for label, vid in [
            ("Ban Mai (Nữ)", "banmai"),
            ("Mạnh Dũng (Nam)", "manhdung"),
            ("Chiêu Thanh (Nữ)", "chieuthanh"),
            ("Lạc Phi (Nữ)", "lacphi"),
            ("Ngọc Huyền (Nữ)", "ngochuyen"),
            ("Vais1000 (Nữ tự nhiên)", "vais1000"),
        ]:
            self.combo_voice.addItem(label, userData=vid)
        row.addWidget(self.combo_voice, 1)
        lay.addLayout(row)

        self.txt_input = PlainTextEdit(self)
        self.txt_input.setPlaceholderText("Nhập văn bản tiếng Việt để chuyển thành giọng nói...")
        lay.addWidget(self.txt_input, 1)

        self.btn_synth = PrimaryPushButton(FIF.MICROPHONE, "Tạo & Nghe Thử Giọng Đọc", self)
        self.btn_synth.clicked.connect(self._synthesize)
        lay.addWidget(self.btn_synth)

    def _synthesize(self):
        text = self.txt_input.toPlainText().strip()
        if not text:
            InfoBar.warning("Thiếu nội dung", "Vui lòng nhập văn bản.", parent=self, position=InfoBarPosition.TOP)
            return
        try:
            from piper import PiperVoice
            import app.core.audio_generator as ag
            vid = self.combo_voice.currentData() or "banmai"
            root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            mpath = os.path.join(root, "models", "piper", "Tiếng Việt", f"{vid}.onnx")
            if not os.path.exists(mpath):
                InfoBar.warning("Chưa có model", f"Chưa tìm thấy {mpath}. Hãy tải model trong Cài Đặt.", parent=self, position=InfoBarPosition.TOP)
                return
            voice = PiperVoice.load(mpath, mpath + ".json" if os.path.exists(mpath + ".json") else None)
            out_dir = os.path.join(root, "Data")
            temp_files = []
            out_wav = ag.fetch_piper_voice("studio", text, temp_files, None, out_dir, voice)
            if out_wav and os.path.exists(out_wav):
                os.startfile(out_wav)
                InfoBar.success("Hoàn tất", f"Đã tạo: {out_wav}", parent=self, position=InfoBarPosition.TOP)
        except Exception as e:
            InfoBar.error("Lỗi TTS", str(e), parent=self, position=InfoBarPosition.TOP)

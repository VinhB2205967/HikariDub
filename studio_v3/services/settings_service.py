"""
Settings, Project Persistence, Keyring Secret Service & i18n Manager.
Stores non-sensitive settings in JSON and sensitive credentials (TikTok Session ID, Gemini API Key)
in OS keyring (with obfuscated local fallback if keyring backend is unavailable).
"""

import base64
import json
import os
from typing import Any, Dict

SERVICE_NAME = "HikariTsukimiStudioV3"

I18N: Dict[str, Dict[str, str]] = {
    "vi": {
        "app_title": "Hikari Tsukimi — AI Dubbing & Creative Studio",
        "engine_ready": "AI Engine Sẵn sàng",
        "output_dir": "Thư mục xuất",
        "ai_config": "Cấu hình",
        "col1_title": "Dự án & Giọng đọc",
        "col2_title": "Xem trước & Timeline",
        "col3_title": "Trình biên tập phụ đề",
        "card_source": "1. Nguồn & Đầu ra",
        "card_stt": "2. Nhận dạng giọng nói (Whisper)",
        "card_tts": "3. Giọng đọc AI (Piper / TikTok)",
        "card_translate": "4. Dịch thuật & Phong cách",
        "card_audio": "5. Âm thanh & Lọc giọng",
        "select_video": "Chọn Video Nguồn",
        "no_video": "Chưa chọn video",
        "drop_hint": "Kéo video vào đây hoặc bấm Chọn video",
        "start_auto": "▶ Bắt đầu xử lý tự động",
        "cancel": "⏹ Hủy",
        "step_1": "1. Bóc băng",
        "step_2": "2. Dịch phụ đề",
        "step_3": "3. Tạo giọng AI",
        "step_4": "4. Xuất video 1080p",
    },
    "en": {
        "app_title": "Hikari Tsukimi — AI Dubbing & Creative Studio",
        "engine_ready": "AI Engine Ready",
        "output_dir": "Output Folder",
        "ai_config": "Settings",
        "col1_title": "Project & Voice",
        "col2_title": "Preview & Timeline",
        "col3_title": "Subtitle Editor",
        "card_source": "1. Source & Output",
        "card_stt": "2. Speech Recognition (Whisper)",
        "card_tts": "3. AI Voice (Piper / TikTok)",
        "card_translate": "4. Translation & Style",
        "card_audio": "5. Audio Mix & Vocal Filter",
        "select_video": "Select Source Video",
        "no_video": "No video selected",
        "drop_hint": "Drag and drop video here or click Select Video",
        "start_auto": "▶ Start Auto Processing",
        "cancel": "⏹ Cancel",
        "step_1": "1. Transcribe",
        "step_2": "2. Translate",
        "step_3": "3. Synthesize",
        "step_4": "4. Export 1080p",
    },
}


class SecretStore:
    """Secure secret manager using OS keyring with local fallback."""

    def __init__(self, fallback_path: str):
        self._fallback_path = fallback_path

    def set_secret(self, key: str, value: str) -> None:
        val = (value or "").strip()
        try:
            import keyring
            keyring.set_password(SERVICE_NAME, key, val)
            return
        except Exception:
            pass
        data = self._read_fallback()
        data[key] = base64.b64encode(val.encode("utf-8")).decode("ascii")
        os.makedirs(os.path.dirname(self._fallback_path), exist_ok=True)
        with open(self._fallback_path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def get_secret(self, key: str) -> str:
        try:
            import keyring
            res = keyring.get_password(SERVICE_NAME, key)
            if res is not None:
                return res
        except Exception:
            pass
        data = self._read_fallback()
        enc = data.get(key, "")
        if not enc:
            return ""
        try:
            return base64.b64decode(enc.encode("ascii")).decode("utf-8")
        except Exception:
            return ""

    def _read_fallback(self) -> dict:
        if os.path.exists(self._fallback_path):
            try:
                with open(self._fallback_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}


class SettingsService:
    """Manages user preferences, window geometry, and project JSON files."""

    def __init__(self, base_dir: str = None):
        self.base_dir = base_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = os.path.join(self.base_dir, "Data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.settings_path = os.path.join(self.data_dir, "studio_v3_settings.json")
        self.secrets = SecretStore(os.path.join(self.data_dir, ".secrets.json"))
        self._data: Dict[str, Any] = {
            "lang": "vi",
            "output_dir": os.path.join(self.base_dir, "Output"),
            "whisper_model": "small",
            "source_lang": "auto",
            "target_lang": "Tiếng Việt",
            "translate_style": "Tự nhiên",
            "voice_id": "piper:banmai",
            "voice_speed": 100,
            "voice_pitch": 0,
            "vocal_sep": False,
            "orig_volume": 35,
            "voice_volume": 100,
            "splitter_sizes": [310, 750, 350],
            "window_size": [1420, 860],
        }
        self.load()

    def load(self) -> Dict[str, Any]:
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    self._data.update(loaded)
            except Exception:
                pass
        return self._data

    def save(self) -> None:
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self.save()

    def tr(self, key: str) -> str:
        lang = self._data.get("lang", "vi")
        return I18N.get(lang, I18N["vi"]).get(key, key)

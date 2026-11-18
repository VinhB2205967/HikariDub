"""
Configuration Manager for Hikari Tsukimi / Hikari Dub Studio.
Stores persistent settings in Data/config.json.
"""

import json
import os
import threading

_LOCK = threading.Lock()
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_DATA_DIR = os.path.join(_PROJECT_ROOT, "Data")
_CONFIG_PATH = os.path.join(_DATA_DIR, "config.json")

_DEFAULT_CONFIG = {
    "gemini_model": "gemini-4-argon",
    "gemini_keys": [],
    "prompt_style": "Mặc định",
    "target_lang": "Tiếng Việt",
    "whisper_model": "small",
    "whisper_device": "auto",
    "tts_voice": "banmai",
    "output_dir": os.path.join(_PROJECT_ROOT, "Output"),
    "video_overlay": {},
}

_cache = None


def load_config() -> dict:
    """Load configuration from disk, merging with defaults."""
    global _cache
    with _LOCK:
        os.makedirs(_DATA_DIR, exist_ok=True)
        cfg = dict(_DEFAULT_CONFIG)
        if os.path.exists(_CONFIG_PATH):
            try:
                with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    cfg.update(data)
            except Exception:
                pass
        _cache = cfg
        return dict(cfg)


def save_config(cfg: dict) -> bool:
    """Persist configuration dictionary to disk."""
    global _cache
    with _LOCK:
        os.makedirs(_DATA_DIR, exist_ok=True)
        merged = dict(_DEFAULT_CONFIG)
        if isinstance(cfg, dict):
            merged.update(cfg)
        try:
            with open(_CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(merged, f, ensure_ascii=False, indent=2)
            _cache = merged
            return True
        except Exception:
            return False


def get_config(key: str, default=None):
    """Retrieve a single configuration value by key."""
    global _cache
    if _cache is None:
        load_config()
    return _cache.get(key, default)


def set_config(key: str, value) -> bool:
    """Update a single configuration key and persist to disk."""
    cfg = load_config()
    cfg[key] = value
    return save_config(cfg)


def get_hf_cache_dir() -> str:
    """Return the local directory used to cache Whisper / HuggingFace models."""
    cache_dir = os.path.join(_PROJECT_ROOT, "models", "whisper")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def get_paddleocr_cache_dir() -> str:
    """Return the local directory used to cache PaddleOCR models."""
    cache_dir = os.path.join(_PROJECT_ROOT, "models", "paddleocr")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def get_audio_sep_cache_dir() -> str:
    """Return the local directory used to cache audio-separator models."""
    cache_dir = os.path.join(_PROJECT_ROOT, "models", "audio_separator")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir

"""
Audio Generator Module - Hikari Tsukimi v3.0
Wraps and patches audio_generator.pyc
"""

import os
import re
import sys
import importlib.util
import unicodedata

# Load base audio_generator.pyc
_pyc_path = None
for cand in [
    r"D:\HikariDub\pyc_dump\app\core\audio_generator.pyc",
    r"D:\Hikari_Dub\_internal\app\core\audio_generator.pyc",
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "pyc_dump", "app", "core", "audio_generator.pyc"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pyc_dump", "app", "core", "audio_generator.pyc"),
    os.path.join(os.path.dirname(__file__), "audio_generator.pyc"),
    r"D:\Hikari_Dub\pyc_dump\app\core\audio_generator.pyc",
]:
    if os.path.exists(cand):
        _pyc_path = cand
        break

if not _pyc_path:
    raise FileNotFoundError("Could not find base audio_generator.pyc")

_spec = importlib.util.spec_from_file_location("app.core.audio_generator", _pyc_path)
_base_mod = importlib.util.module_from_spec(_spec)
sys.modules["app.core.audio_generator"] = _base_mod
_spec.loader.exec_module(_base_mod)

for _attr in dir(_base_mod):
    if not _attr.startswith("__"):
        globals()[_attr] = getattr(_base_mod, _attr)

def _clean_tts_text(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    # Remove emojis
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F"
        "\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F"
        "\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251]+",
        flags=re.UNICODE
    )
    text = emoji_pattern.sub("", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) not in ("Cc", "Cf") or ch in ("\n", "\t", " "))
    text = re.sub(r"[ \t]+", " ", text).strip()
    return text

_orig_generate_audio_logic = getattr(_base_mod, "generate_audio_logic", None)

def generate_audio_logic_patched(*args, **kwargs):
    """
    Accepts arbitrary args:
    args: (srt_path, api_key, voice_model, status_cb, cancel_event, temp_files, workspace_dir, target_lang, max_speed)
    """
    import pysrt

    args_list = list(args)
    srt_path = args_list[0] if len(args_list) > 0 else kwargs.get("srt_path")

    if srt_path and os.path.exists(srt_path):
        try:
            subs = pysrt.open(srt_path, encoding="utf-8")
            changed = False
            for sub in subs:
                cleaned = _clean_tts_text(sub.text)
                if not any(unicodedata.category(c).startswith("L") for c in cleaned):
                    cleaned = "..."
                if cleaned != sub.text:
                    sub.text = cleaned
                    changed = True
            if changed:
                subs.save(srt_path, encoding="utf-8")
        except Exception as e:
            print(f"[audio_generator] Clean SRT warning: {e}")

    if _orig_generate_audio_logic:
        return _orig_generate_audio_logic(*args_list, **kwargs)

generate_audio_logic = generate_audio_logic_patched
_base_mod.generate_audio_logic = generate_audio_logic_patched
globals()["generate_audio_logic"] = generate_audio_logic_patched

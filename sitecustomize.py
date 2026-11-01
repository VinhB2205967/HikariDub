"""
Site-wide customization for Hikari Dub.
Automatically executed by Python on startup for both main process and child processes.
"""

import os
import sys

# 1. Configure cache paths
curr = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(os.path.join(curr, "_internal")):
    project_root = curr
elif os.path.basename(curr) == "_internal":
    project_root = os.path.dirname(curr)
else:
    project_root = os.environ.get("HIKARI_ROOT", r"D:\HikariDub" if os.path.exists(r"D:\HikariDub") else (r"D:\Hikari_Dub" if os.path.exists(r"D:\Hikari_Dub") else curr))

models_dir = os.path.join(project_root, "models")
hf_dir = os.path.join(models_dir, "whisper")
paddle_dir = os.path.join(models_dir, "paddleocr")
audio_sep_dir = os.path.join(models_dir, "audio-separator")

os.environ["HF_HOME"] = hf_dir
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# 2. Patch Numba JIT caching to prevent 'no locator available' in pyc-only environments
try:
    import numba.core.dispatcher as ncd
    _orig_enable_caching = ncd.Dispatcher.enable_caching
    def _safe_enable_caching(self):
        try:
            _orig_enable_caching(self)
        except Exception:
            self._cache = None
    ncd.Dispatcher.enable_caching = _safe_enable_caching
except Exception:
    pass


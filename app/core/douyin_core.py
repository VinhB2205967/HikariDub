"""
Douyin Core Module - Hikari Dub Edition
Wraps and patches douyin_core.pyc to ensure all downloaded videos are named with 'HikariDub_' prefix instead of 'SirVietsub_'.
"""

import os
import sys
import glob
import importlib.util

# Load base douyin_core.pyc
_pyc_path = None
for cand in [
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "pyc_dump", "app", "core", "douyin_core.pyc"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pyc_dump", "app", "core", "douyin_core.pyc"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_internal", "app", "core", "douyin_core.pyc"),
    os.path.join(os.path.dirname(__file__), "douyin_core.pyc"),
    r"D:\HikariDub\pyc_dump\app\core\douyin_core.pyc",
    r"D:\HikariDub\app\core\douyin_core.pyc",
    r"D:\Hikari_Dub\pyc_dump\app\core\douyin_core.pyc",
]:
    if os.path.exists(cand):
        _pyc_path = cand
        break

if not _pyc_path:
    raise FileNotFoundError("Could not find base douyin_core.pyc")

_spec = importlib.util.spec_from_file_location("app.core.douyin_core", _pyc_path)
_base_mod = importlib.util.module_from_spec(_spec)
sys.modules["app.core.douyin_core"] = _base_mod
_spec.loader.exec_module(_base_mod)

for _attr in dir(_base_mod):
    if not _attr.startswith("__"):
        globals()[_attr] = getattr(_base_mod, _attr)

# 1. Patch os.path.join in douyin_core to use 'HikariDub_' prefix
_orig_join = _base_mod.os.path.join
def _hikari_join(*args):
    new_args = []
    for a in args:
        if isinstance(a, str):
            a = a.replace("SirVietsub_", "HikariDub_").replace("sirvietsub_", "hikaridub_")
        new_args.append(a)
    return _orig_join(*new_args)

_base_mod.os.path.join = _hikari_join
globals()["os"].path.join = _hikari_join

# 2. Patch os.rename and os.replace in douyin_core
_orig_rename = getattr(_base_mod.os, "rename", None)
if _orig_rename:
    def _hikari_rename(src, dst):
        if isinstance(dst, str):
            dst = dst.replace("SirVietsub_", "HikariDub_").replace("sirvietsub_", "hikaridub_")
        return _orig_rename(src, dst)
    _base_mod.os.rename = _hikari_rename
    globals()["os"].rename = _hikari_rename

_orig_replace = getattr(_base_mod.os, "replace", None)
if _orig_replace:
    def _hikari_replace(src, dst):
        if isinstance(dst, str):
            dst = dst.replace("SirVietsub_", "HikariDub_").replace("sirvietsub_", "hikaridub_")
        return _orig_replace(src, dst)
    _base_mod.os.replace = _hikari_replace
    globals()["os"].replace = _hikari_replace

# 3. Patch yt_dlp.YoutubeDL outtmpl
if hasattr(_base_mod, "yt_dlp") and hasattr(_base_mod.yt_dlp, "YoutubeDL"):
    _orig_ydl_init = _base_mod.yt_dlp.YoutubeDL.__init__
    def _hikari_ydl_init(self, params=None, *args, **kwargs):
        if params and "outtmpl" in params:
            if isinstance(params["outtmpl"], str):
                params["outtmpl"] = params["outtmpl"].replace("SirVietsub_", "HikariDub_").replace("sirvietsub_", "hikaridub_")
            elif isinstance(params["outtmpl"], dict):
                for k, v in params["outtmpl"].items():
                    if isinstance(v, str):
                        params["outtmpl"][k] = v.replace("SirVietsub_", "HikariDub_").replace("sirvietsub_", "hikaridub_")
        return _orig_ydl_init(self, params, *args, **kwargs)
    _base_mod.yt_dlp.YoutubeDL.__init__ = _hikari_ydl_init

# 4. Wrap DouyinDownloadWorker to guarantee zero SirVietsub prefix
_BaseDownloadWorker = _base_mod.DouyinDownloadWorker

class HikariDownloadWorker(_BaseDownloadWorker):
    def __init__(self, videos, output_dir, parent=None, options=None):
        super().__init__(videos, output_dir, parent, options)
        self.output_dir = output_dir

    def run(self):
        # Run base downloader logic
        super().run()
        
        # Post-download verification: rename any residual SirVietsub_ files in output_dir
        try:
            if os.path.exists(self.output_dir):
                for fname in os.listdir(self.output_dir):
                    if fname.startswith("SirVietsub_") or fname.startswith("sirvietsub_"):
                        new_fname = fname.replace("SirVietsub_", "HikariDub_").replace("sirvietsub_", "hikaridub_")
                        old_path = os.path.join(self.output_dir, fname)
                        new_path = os.path.join(self.output_dir, new_fname)
                        try:
                            if not os.path.exists(new_path):
                                os.rename(old_path, new_path)
                            else:
                                os.replace(old_path, new_path)
                        except Exception:
                            pass
        except Exception:
            pass

_base_mod.DouyinDownloadWorker = HikariDownloadWorker
globals()["DouyinDownloadWorker"] = HikariDownloadWorker


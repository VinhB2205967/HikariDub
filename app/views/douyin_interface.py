"""
Douyin Interface Module - Hikari Dub Edition
Wraps and patches DouyinInterface to ensure all downloaded videos are named with 'HikariDub_' prefix instead of 'SirVietsub_'.
"""

import os
import sys
import importlib.util

# Find base douyin_interface.pyc
_pyc_path = None
for cand in [
    os.path.join(os.path.dirname(__file__), "douyin_interface.pyc"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "pyc_dump", "app", "views", "douyin_interface.pyc"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pyc_dump", "app", "views", "douyin_interface.pyc"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_internal", "app", "views", "douyin_interface.pyc"),
    r"D:\HikariDub\pyc_dump\app\views\douyin_interface.pyc",
    r"D:\Hikari_Dub\pyc_dump\app\views\douyin_interface.pyc"
]:
    if os.path.exists(cand):
        _pyc_path = cand
        break

if not _pyc_path:
    raise FileNotFoundError("Could not find base douyin_interface.pyc")

_spec = importlib.util.spec_from_file_location("app.views.douyin_interface_base", _pyc_path)
_base_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base_mod)

for _attr in dir(_base_mod):
    if not _attr.startswith('__'):
        globals()[_attr] = getattr(_base_mod, _attr)

DouyinInterface = _base_mod.DouyinInterface

# Patch on_download_finished to normalize downloaded file names
_orig_on_download_finished = DouyinInterface.on_download_finished

def _patched_on_download_finished(self, fpath):
    if fpath and isinstance(fpath, str):
        if "SirVietsub_" in fpath or "sirvietsub_" in fpath:
            clean_fpath = fpath.replace("SirVietsub_", "HikariDub_").replace("sirvietsub_", "hikaridub_")
            if os.path.exists(fpath) and not os.path.exists(clean_fpath):
                try:
                    os.rename(fpath, clean_fpath)
                    fpath = clean_fpath
                except Exception:
                    pass
            elif os.path.exists(clean_fpath):
                fpath = clean_fpath
    
    # Also check save_dir for any residual SirVietsub_ files
    try:
        save_dir = self.dir_input.text().strip()
        if os.path.exists(save_dir):
            for item in os.listdir(save_dir):
                if item.startswith("SirVietsub_") or item.startswith("sirvietsub_"):
                    old_item_path = os.path.join(save_dir, item)
                    new_item_name = item.replace("SirVietsub_", "HikariDub_").replace("sirvietsub_", "hikaridub_")
                    new_item_path = os.path.join(save_dir, new_item_name)
                    try:
                        if not os.path.exists(new_item_path):
                            os.rename(old_item_path, new_item_path)
                        else:
                            os.replace(old_item_path, new_item_path)
                    except Exception:
                        pass
    except Exception:
        pass

    return _orig_on_download_finished(self, fpath)

DouyinInterface.on_download_finished = _patched_on_download_finished


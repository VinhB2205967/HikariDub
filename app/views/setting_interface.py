"""
Setting Interface Module - Free Forever & Local-First Edition
Wraps SettingInterface and patches ModelDownloaderWorker to ensure
all child download subprocesses run with full PYTHONPATH and environment access.
"""

import os
import sys
import importlib.util

# Find base setting_interface.pyc
_pyc_path = None
for cand in [
    os.path.join(os.path.dirname(__file__), "setting_interface.pyc"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "pyc_dump", "app", "views", "setting_interface.pyc"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pyc_dump", "app", "views", "setting_interface.pyc"),
    r"D:\HikariDub\pyc_dump\app\views\setting_interface.pyc",
    r"D:\Hikari_Dub\pyc_dump\app\views\setting_interface.pyc",
]:
    if os.path.exists(cand):
        _pyc_path = cand
        break

if not _pyc_path:
    raise FileNotFoundError("Could not find base setting_interface.pyc")

_spec = importlib.util.spec_from_file_location("app.views.setting_interface_base", _pyc_path)
_base_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base_mod)

# Export all symbols from base module
for attr in dir(_base_mod):
    if not attr.startswith('__'):
        globals()[attr] = getattr(_base_mod, attr)

# 1. Hide the account page and show neutral product information.
_original_init_widget = _base_mod.SettingInterface._initWidget

def _init_widget_without_account(self):
    _original_init_widget(self)

    pivot = getattr(self, "pivot", None)
    if pivot is not None:
        pivot.removeWidget("account")

    stacked_widget = getattr(self, "stackedWidget", None)
    account_page = getattr(self, "page_account", None)
    if stacked_widget is not None and account_page is not None:
        stacked_widget.removeWidget(account_page)

_base_mod.SettingInterface._initWidget = _init_widget_without_account

def _setLicenseInfo_patched(self, status="premium", msg="Hikari Tsukimi — AI Dubbing Studio"):
    if hasattr(self, 'lbl_license_status'):
        self.lbl_license_status.setText("✦ HIKARI TSUKIMI • AI Dubbing Studio")
        self.lbl_license_status.setStyleSheet("color: #34D399; font-weight: bold; font-size: 13px; letter-spacing: 0.5px;")

_base_mod.SettingInterface.setLicenseInfo = _setLicenseInfo_patched

# 2. Patch ModelDownloaderWorker._run_script to ensure child processes inherit PYTHONPATH & PATH
def _patched_run_script(self, python_exe, script):
    import subprocess
    import sys
    import os

    env = os.environ.copy()

    # Determine project root and _internal directory
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(curr_dir))
    if not os.path.exists(os.path.join(project_root, "_internal")):
        project_root = os.environ.get("HIKARI_ROOT", r"D:\HikariDub" if os.path.exists(r"D:\HikariDub") else (r"D:\Hikari_Dub" if os.path.exists(r"D:\Hikari_Dub") else curr_dir))
    internal_dir = os.path.join(project_root, "_internal")

    # Inject project root and _internal into PYTHONPATH
    py_paths = [project_root, internal_dir]
    if env.get("PYTHONPATH"):
        py_paths.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(py_paths)

    # Inject ffmpeg and DLL directories into PATH
    ffmpeg_dir = os.path.join(internal_dir, "ffmpeg")
    torch_lib = os.path.join(internal_dir, "torch", "lib")
    cuda_dirs = [
        os.path.join(internal_dir, "nvidia", "cublas", "bin"),
        os.path.join(internal_dir, "nvidia", "cudnn", "bin"),
        torch_lib,
        ffmpeg_dir,
    ]
    extra_paths = [p for p in cuda_dirs if os.path.exists(p)]
    if os.path.exists(ffmpeg_dir):
        env["BUNDLE_FFMPEG_DIR"] = ffmpeg_dir

    if extra_paths:
        env["PATH"] = os.pathsep.join(extra_paths) + os.pathsep + env.get("PATH", "")

    # Force UTF-8 encoding for child process streams
    env["PYTHONIOENCODING"] = "utf-8"

    # Inject cache directories
    models_dir = os.path.join(project_root, "models")
    env["HF_HOME"] = os.path.join(models_dir, "whisper")
    env["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
    env["HF_HUB_DISABLE_TELEMETRY"] = "1"
    env["KMP_DUPLICATE_LIB_OK"] = "TRUE"

    # Prepend numba safe caching to child script to prevent 'no locator available'
    numba_preamble = (
        "try:\n"
        "    import numba.core.dispatcher as ncd\n"
        "    _orig_ec = ncd.Dispatcher.enable_caching\n"
        "    def _safe_ec(self):\n"
        "        try: _orig_ec(self)\n"
        "        except Exception: self._cache = None\n"
        "    ncd.Dispatcher.enable_caching = _safe_ec\n"
        "except Exception: pass\n"
    )
    script = numba_preamble + script

    creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
    process = subprocess.Popen(
        [python_exe, "-c", script],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        creationflags=creationflags
    )
    for line in process.stdout:
        if line:
            self.progress.emit(line.strip())
    process.wait()

_base_mod.ModelDownloaderWorker._run_script = _patched_run_script

# Re-assign patched classes to globals
SettingInterface = _base_mod.SettingInterface
ModelDownloaderWorker = _base_mod.ModelDownloaderWorker

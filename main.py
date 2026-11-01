"""
Hikari Tsukimi v3.0 — AI Dubbing Studio
Free Forever & Local-First Edition (Refactored for Permanent Offline & Free Usage)
"""

import sys
import os
import traceback
import subprocess
import multiprocessing

# Add project root and _internal to sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
INTERNAL_DIR = os.path.join(PROJECT_ROOT, "_internal")

if INTERNAL_DIR not in sys.path:
    sys.path.insert(0, INTERNAL_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Set PYTHONPATH in os.environ for all child processes spawned by the app
current_ppath = os.environ.get("PYTHONPATH", "")
os.environ["PYTHONPATH"] = os.pathsep.join(filter(None, [PROJECT_ROOT, INTERNAL_DIR, current_ppath]))
os.environ["PYTHONIOENCODING"] = "utf-8"

# Configure cache directories so Faster-Whisper, PaddleOCR and Audio Separator find models locally
models_dir = os.path.join(PROJECT_ROOT, "models")
hf_dir = os.path.join(models_dir, "whisper")
paddle_dir = os.path.join(models_dir, "paddleocr")
audio_sep_dir = os.path.join(models_dir, "audio-separator")

os.environ["HF_HOME"] = hf_dir
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Patch Numba JIT caching to prevent 'no locator available' in pyc-only environments
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

# Add Qt DLL directory on Windows
if os.name == 'nt':
    qt_bin = os.path.join(INTERNAL_DIR, "PyQt6", "Qt6", "bin")
    if os.path.exists(qt_bin):
        try:
            os.add_dll_directory(qt_bin)
        except Exception:
            pass
            
    # Add CUDA / Torch DLL directories if present
    extra_dll_dirs = [
        os.path.join(INTERNAL_DIR, "nvidia", "cublas", "bin"),
        os.path.join(INTERNAL_DIR, "nvidia", "cudnn", "bin"),
        os.path.join(INTERNAL_DIR, "torch", "lib"),
    ]
    for sub in extra_dll_dirs:
        if os.path.exists(sub):
            try:
                os.add_dll_directory(sub)
            except Exception:
                pass

    # Add ffmpeg and CUDA dll directories to PATH and set BUNDLE_FFMPEG_DIR
    ffmpeg_dir = os.path.join(INTERNAL_DIR, "ffmpeg")
    if os.path.exists(ffmpeg_dir):
        os.environ["BUNDLE_FFMPEG_DIR"] = ffmpeg_dir
    
    path_dirs = [p for p in [ffmpeg_dir] + extra_dll_dirs if os.path.exists(p)]
    os.environ["PATH"] = os.pathsep.join(path_dirs) + os.pathsep + os.environ.get("PATH", "")

# Load PyArmor runtime if present
try:
    import pyarmor_runtime_000000
except Exception:
    pass

APP_VERSION = "3.0"
APP_NAME = "Hikari Tsukimi"

class DummyStream:
    def write(self, *args, **kwargs):
        pass
    def flush(self, *args, **kwargs):
        pass
    def isatty(self):
        return False

# Ensure std streams exist
if getattr(sys, 'stdout', None) is None:
    sys.stdout = DummyStream()
if getattr(sys, 'stderr', None) is None:
    sys.stderr = DummyStream()
if getattr(sys, '__stdout__', None) is None:
    sys.__stdout__ = DummyStream()
if getattr(sys, '__stderr__', None) is None:
    sys.__stderr__ = DummyStream()

# Hide child console windows on Windows & ensure subprocesses inherit PYTHONPATH
if os.name == 'nt':
    original_popen = subprocess.Popen
    class PatchedPopen(original_popen):
        def __init__(self, *args, **kwargs):
            if 'creationflags' not in kwargs:
                kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW
            
            # If a custom env dict is provided, ensure PYTHONPATH and BUNDLE_FFMPEG_DIR are present
            if 'env' in kwargs and kwargs['env'] is not None:
                custom_env = kwargs['env'].copy()
                curr_py = custom_env.get('PYTHONPATH', '')
                custom_env['PYTHONPATH'] = os.pathsep.join(filter(None, [PROJECT_ROOT, INTERNAL_DIR, curr_py]))
                if ffmpeg_dir and os.path.exists(ffmpeg_dir):
                    custom_env['BUNDLE_FFMPEG_DIR'] = ffmpeg_dir
                    custom_env['PATH'] = ffmpeg_dir + os.pathsep + custom_env.get('PATH', '')
                custom_env['PYTHONIOENCODING'] = 'utf-8'
                kwargs['env'] = custom_env

            super().__init__(*args, **kwargs)
    subprocess.Popen = PatchedPopen

def get_icon_path() -> str:
    candidates = [
        os.path.join(PROJECT_ROOT, "icon.ico"),
        os.path.join(INTERNAL_DIR, "icon.ico"),
        os.path.join(PROJECT_ROOT, "_internal", "icon.ico"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return os.path.join(PROJECT_ROOT, "icon.ico")

def get_png_icon_path() -> str:
    candidates = [
        os.path.join(PROJECT_ROOT, "icon.png"),
        os.path.join(INTERNAL_DIR, "icon.png"),
        os.path.join(PROJECT_ROOT, "_internal", "icon.png"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return os.path.join(PROJECT_ROOT, "icon.png")

def force_native_taskbar_icon(widget, icon_path):
    if not os.path.exists(icon_path):
        return
    try:
        import ctypes
        hwnd = int(widget.winId())
        u32 = ctypes.windll.user32

        # Configure 64-bit safe prototypes
        u32.LoadImageW.restype = ctypes.c_void_p
        u32.LoadImageW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_uint, ctypes.c_int, ctypes.c_int, ctypes.c_uint]
        u32.SendMessageW.restype = ctypes.c_void_p
        u32.SendMessageW.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p, ctypes.c_void_p]

        IMAGE_ICON = 1
        LR_LOADFROMFILE = 0x0010

        # Load multiple sizes for various Windows DPI scaling settings
        hicon_16 = u32.LoadImageW(None, icon_path, IMAGE_ICON, 16, 16, LR_LOADFROMFILE)
        hicon_32 = u32.LoadImageW(None, icon_path, IMAGE_ICON, 32, 32, LR_LOADFROMFILE)
        hicon_48 = u32.LoadImageW(None, icon_path, IMAGE_ICON, 48, 48, LR_LOADFROMFILE)
        hicon_256 = u32.LoadImageW(None, icon_path, IMAGE_ICON, 256, 256, LR_LOADFROMFILE)

        hicon_big = hicon_48 or hicon_32 or hicon_256
        hicon_small = hicon_16 or hicon_32

        WM_SETICON = 0x0080
        ICON_SMALL = 0
        ICON_BIG = 1

        if hicon_small:
            u32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon_small)
        if hicon_big:
            u32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon_big)

        # Set Class Icon for Windows Taskbar & Shell
        GCLP_HICON = -14
        GCLP_HICONSM = -34
        SetClassLong = getattr(u32, 'SetClassLongPtrW', getattr(u32, 'SetClassLongW', None))
        if SetClassLong:
            SetClassLong.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_void_p]
            SetClassLong.restype = ctypes.c_void_p
            if hicon_big:
                SetClassLong(hwnd, GCLP_HICON, hicon_big)
            if hicon_small:
                SetClassLong(hwnd, GCLP_HICONSM, hicon_small)
    except Exception as e:
        print("Lỗi force_native_taskbar_icon:", e)

def show_splash_and_check_license(app):
    from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QApplication, QFrame
    from PyQt6.QtCore import Qt
    from PyQt6.QtGui import QIcon, QPixmap
    from app.common import security

    splash = QWidget()
    splash.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
    splash.setFixedSize(540, 160)
    splash.setObjectName("splash")
    splash.setStyleSheet("""
        #splash {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #070714, stop:0.5 #0A0A1E, stop:1 #0D0B22);
            border: 1px solid #00D4FF;
            border-radius: 14px;
        }
    """)

    main_layout = QHBoxLayout(splash)
    main_layout.setContentsMargins(28, 22, 28, 22)
    main_layout.setSpacing(20)

    # Icon with glow effect container
    icon_container = QWidget()
    icon_container.setFixedSize(72, 72)
    icon_container.setStyleSheet("""
        background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00D4FF22, stop:1 #A855F722);
        border: 1px solid #00D4FF55;
        border-radius: 12px;
    """)
    icon_inner = QHBoxLayout(icon_container)
    icon_inner.setContentsMargins(4, 4, 4, 4)

    icon_label = QLabel()
    png_path = get_png_icon_path()
    if os.path.exists(png_path):
        icon_pixmap = QPixmap(png_path).scaled(60, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        icon_label.setPixmap(icon_pixmap)
    else:
        # Fallback: Japanese kanji for "light" (hikari)
        icon_label.setText("光")
        icon_label.setStyleSheet("color: #00D4FF; font-size: 36px; font-weight: bold;")
    icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    icon_inner.addWidget(icon_label)
    main_layout.addWidget(icon_container)

    # Vertical separator
    sep = QFrame()
    sep.setFrameShape(QFrame.Shape.VLine)
    sep.setFixedWidth(1)
    sep.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:0,y2:1,stop:0 transparent,stop:0.3 #00D4FF,stop:0.7 #A855F7,stop:1 transparent); border: none;")
    main_layout.addWidget(sep)

    text_layout = QVBoxLayout()
    text_layout.setSpacing(6)

    # App name with futuristic styling
    title_label = QLabel("HIKARI TSUKIMI")
    title_label.setStyleSheet("""
        color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00D4FF, stop:1 #A855F7);
        font-size: 26px;
        font-weight: 800;
        font-family: 'Segoe UI Variable Display', 'Segoe UI', Arial;
        letter-spacing: 3px;
    """)
    text_layout.addWidget(title_label)

    # Subtitle — Japanese + Vietnamese bilingual
    ver_label = QLabel(f"v{APP_VERSION}  •  AI Dubbing Studio  •  月見の光")
    ver_label.setStyleSheet("""
        color: #A855F7;
        font-size: 12px;
        font-weight: 600;
        font-family: 'Segoe UI', Arial;
        letter-spacing: 1px;
    """)
    text_layout.addWidget(ver_label)

    # Thin neon separator line
    line = QFrame()
    line.setFrameShape(QFrame.Shape.HLine)
    line.setFixedHeight(1)
    line.setStyleSheet("background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #00D4FF66,stop:0.5 #A855F766,stop:1 transparent); border: none;")
    text_layout.addWidget(line)

    status_label = QLabel("⚡ Đang khởi động hệ thống AI ngoại tuyến...")
    status_label.setStyleSheet("""
        color: #64748B;
        font-size: 11px;
        font-style: italic;
        font-family: 'Segoe UI', Arial;
    """)
    text_layout.addWidget(status_label)

    # Product status badge
    status_badge = QLabel("✦ HIKARI TSUKIMI • AI Dubbing Studio")
    status_badge.setStyleSheet("""
        color: #10B981;
        font-size: 10px;
        font-family: 'Segoe UI', Arial;
        letter-spacing: 0.5px;
    """)
    text_layout.addWidget(status_badge)

    main_layout.addLayout(text_layout)

    screen = QApplication.primaryScreen().availableGeometry()
    splash.move((screen.width() - splash.width()) // 2, (screen.height() - splash.height()) // 2)
    splash.show()
    app.processEvents()

    hwid = security.get_hwid()
    status, msg = security.check_license_online(hwid, APP_VERSION)
    return splash, status, msg

if __name__ == '__main__':
    multiprocessing.freeze_support()

    # CLI subcommand handlers
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == '--run-audio-sep':
            # Run audio separation subcommand
            from audio_separator.separator import Separator
            input_file = sys.argv[2]
            out_dir = sys.argv[3]
            model_name = sys.argv[4]
            use_cuda = sys.argv[5].lower() == 'true'
            segment_size = int(sys.argv[6])
            overlap = int(sys.argv[7])
            
            from app.common.config_manager import get_audio_sep_cache_dir
            cache_dir = get_audio_sep_cache_dir()
            if not use_cuda:
                os.environ['CUDA_VISIBLE_DEVICES'] = ''
                
            separator = Separator(
                output_dir=out_dir,
                output_format='WAV',
                model_file_dir=cache_dir,
                segment_size=segment_size,
                batch_size=1,
                overlap=0.25,
            )
            separator.load_model(model_name)
            separator.separate(input_file)
            sys.exit(0)

        elif cmd == '--run-script' and len(sys.argv) > 2:
            import importlib.util
            script_path = sys.argv[2]
            sys.argv = [sys.argv[0]] + sys.argv[3:]
            spec = importlib.util.spec_from_file_location('__main__', script_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules['__main__'] = module
            spec.loader.exec_module(module)
            sys.exit(0)

        elif cmd == '--run-module' and len(sys.argv) > 2:
            import runpy
            module_name = sys.argv[2]
            sys.argv = [sys.argv[0]] + sys.argv[3:]
            runpy.run_module(module_name, run_name='__main__', alter_sys=True)
            sys.exit(0)

        elif cmd == '-c' and len(sys.argv) > 2:
            code_str = sys.argv[2]
            sys.argv = [sys.argv[0]] + sys.argv[3:]
            exec(code_str)
            sys.exit(0)

    # Set Windows Process App ID
    if os.name == 'nt':
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(f"HikariDub.App.{APP_VERSION}")
        except Exception:
            pass

    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt, QSize, QTimer
    from PyQt6.QtGui import QIcon, QColor, QPalette
    from qfluentwidgets import (
        setTheme, Theme, setThemeColor, qconfig,
        FluentWindow, NavigationItemPosition, SplashScreen, FluentIcon as FIF,
        InfoBar, InfoBarPosition, MessageBox
    )

    os.environ['QT_STYLE_OVERRIDE'] = 'Fusion'

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    qconfig.set(qconfig.themeMode, Theme.DARK, save=False)
    setTheme(Theme.DARK)

    fixed_color = QColor('#22D3EE')
    qconfig.set(qconfig.themeColor, fixed_color, save=False)
    setThemeColor(fixed_color)

    # Deep midnight creative studio palette — Hikari Dub v3.0
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor('#0B0D12'))
    dark_palette.setColor(QPalette.ColorRole.WindowText, QColor('#F1F5F9'))
    dark_palette.setColor(QPalette.ColorRole.Base, QColor('#080A0F'))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor('#121620'))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor('#10131B'))
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor('#22D3EE'))
    dark_palette.setColor(QPalette.ColorRole.Text, QColor('#F1F5F9'))
    dark_palette.setColor(QPalette.ColorRole.Button, QColor('#191F2B'))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor('#F1F5F9'))
    dark_palette.setColor(QPalette.ColorRole.BrightText, QColor('#22D3EE'))
    dark_palette.setColor(QPalette.ColorRole.Link, QColor('#22D3EE'))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor('#22D3EE'))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor('#0B0D12'))
    app.setPalette(dark_palette)
    setTheme(Theme.DARK)

    # Hikari Dub v3.0 Design System Stylesheet
    app.setStyleSheet("""
        QWidget {
            font-family: 'Segoe UI Variable', 'Segoe UI', 'Helvetica Neue', sans-serif;
            color: #F1F5F9;
        }
        
        /* Navigation Sidebar Styling */
        NavigationPanel, NavigationInterface {
            background-color: #10131B;
            border-right: 1px solid #293244;
        }
        NavigationTreeItem, NavigationToolButton {
            background-color: transparent;
            color: #94A3B8;
            border-radius: 6px;
            font-weight: 500;
        }
        NavigationTreeItem:hover, NavigationToolButton:hover {
            background-color: #191F2B;
            color: #F1F5F9;
        }
        
        /* Input & Controls */
        LineEdit, TextEdit {
            background-color: #080A0F;
            color: #F1F5F9;
            border: 1px solid #293244;
            border-radius: 6px;
            padding: 5px 10px;
            selection-background-color: #22D3EE;
            selection-color: #0B0D12;
        }
        LineEdit:focus, TextEdit:focus {
            border: 1px solid #22D3EE;
        }
        
        /* Buttons */
        PushButton {
            background-color: #191F2B;
            color: #F1F5F9;
            border: 1px solid #293244;
            border-radius: 6px;
            font-weight: 500;
            padding: 6px 12px;
        }
        PushButton:hover {
            background-color: #222A39;
            border: 1px solid #22D3EE;
            color: #22D3EE;
        }
        PushButton:pressed {
            background-color: #121620;
        }
        
        PrimaryPushButton {
            background-color: #22D3EE;
            color: #0B0D12;
            font-weight: 700;
            border: 1px solid #06B6D4;
            border-radius: 6px;
            padding: 7px 16px;
        }
        PrimaryPushButton:hover {
            background-color: #38BDF8;
            border: 1px solid #22D3EE;
        }
        PrimaryPushButton:pressed {
            background-color: #0891B2;
        }
        PrimaryPushButton:disabled {
            background-color: #191F2B;
            color: #475569;
            border: 1px solid #293244;
        }
        
        /* Progress Bar */
        ProgressBar {
            background-color: #121620;
            border: 1px solid #293244;
            border-radius: 4px;
            text-align: center;
            color: #22D3EE;
            font-weight: bold;
        }
        ProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #22D3EE, stop:1 #8B5CF6);
            border-radius: 3px;
        }
        
        /* Smooth ScrollBars */
        QScrollBar:vertical {
            background: #080A0F;
            width: 6px;
            border-radius: 3px;
            margin: 0;
        }
        QScrollBar::handle:vertical {
            background: #293244;
            border-radius: 3px;
            min-height: 24px;
        }
        QScrollBar::handle:vertical:hover {
            background: #22D3EE;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        
        QScrollBar:horizontal {
            background: #080A0F;
            height: 6px;
            border-radius: 3px;
            margin: 0;
        }
        QScrollBar::handle:horizontal {
            background: #293244;
            border-radius: 3px;
            min-width: 24px;
        }
        QScrollBar::handle:horizontal:hover {
            background: #22D3EE;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }
        
        /* Tooltip */
        QToolTip {
            background: #10131B;
            color: #22D3EE;
            border: 1px solid #22D3EE;
            border-radius: 6px;
            padding: 5px 9px;
            font-size: 12px;
        }
        
        QStatusBar {
            background: #0B0D12;
            color: #94A3B8;
            border-top: 1px solid #293244;
        }
    """)

    # Load custom fonts
    try:
        from app.common.font_manager import load_custom_fonts
        load_custom_fonts()
    except Exception as e:
        print("Lỗi nạp font:", e)

    # Patch StyleDialog Watermark preview text to match Hikari Tsukimi branding
    try:
        import app.views.style_dialog as sd
        _orig_wm_init = sd.PreviewWidgetWM.__init__
        def _wm_init_patched(self, dialog, parent=None):
            _orig_wm_init(self, dialog, parent)
            self.text = "PRODUCED BY HIKARI TSUKIMI"
        sd.PreviewWidgetWM.__init__ = _wm_init_patched
    except Exception as e:
        print("Lỗi nạp StyleDialog patch:", e)

    ico_path = get_icon_path()
    png_icon = get_png_icon_path()
    if os.path.exists(ico_path):
        app.setWindowIcon(QIcon(ico_path))
    elif os.path.exists(png_icon):
        app.setWindowIcon(QIcon(png_icon))

    splash, license_status, license_msg = show_splash_and_check_license(app)

    from app.core import security as core_sec
    core_sec.CURRENT_LICENSE_STATUS = license_status

    from app.views.home_interface import HomeInterface
    from app.views.library_interface import LibraryInterface
    from app.views.highlight_interface import HighlightInterface
    from app.views.setting_interface import SettingInterface
    from app.views.report_interface import ReportInterface
    from app.views.douyin_interface import DouyinInterface
    from app.views.tts_interface import TTSInterface
    from app.views.video_splitter_interface import VideoSplitterInterface
    from app.views.video_merger_interface import VideoMergerInterface
    from app.views.dictionary_interface import DictionaryInterface

    class MainWindow(FluentWindow):
        def __init__(self, lic_status, lic_msg):
            super().__init__()
            self.license_status = lic_status
            self.license_msg = lic_msg
            self.initWindow()

            self.homeInterface = HomeInterface(self)
            self.homeInterface.license_status = lic_status

            self.libraryInterface = LibraryInterface(self)
            self.highlightInterface = HighlightInterface(self)
            self.settingInterface = SettingInterface(self)
            self.settingInterface.setLicenseInfo(lic_status, lic_msg)

            self.reportInterface = ReportInterface(self)
            self.douyinInterface = DouyinInterface(self)
            self.ttsInterface = TTSInterface(self)
            self.splitterInterface = VideoSplitterInterface(self)
            self.mergerInterface = VideoMergerInterface(self)
            self.dictInterface = DictionaryInterface(self)

            self.initNavigation()
            self.splashScreen.finish()

            QTimer.singleShot(1500, self.show_ready_notification)

        def show_ready_notification(self):
            InfoBar.success(
                title='✦ HIKARI TSUKIMI',
                content='Ứng dụng đã sẵn sàng.',
                parent=self,
                position=InfoBarPosition.TOP,
                duration=6000
            )

        def initNavigation(self):
            # Professional Line Navigation Items
            self.addSubInterface(self.homeInterface, FIF.HOME, 'Bảng Điều Khiển')
            self.addSubInterface(self.libraryInterface, FIF.VIDEO, 'Dự Án Video')
            self.addSubInterface(self.highlightInterface, FIF.FOLDER, 'Cắt Highlight')
            self.addSubInterface(self.splitterInterface, FIF.CUT, 'Chia Tập Video')
            self.addSubInterface(self.mergerInterface, FIF.MOVIE, 'Ghép Nối Video')
            self.addSubInterface(self.douyinInterface, FIF.DOWNLOAD, 'Tải Video Mạng')
            self.addSubInterface(self.ttsInterface, FIF.MICROPHONE, 'Giọng Đọc AI')
            self.addSubInterface(self.dictInterface, FIF.BOOK_SHELF, 'Từ Điển Phát Âm')
            self.addSubInterface(self.reportInterface, FIF.FEEDBACK, 'Báo Lỗi / Hỗ Trợ', NavigationItemPosition.BOTTOM)
            self.addSubInterface(self.settingInterface, FIF.SETTING, 'Cài Đặt Hệ Thống', NavigationItemPosition.BOTTOM)

            # Compact navigation width for elegant modern aesthetic
            if hasattr(self.navigationInterface, 'panel'):
                try:
                    self.navigationInterface.panel.setExpandWidth(220)
                except Exception:
                    pass

            # Style navigation indicator with electric cyan accent
            try:
                ind = [c for c in self.navigationInterface.findChildren(object) if 'indicator' in c.metaObject().className().lower()]
                if ind:
                    ind[0].setIndicatorColor(QColor('#22D3EE'), QColor('#22D3EE'))
            except Exception:
                pass

            if hasattr(self.navigationInterface, 'setReturnButtonVisible'):
                self.navigationInterface.setReturnButtonVisible(False)
            if hasattr(self.navigationInterface, 'panel') and hasattr(self.navigationInterface.panel, 'setReturnButtonVisible'):
                self.navigationInterface.panel.setReturnButtonVisible(False)

        def initWindow(self):
            self.resize(1280, 780)
            icon_path = get_icon_path()
            png_path = get_png_icon_path()
            
            # Use multi-resolution .ico (16px to 256px) for native Windows window & taskbar icon
            main_icon = QIcon(icon_path) if os.path.exists(icon_path) else QIcon(png_path)
            self.setWindowIcon(main_icon)
            
            # Show Hikari Tsukimi logo in application TitleBar
            if hasattr(self, 'titleBar'):
                self.titleBar.setIcon(main_icon)
                if hasattr(self.titleBar, 'iconLabel'):
                    self.titleBar.iconLabel.show()
                    self.titleBar.iconLabel.setVisible(True)
                    self.titleBar.iconLabel.setFixedSize(22, 22)
                if hasattr(self.titleBar, 'titleLabel'):
                    self.titleBar.titleLabel.setStyleSheet("color: #22D3EE; font-weight: 700; font-size: 13px; letter-spacing: 0.5px;")

            if os.path.exists(icon_path):
                force_native_taskbar_icon(self, icon_path)
            self.setWindowTitle(f"Hikari Tsukimi v{APP_VERSION} — AI Dubbing Studio")
            
            desktop = QApplication.primaryScreen().availableGeometry()
            w, h = desktop.width(), desktop.height()
            self.move((w - self.width()) // 2, (h - self.height()) // 2)
            self.splashScreen = SplashScreen(self.windowIcon(), self)
            self.splashScreen.setIconSize(QSize(102, 102))
            self.splashScreen.raise_()

        def showEvent(self, event):
            super().showEvent(event)
            # Re-apply native icons once the HWND is fully shown & mapped by Windows DWM
            icon_path = get_icon_path()
            if os.path.exists(icon_path):
                force_native_taskbar_icon(self, icon_path)
                QTimer.singleShot(100, lambda: force_native_taskbar_icon(self, icon_path))
                QTimer.singleShot(300, lambda: force_native_taskbar_icon(self, icon_path))

        def closeEvent(self, event):
            super().closeEvent(event)

    w = MainWindow(license_status, license_msg)
    w.show()
    splash.close()
    sys.exit(app.exec())


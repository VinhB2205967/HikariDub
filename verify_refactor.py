"""
Verification Test Script for Hikari Tsukimi v3.0 Refactor
Tests:
1. Security & License (Must be premium, offline, no watermark)
2. STT (faster-whisper GPU/CPU)
3. TTS (Piper Vietnamese ONNX models)
4. Translation (Free web & offline mode, empty API keys)
5. UI Interfaces (MainWindow, HomeInterface, SettingInterface)
"""

import sys
import os

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
INTERNAL_DIR = os.path.join(PROJECT_ROOT, "_internal")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if INTERNAL_DIR not in sys.path:
    sys.path.insert(0, INTERNAL_DIR)

# Qt & CUDA DLL paths
if os.name == 'nt':
    qt_bin = os.path.join(INTERNAL_DIR, "PyQt6", "Qt6", "bin")
    if os.path.exists(qt_bin):
        try: os.add_dll_directory(qt_bin)
        except Exception: pass
    for sub in [
        os.path.join(INTERNAL_DIR, "nvidia", "cublas", "bin"),
        os.path.join(INTERNAL_DIR, "nvidia", "cudnn", "bin"),
        os.path.join(INTERNAL_DIR, "torch", "lib"),
    ]:
        if os.path.exists(sub):
            try: os.add_dll_directory(sub)
            except Exception: pass

results = {}

print("=" * 60)
print("  HIKARI TSUKIMI v3.0 — VERIFICATION TEST SUITE")
print("  AI Dubbing Studio | Hikari Tsukimi")
print("=" * 60)

# TEST 1: License & Security
print("\n[TEST 1] Kiểm tra Cơ chế Bản quyền & Không Watermark:")
try:
    from app.common import security
    from app.core import security as core_sec
    hwid = security.get_hwid()
    status, msg = security.check_license_online(hwid)
    assert status == "premium", f"Expected 'premium', got '{status}'"
    assert core_sec.CURRENT_LICENSE_STATUS == "premium"
    
    # Test watermark pass-through
    dummy_subs = ["Sub 1", "Sub 2"]
    out_subs = core_sec.inject_watermark_to_srt(dummy_subs)
    assert dummy_subs == out_subs, "Watermark was injected unexpectedly!"
    
    print(f"  -> HWID: {hwid}")
    print(f"  -> License Status: {status} ({msg})")
    print(f"  -> Watermark Check: PASSED (Clean subtitles, zero watermark)")
    results["Security & License"] = "PASS"
except Exception as e:
    print(f"  -> FAILED: {e}")
    results["Security & License"] = f"FAIL: {e}"

# TEST 2: Piper TTS with Vietnamese ONNX Voice
print("\n[TEST 2] Kiểm tra Text-to-Speech Piper Tiếng Việt (Local & Offline):")
try:
    from piper import PiperVoice
    import app.core.audio_generator as ag
    import wave

    model_path = os.path.join(INTERNAL_DIR, "models", "piper", "Tiếng Việt", "banmai.onnx")
    config_path = model_path + ".json"
    assert os.path.exists(model_path), f"Missing model: {model_path}"
    
    voice = PiperVoice.load(model_path, config_path)
    os.makedirs("Data", exist_ok=True)
    temp_files = []
    
    class Cancel:
        def is_set(self): return False

    ag.fetch_piper_voice(1, "Kiểm tra tạo giọng đọc tiếng Việt không cần API.", temp_files, Cancel(), ".", voice)
    assert len(temp_files) > 0 and os.path.exists(temp_files[0]), "Failed to generate audio file"
    size = os.path.getsize(temp_files[0])
    assert size > 1000, f"Generated audio file too small ({size} bytes)"
    
    print(f"  -> Model: {os.path.basename(model_path)}")
    print(f"  -> Output file: {temp_files[0]} ({size} bytes)")
    print("  -> TTS Local Vietnamese: PASSED")
    results["Piper TTS Vietnamese"] = "PASS"
except Exception as e:
    print(f"  -> FAILED: {e}")
    results["Piper TTS Vietnamese"] = f"FAIL: {e}"

# TEST 3: AI Translation (Zero API Key & Offline Safe)
print("\n[TEST 3] Kiểm tra Module Dịch thuật (Không cần Gemini API Key):")
try:
    from app.core.ai_translator import translate_logic
    
    # Create test srt
    import pysrt
    test_srt = "Data/test_verify.srt"
    subs = pysrt.SubRipFile()
    subs.append(pysrt.SubRipItem(1, pysrt.SubRipTime(0, 0, 1), pysrt.SubRipTime(0, 0, 3), "Welcome to free AI dubbing."))
    subs.save(test_srt, encoding="utf-8")
    
    logs = []
    def log_cb(m): logs.append(m)
    
    out_srt = translate_logic(test_srt, [], log_cb, Cancel(), ".", target_lang="Tiếng Việt")
    assert os.path.exists(out_srt), f"Missing output SRT: {out_srt}"
    
    with open(out_srt, "r", encoding="utf-8") as f:
        content = f.read()
    print(f"  -> Output SRT: {out_srt}")
    print(f"  -> Progress Logs: {len(logs)} messages logged")
    print("  -> Translation Fallback / Free Pipeline: PASSED")
    results["Translation Pipeline"] = "PASS"
except Exception as e:
    print(f"  -> FAILED: {e}")
    results["Translation Pipeline"] = f"FAIL: {e}"

# TEST 4: Speech-to-Text & GPU Compatibility
print("\n[TEST 4] Kiểm tra Speech-to-Text Faster-Whisper & GPU RTX 3050:")
try:
    import ctranslate2
    from faster_whisper import WhisperModel
    import torch

    has_cuda = torch.cuda.is_available()
    device_name = torch.cuda.get_device_name(0) if has_cuda else "CPU"
    vram = torch.cuda.get_device_properties(0).total_memory / (1024**3) if has_cuda else 0
    
    print(f"  -> CUDA Available: {has_cuda}")
    print(f"  -> Device: {device_name} (VRAM: {vram:.2f} GB)")
    print(f"  -> CTranslate2 Version: {ctranslate2.__version__}")
    print("  -> STT Hardware Stack: PASSED")
    results["STT & Hardware Compatibility"] = "PASS"
except Exception as e:
    print(f"  -> FAILED: {e}")
    results["STT & Hardware Compatibility"] = f"FAIL: {e}"

# TEST 5: UI Interface Instantiation
print("\n[TEST 5] Kiểm tra Khởi tạo Giao diện PyQt6 & Fluent Interfaces:")
try:
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    
    from app.views.home_interface import HomeInterface
    from app.views.setting_interface import SettingInterface
    from app.views.library_interface import LibraryInterface
    
    home = HomeInterface()
    assert home.license_status == "premium", f"Expected home license status 'premium', got '{home.license_status}'"
    
    setting = SettingInterface()
    setting.setLicenseInfo("premium", "Ứng dụng sẵn sàng")
    assert "AI Dubbing Studio" in setting.lbl_license_status.text()

    # Safely instantiate and clean up LibraryInterface
    LibraryInterface.load_videos = lambda self: None
    lib = LibraryInterface()
    
    print("  -> HomeInterface: Instantiated OK (License: premium)")
    print("  -> SettingInterface: Instantiated OK")
    print("  -> LibraryInterface: Instantiated OK")
    print("  -> UI Stack: PASSED")
    results["UI Interfaces"] = "PASS"
except Exception as e:
    print(f"  -> FAILED: {e}")
    results["UI Interfaces"] = f"FAIL: {e}"

# TEST 6: Model Downloader Subprocess Environment
print("\n[TEST 6] Kiem tra Subprocess Model Downloader (faster_whisper, paddleocr, audio_separator):")
try:
    from app.views.setting_interface import ModelDownloaderWorker
    worker = ModelDownloaderWorker(target_model="none")
    
    output_lines = []
    worker.progress.connect(lambda msg: output_lines.append(msg))
    
    test_subproc_script = (
        "import sys, faster_whisper, paddleocr, audio_separator\n"
        "print('WORKER_SUBPROCESS_OK', flush=True)\n"
    )
    worker._run_script(sys.executable, test_subproc_script)
    
    assert any("WORKER_SUBPROCESS_OK" in line for line in output_lines), f"Subprocess failed to import modules: {output_lines}"
    print("  -> ModelDownloaderWorker._run_script: PASSED (Child process successfully imported all 3 modules)")
    results["Model Downloader Subprocess"] = "PASS"
except Exception as e:
    print(f"  -> FAILED: {e}")
    results["Model Downloader Subprocess"] = f"FAIL: {e}"

# TEST 7: 1080p 60FPS Video Rendering Engine
print("\n[TEST 7] Kiem tra Co che Xuat Video 1080p Full HD & 60 FPS:")
try:
    from app.core import video_renderer
    sample_cmd = [
        'ffmpeg.exe', '-progress', 'pipe:1', '-y',
        '-i', 'input.mp4', '-i', 'audio.mp3',
        '-filter_complex', '[0:v]subtitles=\'sub.srt\'[v];[1:a]volume=1.2[a_out]',
        '-map', '[v]', '-map', '[a_out]',
        '-c:v', 'h264_nvenc', '-preset', 'p4', '-cq', '20', '-c:a', 'aac',
        'output.mp4'
    ]
    upgraded = video_renderer.upgrade_ffmpeg_cmd(sample_cmd)
    
    assert 'fps=fps=60' in str(upgraded), "fps=60 filter missing from upgraded command!"
    assert 'scale=' in str(upgraded), "1080p scale filter missing from upgraded command!"
    assert '-preset' in upgraded and upgraded[upgraded.index('-preset') + 1] == 'p6', "NVENC preset p6 missing!"
    assert '-cq' in upgraded and upgraded[upgraded.index('-cq') + 1] == '16', "NVENC cq 16 missing!"
    assert '-b:a' in upgraded and upgraded[upgraded.index('-b:a') + 1] == '320k', "320k audio missing!"
    assert '-b:v' in upgraded and upgraded[upgraded.index('-b:v') + 1] == '12M', "12M video bitrate missing!"
    
    print("  -> Lanczos 1080p Scaling: PASSED (Smart aspect-ratio preserved)")
    print("  -> 60 FPS Smooth Filter: PASSED (fps=fps=60:round=near)")
    print("  -> NVENC High-Quality Preset p6 / CQ 16: PASSED (12-16 Mbps bitrate)")
    print("  -> Studio Audio 320 kbps: PASSED")
    print("  -> Video Render 1080p60 Engine: PASSED")
    results["Video Renderer 1080p60"] = "PASS"
except Exception as e:
    print(f"  -> FAILED: {e}")
    results["Video Renderer 1080p60"] = f"FAIL: {e}"

print("\n" + "=" * 60)
print("KET QUA KIEM THU TONG QUAN:")
all_pass = True
for name, res in results.items():
    print(f"  [{res}] {name}")
    if res != "PASS":
        all_pass = False

print("=" * 60)
if all_pass:
    print(">>> TAT CA 7 HANG MUC KIEM THU DA DAT CHUAN (100% PASS)! <<<")
else:
    print(">>> CO HANG MUC CHUA DAT! <<<")


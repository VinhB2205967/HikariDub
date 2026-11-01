"""
Standalone Model Downloader Script for Hikari Dub
Downloads all required offline models:
1. Faster-Whisper (tiny, base, small, medium)
2. PaddleOCR (Vietnamese & English OCR models)
3. Audio Separator / Vocal Separation (BS-Roformer & UVR-MDX-Net)
"""

import os
import sys

# Setup environment
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
INTERNAL_DIR = os.path.join(PROJECT_ROOT, "_internal")

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if INTERNAL_DIR not in sys.path:
    sys.path.insert(0, INTERNAL_DIR)

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

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

import app.common.config_manager as cm

hf_cache_dir = cm.get_hf_cache_dir()
paddle_cache_dir = cm.get_paddleocr_cache_dir()
audio_sep_cache_dir = cm.get_audio_sep_cache_dir()

ffmpeg_dir = os.path.join(INTERNAL_DIR, "ffmpeg")
if os.path.exists(ffmpeg_dir):
    os.environ["BUNDLE_FFMPEG_DIR"] = ffmpeg_dir
    os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.path.join(INTERNAL_DIR, "torch", "lib") + os.pathsep + os.environ.get("PATH", "")

print("=" * 65)
print("     TRÌNH TẢI & KIỂM TRA MÔ HÌNH OFFLINE - HIKARI DUB")
print("=" * 65)
print(f"Thư mục Whisper:         {hf_cache_dir}")
print(f"Thư mục PaddleOCR:       {paddle_cache_dir}")
print(f"Thư mục Audio Separator: {audio_sep_cache_dir}")
print("=" * 65)

# --- 1. WHISPER MODELS ---
print("\n[1/3] Đang kiểm tra & tải Mô hình Nhận dạng Giọng nói (Faster-Whisper)...")
os.environ['HF_HOME'] = hf_cache_dir
os.environ['HF_HUB_DISABLE_SYMLINKS'] = '1'
os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'

try:
    from faster_whisper import WhisperModel
    whisper_models = ['tiny', 'base', 'small', 'medium']
    for idx, m_name in enumerate(whisper_models, start=1):
        print(f"  -> [{idx}/{len(whisper_models)}] Kiểm tra / tải gói Chế độ {idx} ({m_name})...", flush=True)
        try:
            WhisperModel(m_name, device='cpu', compute_type='int8')
            print(f"     [OK] Gói {m_name} sẵn sàng.")
        except Exception as e:
            print(f"     [CẢNH BÁO] Không thể tải gói {m_name}: {e}")
    print("  => Hoàn tất kiểm tra Chế độ Nghe (Faster-Whisper)!")
except Exception as e:
    print(f"  [LỖI] Faster-Whisper: {e}")

# --- 2. PADDLEOCR MODELS ---
print("\n[2/3] Đang kiểm tra & tải Mô hình Quét chữ / OCR (PaddleOCR)...")
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['USERPROFILE'] = paddle_cache_dir
os.environ['HOME'] = paddle_cache_dir

try:
    from paddleocr import PaddleOCR
    print("  -> Kiểm tra / tải gói Nhận dạng chữ Tiếng Việt (lang=vi)...", flush=True)
    try:
        PaddleOCR(use_angle_cls=True, lang='vi', use_gpu=False, show_log=False)
        print("     [OK] Gói Tiếng Việt sẵn sàng.")
    except Exception as e:
        print(f"     [CẢNH BÁO] Lỗi tải Tiếng Việt: {e}")

    print("  -> Kiểm tra / tải gói Nhận dạng chữ Tiếng Anh (lang=en)...", flush=True)
    try:
        PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False, show_log=False)
        print("     [OK] Gói Tiếng Anh sẵn sàng.")
    except Exception as e:
        print(f"     [CẢNH BÁO] Lỗi tải Tiếng Anh: {e}")
    print("  => Hoàn tất kiểm tra Chế độ Bóc chữ (PaddleOCR)!")
except Exception as e:
    print(f"  [LỖI] PaddleOCR: {e}")

# --- 3. AUDIO SEPARATOR MODELS ---
print("\n[3/3] Đang kiểm tra & tải Mô hình Tách Nhạc / Lọc Tạp Âm (Audio Separator)...")
try:
    # Patch CDN for TRvlvr application_data
    import urllib.request
    _orig_urlopen = urllib.request.urlopen
    def _patched_urlopen(url, *a, **kw):
        s = url if isinstance(url, str) else (url.full_url if hasattr(url, 'full_url') else str(url))
        if 'raw.githubusercontent.com/TRvlvr/application_data' in s:
            s = s.replace('raw.githubusercontent.com/TRvlvr/application_data/main', 'cdn.jsdelivr.net/gh/TRvlvr/application_data@main')
            if isinstance(url, str): url = s
            else: url = urllib.request.Request(s, headers=dict(url.headers) if hasattr(url,'headers') else {})
        return _orig_urlopen(url, *a, **kw)
    urllib.request.urlopen = _patched_urlopen

    import requests as _rq
    _orig_get = _rq.Session.get
    def _patched_get(self, url, **kw):
        if isinstance(url, str) and 'raw.githubusercontent.com/TRvlvr/application_data' in url:
            url = url.replace('raw.githubusercontent.com/TRvlvr/application_data/main', 'cdn.jsdelivr.net/gh/TRvlvr/application_data@main')
        return _orig_get(self, url, **kw)
    _rq.Session.get = _patched_get

    from audio_separator.separator import Separator
    os.makedirs(audio_sep_cache_dir, exist_ok=True)
    
    print("  -> Tải mô hình BS-Roformer tách tiếng người (~250MB)...", flush=True)
    try:
        Separator(output_dir=audio_sep_cache_dir, model_file_dir=audio_sep_cache_dir).load_model(model_filename='model_bs_roformer_ep_317_sdr_12.9755.ckpt')
        print("     [OK] BS-Roformer sẵn sàng.")
    except Exception as e:
        print(f"     [CẢNH BÁO] Lỗi tải BS-Roformer: {e}")

    print("  -> Tải mô hình Eco UVR-MDX-NET (~66MB)...", flush=True)
    try:
        Separator(output_dir=audio_sep_cache_dir, model_file_dir=audio_sep_cache_dir).load_model(model_filename='UVR-MDX-NET-Inst_HQ_3.onnx')
        print("     [OK] UVR-MDX-NET sẵn sàng.")
    except Exception as e:
        print(f"     [CẢNH BÁO] Lỗi tải UVR-MDX-NET: {e}")
    print("  => Hoàn tất kiểm tra Chế độ Tách Nhạc!")
except Exception as e:
    print(f"  [LỖI] Audio Separator: {e}")

print("\n" + "=" * 65)
print("     HOÀN TẤT TIẾN TRÌNH KIỂM TRA & TẢI MÔ HÌNH!")
print("=" * 65)


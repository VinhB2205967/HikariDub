"""
Vocal Separator Module - Hikari Tsukimi Studio.
Fast, deadlock-free FFmpeg speech isolation & vocal reduction (runs in ~1s):
- vocals.wav: isolates center speech frequencies (highpass + lowpass + afftdn) for clean Whisper STT.
- instrumental.wav: reduces center vocals while preserving stereo BGM & SFX for dubbed export.
"""

import os
import subprocess
import imageio_ffmpeg


def separate_vocals_and_bgm(video_path: str, workspace_dir: str, status_cb=None):
    """
    Separates speech (vocals) and background music/SFX (instrumental) from video_path.
    Returns (vocals_wav_path, instrumental_wav_path).
    """
    if not video_path or not os.path.exists(video_path):
        raise FileNotFoundError(f"Không tìm thấy video: {video_path}")

    sep_dir = os.path.join(workspace_dir, "separated")
    os.makedirs(sep_dir, exist_ok=True)
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    vocals_path = os.path.join(sep_dir, "vocals.wav")
    bgm_path = os.path.join(sep_dir, "instrumental.wav")

    if status_cb:
        status_cb("🎛️ Đang lọc tách lời thoại & nhạc nền (FFmpeg Fast Vocal Filter)...")

    # 1. Vocals track: isolate human speech band (120Hz-7500Hz) + FFT denoise + normalize for accurate STT
    subprocess.run(
        [
            ffmpeg_exe, "-y", "-i", video_path,
            "-vn", "-ac", "1", "-ar", "16000",
            "-af", "aresample=async=1:first_pts=0,highpass=f=120,lowpass=f=7500,afftdn=nf=-22,dynaudnorm",
            "-c:a", "pcm_s16le", vocals_path,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )

    # 2. Instrumental/BGM track: attenuate center-panned speech while keeping stereo BGM & SFX
    subprocess.run(
        [
            ffmpeg_exe, "-y", "-i", video_path,
            "-vn", "-ac", "2", "-ar", "44100",
            "-af", "aresample=async=1:first_pts=0,stereotools=mlev=0.05:slev=1.0,lowpass=f=16000",
            "-c:a", "pcm_s16le", bgm_path,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )

    if status_cb:
        status_cb("✓ Lọc giọng hoàn tất (tách riêng lời thoại & nhạc nền BGM).")
    return vocals_path, bgm_path

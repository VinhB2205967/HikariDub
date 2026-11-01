"""
Video Utilities Module for Hikari Dub
"""

import os
import re
import hashlib
import subprocess
import imageio_ffmpeg

def get_safe_basename(video_path: str) -> str:
    """
    Returns a sanitized basename for a video file, safely truncated if overly long.
    """
    raw_name = os.path.splitext(os.path.basename(video_path))[0]
    if len(raw_name) <= 80:
        return raw_name
    short = raw_name[:50].strip()
    h = hashlib.md5(raw_name.encode('utf-8')).hexdigest()[:6]
    return f"{short}_{h}"

def get_video_duration(video_path: str) -> float:
    """
    Returns the duration of the given video in seconds using ffmpeg.
    """
    try:
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        cmd = [ffmpeg_exe, "-i", video_path]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        _, stderr = process.communicate()
        match = re.search(r'Duration:\s*(\d{2}):(\d{2}):(\d{2}\.\d+)', stderr.decode('utf-8', errors='ignore'))
        if match:
            h, m, s = match.groups()
            return float(h) * 3600 + float(m) * 60 + float(s)
        return 0.0
    except Exception:
        return 0.0


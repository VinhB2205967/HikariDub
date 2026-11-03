"""
Canvas Transform Module - Hikari Dub v3.0
Manages aspect ratio, zoom, position and rotation state for video preview & export.
"""

from __future__ import annotations
import json
import os
import math
from dataclasses import dataclass, asdict, field
from typing import Optional


# ---------------------------------------------------------------------------
# Aspect Ratio Presets
# ---------------------------------------------------------------------------
ASPECT_RATIOS = {
    "9:16":   (1080, 1920),
    "16:9":   (1920, 1080),
    "3:4":    (1080, 1440),
    "1:1":    (1080, 1080),
    "4:3":    (1440, 1080),
    "custom": None,          # width/height supplied by user
}


def get_canvas_size(ratio: str, custom_w: int = 1920, custom_h: int = 1080) -> tuple[int, int]:
    """Return (canvas_width, canvas_height) for the given ratio label."""
    ratio = ratio.strip().lower()
    if ratio in ASPECT_RATIOS and ASPECT_RATIOS[ratio] is not None:
        return ASPECT_RATIOS[ratio]
    # custom or unknown
    return (max(1, int(custom_w)), max(1, int(custom_h)))


# ---------------------------------------------------------------------------
# Transform State
# ---------------------------------------------------------------------------
@dataclass
class CanvasTransform:
    # Aspect ratio / canvas size
    aspect_ratio: str = "16:9"
    canvas_w: int = 1920
    canvas_h: int = 1080

    # Video position & size within canvas (affects export)
    video_scale: float = 1.0    # 1.0 = fit-to-canvas
    pos_x: float = 0.0          # pixel offset from center (positive = right)
    pos_y: float = 0.0          # pixel offset from center (positive = down)
    rotation: float = 0.0       # degrees

    # Preview-only zoom (does NOT affect export)
    preview_zoom: float = 1.0   # 1.0 = 100%
    preview_pan_x: float = 0.0  # preview viewport offset
    preview_pan_y: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "CanvasTransform":
        valid = {k: v for k, v in d.items() if k in cls.__dataclass_fields__}
        return cls(**valid)


# ---------------------------------------------------------------------------
# FFmpeg filter generator
# ---------------------------------------------------------------------------
def build_ffmpeg_vf(transform: CanvasTransform, source_w: int, source_h: int) -> str:
    """
    Build FFmpeg video filter string to apply canvas transform.

    Strategy:
      1. Scale video to fit canvas, then apply video_scale multiplier.
      2. Apply rotation (if any).
      3. Pad/overlay onto canvas background of canvas_w × canvas_h,
         placing video center at (canvas_w/2 + pos_x, canvas_h/2 + pos_y).

    Returns a vf filter string.
    """
    cw, ch = transform.canvas_w, transform.canvas_h
    vscale = max(0.01, transform.video_scale)
    px = transform.pos_x
    py = transform.pos_y
    rot = transform.rotation

    # Step 1: fit video into canvas preserving aspect ratio, then apply scale
    if source_w > 0 and source_h > 0:
        fit_ratio = min(cw / source_w, ch / source_h)
    else:
        fit_ratio = 1.0

    scaled_w = int(source_w * fit_ratio * vscale)
    scaled_h = int(source_h * fit_ratio * vscale)
    # must be even for most codecs
    scaled_w = max(2, scaled_w if scaled_w % 2 == 0 else scaled_w + 1)
    scaled_h = max(2, scaled_h if scaled_h % 2 == 0 else scaled_h + 1)

    vw, vh = scaled_w, scaled_h
    filters = [f"scale={scaled_w}:{scaled_h}:flags=lanczos"]

    # Rotation (if non-zero)
    if abs(rot) > 0.01:
        rot_rad = math.radians(rot)
        rot_w = int(abs(scaled_w * math.cos(rot_rad)) + abs(scaled_h * math.sin(rot_rad)))
        rot_h = int(abs(scaled_w * math.sin(rot_rad)) + abs(scaled_h * math.cos(rot_rad)))
        rot_w = rot_w if rot_w % 2 == 0 else rot_w + 1
        rot_h = rot_h if rot_h % 2 == 0 else rot_h + 1
        filters.append(
            f"rotate={rot_rad:.6f}:ow={rot_w}:oh={rot_h}:fillcolor=black@0"
        )
        vw, vh = rot_w, rot_h

    # Bounding-box placement math:
    # Handles video scaled > canvas, translation, or rotation with zero FFmpeg errors
    tl_x = int(round(cw / 2.0 + px - vw / 2.0))
    tl_y = int(round(ch / 2.0 + py - vh / 2.0))

    min_x = min(0, tl_x)
    max_x = max(cw, tl_x + vw)
    min_y = min(0, tl_y)
    max_y = max(ch, tl_y + vh)

    pad_left = -min_x
    pad_top = -min_y
    pw = max_x - min_x
    ph = max_y - min_y

    # Ensure even dimensions
    if pw % 2 != 0: pw += 1
    if ph % 2 != 0: ph += 1

    vid_pad_x = tl_x + pad_left
    vid_pad_y = tl_y + pad_top

    # Pad video to bounding box
    if pw > vw or ph > vh or vid_pad_x > 0 or vid_pad_y > 0:
        filters.append(f"pad={pw}:{ph}:{vid_pad_x}:{vid_pad_y}:black")

    # Crop bounding box to final canvas size cw:ch
    crop_x = pad_left
    crop_y = pad_top
    if pw != cw or ph != ch or crop_x != 0 or crop_y != 0:
        filters.append(f"crop={cw}:{ch}:{crop_x}:{crop_y}")

    return ",".join(filters)


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------
_DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "Data", "canvas_transform.json"
)


def save_transform(transform: CanvasTransform, path: Optional[str] = None) -> None:
    """Save transform state to JSON file."""
    fpath = path or _DEFAULT_CONFIG_PATH
    os.makedirs(os.path.dirname(fpath), exist_ok=True)
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(transform.to_dict(), f, indent=2, ensure_ascii=False)


def load_transform(path: Optional[str] = None) -> CanvasTransform:
    """Load transform state from JSON file; return default if not found."""
    fpath = path or _DEFAULT_CONFIG_PATH
    if os.path.exists(fpath):
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            return CanvasTransform.from_dict(data)
        except Exception:
            pass
    return CanvasTransform()


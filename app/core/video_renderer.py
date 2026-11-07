"""
Video Renderer Module - Free Forever & Local-First Edition
High-Definition Upgrade: 1080p Full HD & 60 FPS Output
"""

import os
import sys
import importlib.util
import subprocess
import shlex

# Find base video_renderer.pyc
_pyc_path = None
for cand in [
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "pyc_dump", "app", "core", "video_renderer.pyc"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pyc_dump", "app", "core", "video_renderer.pyc"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_internal", "app", "core", "video_renderer.pyc"),
    os.path.join(os.path.dirname(__file__), "video_renderer.pyc"),
    r"D:\HikariDub\pyc_dump\app\core\video_renderer.pyc",
    r"D:\Hikari_Dub\pyc_dump\app\core\video_renderer.pyc"
]:
    if os.path.exists(cand):
        _pyc_path = cand
        break

if not _pyc_path:
    raise FileNotFoundError("Could not find base video_renderer.pyc")

# PyArmor requires sys.modules['app.core.video_renderer'] to be populated
_spec = importlib.util.spec_from_file_location("app.core.video_renderer", _pyc_path)
_base_mod = importlib.util.module_from_spec(_spec)
sys.modules["app.core.video_renderer"] = _base_mod
_spec.loader.exec_module(_base_mod)

# Export all symbols from base module
for attr in dir(_base_mod):
    if not attr.startswith('__'):
        globals()[attr] = getattr(_base_mod, attr)

import re as _re

def _upgrade_mask_filters_in_fc(fc_str: str, src_w: int = None, src_h: int = None) -> str:
    """
    Upgrades Box-Blur mask stages in FFmpeg filter_complex to a hybrid
    `delogo + high-sigma Gaussian blur` pipeline with slight vertical padding.
    This interpolates surrounding background pixels first (completely erasing high-contrast
    white/colored subtitle text) and then smooths the region with Gaussian blur, matching
    the preview canvas 1:1.
    """
    if not fc_str:
        return fc_str

    # Infer native source dimensions from the [v_anticopy] scale=W:H stage if not passed
    if not src_w or not src_h:
        m_scale = _re.search(r'crop=iw\*0\.99:ih\*0\.99,scale=(\d+):(\d+)', fc_str)
        if m_scale:
            src_w = int(m_scale.group(1))
            src_h = int(m_scale.group(2))

    pattern = _re.compile(
        r'(\[(?:0:v|v_mask\d+|v_canvas_in)\])'
        r'split=2\[orig_m(\d+)\]\[tocrop_m\2\];'
        r'\[tocrop_m\2\]crop=(\d+):(\d+):(\d+):(\d+),gblur=sigma=\d+:steps=\d+\[blurred_m\2\];'
        r'\[orig_m\2\]\[blurred_m\2\]overlay=\5:\6(\[v_mask\2\])'
    )

    def _repl(match):
        in_pad = match.group(1)
        idx = match.group(2)
        mw = int(match.group(3))
        mh = int(match.group(4))
        mx = int(match.group(5))
        my = int(match.group(6))
        out_pad = match.group(7)

        # Add slight vertical padding (4px top, 6px bottom) so subtitle strokes/descenders
        # near the red mask border are 100% covered
        pad_top = 4
        pad_bot = 6
        dx = max(2, mx)
        dy = max(2, my - pad_top)
        dw = max(4, mw)
        dh = max(4, mh + pad_top + pad_bot)

        if src_w and src_h:
            if dx >= src_w - 6:
                dx = max(2, src_w - 8)
            if dy >= src_h - 6:
                dy = max(2, src_h - 8)
            dw = max(4, min(src_w - dx - 2, dw))
            dh = max(4, min(src_h - dy - 2, dh))

        return (
            f"{in_pad}delogo=x={dx}:y={dy}:w={dw}:h={dh}[delogo_m{idx}];"
            f"[delogo_m{idx}]split=2[orig_m{idx}][tocrop_m{idx}];"
            f"[tocrop_m{idx}]crop={dw}:{dh}:{dx}:{dy},gblur=sigma=24:steps=2[blurred_m{idx}];"
            f"[orig_m{idx}][blurred_m{idx}]overlay={dx}:{dy}{out_pad}"
        )

    fc_upgraded = pattern.sub(_repl, fc_str)
    fc_upgraded = fc_upgraded.replace('gblur=sigma=15:steps=2', 'gblur=sigma=28:steps=3')
    return fc_upgraded


# -------------------------------------------------------------
# FFmpeg 1080p 60fps Upgrade Engine
# -------------------------------------------------------------
def upgrade_ffmpeg_cmd(args):
    """
    Upgrades FFmpeg rendering commands to output:
    - Resolution: Full HD 1080p (Lanczos high-quality scaling, aspect-ratio preserving)
    - Frame Rate: 60 FPS (fps=fps=60:round=near)
    - Video Bitrate: High bitrate NVENC preset p6 / CQ 16 or CRF 17 (12-16 Mbps)
    - Audio: 320 kbps high-definition AAC
    """
    is_list = isinstance(args, list)
    cmd_list = list(args) if is_list else shlex.split(args)

    if not cmd_list:
        return args

    first_arg = cmd_list[0].lower()
    if not ('ffmpeg' in first_arg or first_arg.endswith('.exe')):
        return args

    # Check for probe or version commands
    cmd_str = " ".join(cmd_list)
    if '-version' in cmd_list or any(cmd_str.strip().endswith(x) for x in ['-version', '-h', '--help']):
        return args

    # Find all input files preceded by '-i'
    input_indices = [idx + 1 for idx, a in enumerate(cmd_list[:-1]) if a == '-i']
    # If the last argument is immediately preceded by '-i', this is a probe call, not a render command
    if (len(cmd_list) - 1) in input_indices:
        return args

    # Check output file extension
    out_file = cmd_list[-1]
    if not any(out_file.lower().endswith(ext) for ext in ['.mp4', '.mkv', '.mov', '.avi']):
        return args

    # Cutting and segmenting may use stream copy; adding video filters to those
    # commands makes FFmpeg fail, so only rewrite actual encoding commands.
    copy_video_options = {'-c', '-codec', '-c:v', '-vcodec'}
    if any(
        arg in copy_video_options and idx + 1 < len(cmd_list) and cmd_list[idx + 1].lower() == 'copy'
        for idx, arg in enumerate(cmd_list)
    ):
        return args

    if any(
        arg == '-f' and idx + 1 < len(cmd_list) and cmd_list[idx + 1].lower() == 'segment'
        for idx, arg in enumerate(cmd_list)
    ) or any(arg in {'-segment_time', '-segment_times', '-segment_frames'} for arg in cmd_list):
        return args

    # Lanczos 1080p + 60fps filter:
    # If horizontal (iw >= ih): scales height to 1080, width auto (divisible by 2)
    # If vertical (ih > iw): scales width to 1080, height auto (divisible by 2)
    enhanced_filter = "fps=fps=60:round=near,scale='if(gte(iw,ih),-2,1080)':'if(gte(iw,ih),1080,-2)':flags=lanczos"

    new_cmd = []
    i = 0
    has_filter_complex = False
    has_vf = False

    while i < len(cmd_list):
        arg = cmd_list[i]

        if arg == '-filter_complex' and i + 1 < len(cmd_list):
            has_filter_complex = True
            fc_str = cmd_list[i + 1]
            # Upgrade mask blur stages to hybrid delogo + high-sigma Gaussian blur
            fc_str = _upgrade_mask_filters_in_fc(fc_str)
            if '[v]' in fc_str:
                fc_str_mod = fc_str.replace('[v]', '[v_pre_scale]')
                fc_str_mod += f"; [v_pre_scale]{enhanced_filter}[v]"
                new_cmd.extend(['-filter_complex', fc_str_mod])
            else:
                fc_str_mod = fc_str + f"; [0:v]{enhanced_filter}[v]"
                new_cmd.extend(['-filter_complex', fc_str_mod])
            i += 2
            continue

        elif arg == '-vf' and i + 1 < len(cmd_list):
            has_vf = True
            vf_str = cmd_list[i + 1]
            vf_str = _upgrade_mask_filters_in_fc(vf_str)
            vf_str_mod = vf_str + f",{enhanced_filter}"
            new_cmd.extend(['-vf', vf_str_mod])
            i += 2
            continue

        elif arg == '-preset' and i + 1 < len(cmd_list):
            curr_preset = cmd_list[i + 1]
            # Upgrade NVENC preset from p1-p4 to p6 (High Quality)
            new_preset = 'p6' if curr_preset.startswith('p') else curr_preset
            new_cmd.extend(['-preset', new_preset])
            i += 2
            continue

        elif arg == '-cq' and i + 1 < len(cmd_list):
            # Upgrade NVENC CQ from 20 -> 16 for sharp, crisp visuals
            new_cmd.extend(['-cq', '16'])
            i += 2
            continue

        elif arg == '-crf' and i + 1 < len(cmd_list):
            # Upgrade CPU CRF to 17 (visually lossless)
            new_cmd.extend(['-crf', '17'])
            i += 2
            continue

        new_cmd.append(arg)
        i += 1

    # If neither filter_complex nor -vf was present, add -vf
    out_arg = new_cmd.pop()
    if not has_filter_complex and not has_vf:
        new_cmd.extend(['-vf', enhanced_filter])

    # Optimize Video Bitrate for 1080p60
    if '-c:v' in new_cmd:
        c_idx = new_cmd.index('-c:v')
        codec = new_cmd[c_idx + 1] if c_idx + 1 < len(new_cmd) else ''
        if 'nvenc' in codec:
            if '-b:v' not in new_cmd:
                new_cmd.extend(['-b:v', '12M', '-maxrate', '16M', '-bufsize', '20M'])
        elif '264' in codec:
            if '-preset' not in new_cmd:
                new_cmd.extend(['-preset', 'medium'])

    # Optimize Audio to Studio 320k
    if '-b:a' not in new_cmd and '-c:a' in new_cmd:
        a_idx = new_cmd.index('-c:a')
        new_cmd.insert(a_idx + 2, '320k')
        new_cmd.insert(a_idx + 2, '-b:a')

    new_cmd.append(out_arg)
    return new_cmd if is_list else " ".join(new_cmd)


# Patch render_logic in video_renderer
_orig_render_logic = _base_mod.render_logic

def render_logic_patched(video_path, srt_path, audio_path, workspace_dir, status_cb, cancel_event, license_status='expired', video_config=None):
    """
    Wrapped render_logic ensuring 1080p 60fps output and permanent premium status.
    """
    license_status = 'premium'

    announced_hd = False
    def wrapped_status_cb(msg, *a, **kw):
        nonlocal announced_hd
        if not announced_hd and ('bắt đầu' in msg.lower() or 'xuất video' in msg.lower()):
            announced_hd = True
            msg = f"{msg} [Chuẩn 1080p Full HD - 60 FPS]"
        if status_cb:
            try:
                status_cb(msg, *a, **kw)
            except Exception:
                try:
                    status_cb(msg)
                except Exception:
                    pass

    orig_sub_popen = _base_mod.subprocess.Popen
    class HighDefPopen(orig_sub_popen):
        def __init__(self, *args, **kwargs):
            try:
                cmd = args[0] if args else kwargs.get('args')
                upgraded = upgrade_ffmpeg_cmd(cmd)
                if args:
                    args = (upgraded,) + args[1:]
                elif 'args' in kwargs:
                    kwargs['args'] = upgraded
            except Exception:
                pass
            super().__init__(*args, **kwargs)

    _base_mod.subprocess.Popen = HighDefPopen
    subprocess.Popen = HighDefPopen

    try:
        return _orig_render_logic(
            video_path=video_path,
            srt_path=srt_path,
            audio_path=audio_path,
            workspace_dir=workspace_dir,
            status_cb=wrapped_status_cb,
            cancel_event=cancel_event,
            license_status='premium',
            video_config=video_config
        )
    finally:
        _base_mod.subprocess.Popen = orig_sub_popen

render_logic = render_logic_patched
_base_mod.render_logic = render_logic_patched
_base_mod.render_logic_patched = render_logic_patched
_base_mod.upgrade_ffmpeg_cmd = upgrade_ffmpeg_cmd


# ─────────────────────────────────────────────────────────────────────────────
# Canvas Transform Export Integration
# Reads canvas_transform.json written by CanvasControlsWidget and injects
# the correct FFmpeg filters into the export pipeline.
# ─────────────────────────────────────────────────────────────────────────────

def _get_video_dimensions(video_path: str):
    """Return (width, height) of video using ffprobe. Returns (1920,1080) on failure."""
    try:
        import subprocess as _sp, json as _json
        probe_cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_streams", video_path
        ]
        res = _sp.run(probe_cmd, capture_output=True, text=True, timeout=15)
        data = _json.loads(res.stdout)
        for s in data.get("streams", []):
            if s.get("codec_type") == "video":
                return int(s.get("width", 1920)), int(s.get("height", 1080))
    except Exception:
        pass
    return 1920, 1080


def apply_canvas_transform_to_ffmpeg(cmd_list: list, video_path: str, video_config: dict = None) -> list:
    """
    Injects canvas transform (aspect ratio, scale, position, rotation) into
    the FFmpeg command's filter chain.

    This runs BEFORE upgrade_ffmpeg_cmd so the 1080p scale filter is appended last.
    """
    try:
        from app.core.canvas_transform import load_transform, build_ffmpeg_vf

        # Load persisted transform
        transform = load_transform()

        # Allow video_config to override persisted transform (e.g., from UI)
        if video_config:
            if 'canvas_w'     in video_config: transform.canvas_w     = int(video_config['canvas_w'])
            if 'canvas_h'     in video_config: transform.canvas_h     = int(video_config['canvas_h'])
            if 'video_scale'  in video_config: transform.video_scale  = float(video_config['video_scale'])
            if 'pos_x'        in video_config: transform.pos_x        = float(video_config['pos_x'])
            if 'pos_y'        in video_config: transform.pos_y        = float(video_config['pos_y'])
            if 'rotation'     in video_config: transform.rotation     = float(video_config['rotation'])

        # Only inject if user changed canvas size or position/scale/rotation
        is_default = (
            transform.aspect_ratio == "16:9"
            and transform.canvas_w == 1920
            and transform.canvas_h == 1080
            and abs(transform.video_scale - 1.0) < 0.01
            and abs(transform.pos_x) < 1
            and abs(transform.pos_y) < 1
            and abs(transform.rotation) < 0.1
        )
        if is_default:
            return cmd_list  # nothing to do — upgrade_ffmpeg_cmd handles 1080p

        # Get source video dimensions
        src_w, src_h = _get_video_dimensions(video_path)

        # Build the canvas transform vf filter
        canvas_vf = build_ffmpeg_vf(transform, src_w, src_h)

        new_cmd = list(cmd_list)

        # Inject into existing filter_complex or -vf, or add new -vf
        has_filter_complex = False
        has_vf = False
        i = 0
        result = []

        while i < len(new_cmd):
            arg = new_cmd[i]
            if arg == '-filter_complex' and i + 1 < len(new_cmd):
                has_filter_complex = True
                fc = new_cmd[i + 1]
                # _orig_render_logic computes all mask (crop/delogo/overlay) and anti-copy
                # coordinates at the SOURCE video resolution (src_w x src_h).
                # Inject canvas_vf AFTER [v_anticopy] so masks run on native source coordinates first.
                if '[v_anticopy]; [v_anticopy]' in fc:
                    fc = fc.replace(
                        '[v_anticopy]; [v_anticopy]',
                        f'[v_anticopy]; [v_anticopy]{canvas_vf}[v_canvas_in]; [v_canvas_in]',
                        1
                    )
                elif '[v_anticopy];[v_anticopy]' in fc:
                    fc = fc.replace(
                        '[v_anticopy];[v_anticopy]',
                        f'[v_anticopy];[v_anticopy]{canvas_vf}[v_canvas_in];[v_canvas_in]',
                        1
                    )
                elif '[0:v]' in fc:
                    fc = fc.replace('[0:v]', f'[0:v]{canvas_vf}[v_canvas_in];[v_canvas_in]', 1)
                else:
                    fc = f"[0:v]{canvas_vf}[v_canvas_out];{fc}"
                result.extend(['-filter_complex', fc])
                i += 2
                continue
            elif arg == '-vf' and i + 1 < len(new_cmd):
                has_vf = True
                vf = new_cmd[i + 1]
                result.extend(['-vf', f"{canvas_vf},{vf}"])
                i += 2
                continue
            result.append(arg)
            i += 1

        if not has_filter_complex and not has_vf:
            # Insert -vf before the output file (last arg)
            out = result.pop()
            result.extend(['-vf', canvas_vf])
            result.append(out)

        return result

    except Exception as e:
        print(f"[HikariDub] canvas transform export error: {e}")
        import traceback; traceback.print_exc()
        return cmd_list  # fail-safe: return original command


# Patch render_logic to also apply canvas transform before 1080p upgrade
_orig_render_logic_v2 = render_logic_patched

def render_logic_with_canvas(video_path, srt_path, audio_path, workspace_dir,
                              status_cb, cancel_event, license_status='expired',
                              video_config=None):
    """
    Enhanced render_logic that normalizes mask_logos/mask_mode, applies canvas transform,
    and upgrades output to 1080p Full HD 60 FPS.
    """
    license_status = 'premium'

    # Ensure video_config has latest mask_logos and uses high-strength Gaussian Box Blur instead of fragile delogo
    try:
        from app.common.config_manager import get_config, set_config
        saved_ov = dict(get_config('video_overlay', {}) or {})
        if video_config is None:
            video_config = dict(saved_ov)
        else:
            merged_cfg = dict(saved_ov)
            merged_cfg.update(video_config)
            if not merged_cfg.get('mask_logos') and saved_ov.get('mask_logos'):
                merged_cfg['mask_logos'] = saved_ov['mask_logos']
            video_config = merged_cfg

        m_mode = str(video_config.get('mask_mode', 'Làm mờ tự nhiên (Khuyên dùng)')).lower()
        if 'ô vuông' not in m_mode and 'pixelate' not in m_mode and 'đắp' not in m_mode and 'clone' not in m_mode:
            video_config['mask_mode'] = 'Làm mờ nhòe (Box Blur)'
    except Exception:
        pass

    announced_hd = [False]
    def wrapped_status_cb2(msg, *a, **kw):
        if not announced_hd[0] and ('bắt đầu' in msg.lower() or 'xuất video' in msg.lower()):
            announced_hd[0] = True
            msg = f"{msg} [Chuẩn 1080p Full HD - 60 FPS + Canvas Transform]"
        if status_cb:
            try:
                status_cb(msg, *a, **kw)
            except Exception:
                try:
                    status_cb(msg)
                except Exception:
                    pass

    orig_sub_popen2 = _base_mod.subprocess.Popen

    class CanvasAndHDPopen(orig_sub_popen2):
        def __init__(self, *args, **kwargs):
            try:
                cmd = args[0] if args else kwargs.get('args')
                if isinstance(cmd, list):
                    # Step 1: apply canvas transform
                    cmd = apply_canvas_transform_to_ffmpeg(cmd, video_path, video_config)
                    # Step 2: upgrade to 1080p/60fps
                    cmd = upgrade_ffmpeg_cmd(cmd)
                if args:
                    args = (cmd,) + args[1:]
                elif 'args' in kwargs:
                    kwargs['args'] = cmd
            except Exception:
                pass
            super().__init__(*args, **kwargs)

    _base_mod.subprocess.Popen = CanvasAndHDPopen

    try:
        return _orig_render_logic(\
            video_path=video_path,
            srt_path=srt_path,
            audio_path=audio_path,
            workspace_dir=workspace_dir,
            status_cb=wrapped_status_cb2,
            cancel_event=cancel_event,
            license_status='premium',
            video_config=video_config
        )
    finally:
        _base_mod.subprocess.Popen = orig_sub_popen2


render_logic = render_logic_with_canvas
_base_mod.render_logic = render_logic_with_canvas
_base_mod.render_logic_patched = render_logic_with_canvas
_base_mod.apply_canvas_transform_to_ffmpeg = apply_canvas_transform_to_ffmpeg
_base_mod._upgrade_mask_filters_in_fc = _upgrade_mask_filters_in_fc

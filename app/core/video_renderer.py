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

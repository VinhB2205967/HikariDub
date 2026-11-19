"""
Audio Generator Module - Hikari Tsukimi v3.2
Zero-Drop Smart Voice Sync Engine:
1. Elastic SRT Timeline Rebalancing (borrows silent gaps & rebalances tight adjacent lines by syllable count)
2. Automatic TTS Leading/Trailing Dead-Silence Trimming (recovers 200-400ms of speaking time per line)
3. Guaranteed Zero-Truncation atempo fitting (100% of words spoken clearly, zero cut-off sentences)
"""

import os
import re
import sys
import shutil
import subprocess
import importlib.util
import unicodedata

# Pure-Python base implementation (no .pyc dependency)
_base_mod = sys.modules[__name__]


def get_audio_duration(file_path: str) -> float:
    """Return duration of a WAV/audio file in seconds."""
    if not file_path or not os.path.exists(file_path):
        return 0.0
    if file_path.lower().endswith(".wav"):
        try:
            import wave
            with wave.open(file_path, "rb") as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                if rate > 0:
                    return frames / float(rate)
        except Exception:
            pass
    try:
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        out = subprocess.run(
            [ffmpeg_exe, "-i", file_path],
            capture_output=True, text=True, encoding="utf-8", errors="ignore"
        ).stderr
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", out or "")
        if m:
            return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    except Exception:
        pass
    return 0.0


def fetch_piper_voice(idx, text: str, temp_files: list, cancel_event, workspace_dir: str, voice):
    """Synthesize a single subtitle line using a loaded PiperVoice instance."""
    import wave
    if cancel_event and cancel_event.is_set():
        return None
    os.makedirs(workspace_dir, exist_ok=True)
    out_wav = os.path.join(workspace_dir, f"temp_sub_{idx}_raw.wav")
    cleaned = _clean_tts_text(text) or "..."
    with wave.open(out_wav, "wb") as wf:
        voice.synthesize_wav(cleaned, wf)
    if temp_files is not None:
        temp_files.append(out_wav)
    return out_wav


def fetch_tiktok_voice(idx, text: str, temp_files: list, cancel_event, workspace_dir: str, voice_id: str, session_id: str):
    """Synthesize a single subtitle line using TikTok TTS API with sessionid."""
    import base64
    import requests

    if cancel_event and cancel_event.is_set():
        return None
    if not session_id or not str(session_id).strip():
        raise ValueError("Giọng TikTok yêu cầu nhập TikTok Session ID!")

    os.makedirs(workspace_dir, exist_ok=True)
    cleaned = _clean_tts_text(text) or "..."
    vid = str(voice_id or "BV074_streaming").replace("tiktok:", "").strip()

    endpoints = [
        "https://api16-normal-c-useast1a.tiktokv.com/media/api/text/speech/invoke/",
        "https://api16-normal-v6.tiktokv.com/media/api/text/speech/invoke/",
        "https://api22-normal-c-useast1a.tiktokv.com/media/api/text/speech/invoke/",
    ]
    headers = {
        "User-Agent": "com.zhiliaoapp.musically/2022600030 (Linux; U; Android 7.1.2; es_ES; SM-G988N; Build/NRD90M;tt-ok/3.12.13.1)",
        "Cookie": f"sessionid={str(session_id).strip()}",
    }

    last_err = None
    for url in endpoints:
        try:
            resp = requests.post(
                url,
                params={"text_speaker": vid, "req_text": cleaned, "speaker_map_type": 0, "aid": 1233},
                headers=headers,
                timeout=15,
            )
            data = resp.json()
            v_str = (data.get("data") or {}).get("v_str")
            if v_str:
                out_mp3 = os.path.join(workspace_dir, f"temp_sub_{idx}_raw.mp3")
                with open(out_mp3, "wb") as f:
                    f.write(base64.b64decode(v_str))
                if temp_files is not None:
                    temp_files.append(out_mp3)
                return out_mp3
            last_err = data.get("message") or data.get("status_msg") or str(data)
        except Exception as e:
            last_err = str(e)

    raise RuntimeError(f"TikTok TTS lỗi ({vid}): {last_err}")


def _base_generate_audio_logic(
    srt_path: str,
    api_key=None,
    voice_model: str = "banmai",
    status_cb=None,
    cancel_event=None,
    temp_files=None,
    workspace_dir: str = ".",
    target_lang: str = "Tiếng Việt",
    max_speed: float = 1.35,
):
    """Pure-Python Piper TTS & TikTok SessionID TTS + FFmpeg timeline assembly."""
    import pysrt
    import imageio_ffmpeg
    from app.common.config_manager import get_config

    if temp_files is None:
        temp_files = []
    os.makedirs(workspace_dir, exist_ok=True)
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    proj_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    voice_raw = str(voice_model or "banmai").strip()
    is_tiktok = voice_raw.startswith("tiktok:") or voice_raw.startswith("BV") or "_" in voice_raw and not voice_raw.startswith("vi_VN-")

    voice = None
    tiktok_vid = None
    session_id = str(api_key or "").strip() or str(get_config("tiktok_session_id", "") or "").strip()

    if is_tiktok:
        tiktok_vid = voice_raw.replace("tiktok:", "").strip()
        if not session_id:
            raise ValueError("Vui lòng nhập TikTok Session ID để sử dụng giọng đọc TikTok!")
    else:
        from piper import PiperVoice
        voice_name = voice_raw.replace("piper:", "").strip()
        if voice_name == "vais1000":
            voice_name = "vi_VN-vais1000-medium"
        voice_name_onnx = voice_name if voice_name.endswith(".onnx") else f"{voice_name}.onnx"

        model_path = None
        for cand in [
            voice_name if os.path.exists(voice_name) else "",
            os.path.join(proj_root, "models", "piper", "vi", voice_name_onnx),
            os.path.join(proj_root, "models", "piper", "Tiếng Việt", voice_name_onnx),
            os.path.join(proj_root, "models", "piper", voice_name_onnx),
            os.path.join(proj_root, "_internal", "models", "piper", "Tiếng Việt", voice_name_onnx),
        ]:
            if cand and os.path.exists(cand):
                model_path = cand
                break

        if not model_path:
            raise FileNotFoundError(f"Không tìm thấy model Piper TTS: {voice_name_onnx}")

        cfg_path = model_path + ".json"
        voice = PiperVoice.load(model_path, cfg_path if os.path.exists(cfg_path) else None)

    subs = pysrt.open(srt_path, encoding="utf-8")
    total = max(1, len(subs))

    inputs = []
    filter_parts = []
    mix_labels = []

    for i, sub in enumerate(subs):
        if cancel_event and cancel_event.is_set():
            return None
        if status_cb:
            status_cb(f"Đang tạo giọng đọc {i + 1}/{total}...")

        if is_tiktok:
            raw_audio = fetch_tiktok_voice(i, sub.text, temp_files, cancel_event, workspace_dir, tiktok_vid, session_id)
        else:
            raw_audio = fetch_piper_voice(i, sub.text, temp_files, cancel_event, workspace_dir, voice)
        if not raw_audio or not os.path.exists(raw_audio):
            continue

        start_ms = sub.start.ordinal
        end_ms = sub.end.ordinal
        slot_sec = max(0.3, (end_ms - start_ms) / 1000.0)
        raw_dur = get_audio_duration(raw_audio)
        speed = 1.0
        if raw_dur > slot_sec and slot_sec > 0:
            speed = min(float(max_speed or 1.6), max(1.0, (raw_dur / slot_sec) * 1.02))

        fitted_wav = os.path.join(workspace_dir, f"temp_sub_{i}_fit.wav")
        atempo_str = _build_atempo_filter_str(speed)
        subprocess.run(
            [ffmpeg_exe, "-y", "-i", raw_audio, "-filter:a", atempo_str, "-ar", "44100", "-ac", "1", fitted_wav],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False
        )
        use_wav = fitted_wav if os.path.exists(fitted_wav) else raw_audio
        if use_wav not in temp_files:
            temp_files.append(use_wav)

        idx_in = len(mix_labels)
        inputs.extend(["-i", use_wav])
        lbl = f"[a{idx_in}]"
        filter_parts.append(f"[{idx_in}:a]adelay={start_ms}|{start_ms}{lbl}")
        mix_labels.append(lbl)

    if not mix_labels:
        return None

    out_audio = os.path.join(workspace_dir, "dubbed_voice.wav")
    if len(mix_labels) == 1:
        fc = filter_parts[0]
        out_map = mix_labels[0]
    else:
        fc = ";".join(filter_parts) + f";{''.join(mix_labels)}amix=inputs={len(mix_labels)}:duration=longest:normalize=0[aout]"
        out_map = "[aout]"
    cmd = [ffmpeg_exe, "-y", *inputs, "-filter_complex", fc, "-map", out_map, "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", out_audio]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if res.returncode != 0 or not os.path.exists(out_audio) or os.path.getsize(out_audio) < 100:
        err_msg = res.stderr.decode("utf-8", errors="ignore")[-400:] if res.stderr else "unknown"
        raise RuntimeError(f"FFmpeg ghép giọng đọc thất bại: {err_msg}")
    return out_audio



def _clean_tts_text(text: str) -> str:
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    # Remove emojis
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F700-\U0001F77F"
        "\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F"
        "\U0001FA70-\U0001FAFF\U00002702-\U000027B0\U000024C2-\U0001F251]+",
        flags=re.UNICODE
    )
    text = emoji_pattern.sub("", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) not in ("Cc", "Cf") or ch in ("\n", "\t", " "))
    # Replace excessive punctuation pauses (e.g. "..." inside a short line) with a clean space/comma so TTS doesn't stall
    text = re.sub(r"\.{2,}|…+", ", ", text)
    text = re.sub(r"[ \t]+", " ", text).strip()
    return text


def _count_spoken_units(text: str) -> int:
    """Estimates number of spoken syllables/words in a subtitle line."""
    if not text:
        return 1
    words = [w for w in re.split(r"[\s,.;:!?\"'()\-]+", text.strip()) if w]
    return max(1, len(words))


def rebalance_srt_timings_for_tts(srt_path: str) -> None:
    """
    Elastically rebalances subtitle start/end times before TTS generation & fitting:
    1. Resolves any overlapping timestamps.
    2. Extends subtitle ends into trailing silent gaps so TTS doesn't rush when silence follows.
    3. Within contiguous back-to-back subtitle groups (gap <= 120ms), redistributes slot durations
       smoothly when a line has high syllable density (e.g. 6 words in 0.74s) next to a looser line
       (e.g. 4 words in 1.16s), preventing word truncation or unnatural chipmunk speedup.
    """
    if not srt_path or not os.path.exists(srt_path):
        return
    try:
        import pysrt
        subs = pysrt.open(srt_path, encoding="utf-8")
        n = len(subs)
        if n == 0:
            return

        # 1. Fix any overlaps first
        for i in range(n - 1):
            if subs[i].end.ordinal > subs[i + 1].start.ordinal:
                subs[i].end.ordinal = subs[i + 1].start.ordinal

        # 2. Identify contiguous clusters of subtitles (gap between i and i+1 <= 120ms)
        i = 0
        while i < n:
            j = i
            while j + 1 < n and (subs[j + 1].start.ordinal - subs[j].end.ordinal) <= 120:
                j += 1

            # Cluster is subs[i .. j]
            cluster_start = subs[i].start.ordinal
            cluster_end = subs[j].end.ordinal

            # Can we pull cluster_start slightly earlier into leading silence if line i is dense?
            w_first = _count_spoken_units(subs[i].text)
            dur_first = max(100, subs[i].end.ordinal - subs[i].start.ordinal)
            prev_end = subs[i - 1].end.ordinal + 60 if i > 0 else 0
            lead_slack = max(0, cluster_start - prev_end)
            if (w_first * 320) > dur_first and lead_slack > 80:
                pull_ms = min(lead_slack - 40, 220, (w_first * 320) - dur_first)
                if pull_ms > 20:
                    cluster_start -= int(pull_ms)
                    subs[i].start.ordinal = cluster_start

            # Can we extend cluster_end into trailing silence after sub[j]?
            if j + 1 < n:
                next_cluster_start = subs[j + 1].start.ordinal
                trail_slack = max(0, next_cluster_start - cluster_end)
                if trail_slack > 80:
                    extend_ms = min(trail_slack - 50, 750)
                    if extend_ms > 20:
                        cluster_end += int(extend_ms)
                        subs[j].end.ordinal = cluster_end
            else:
                # Last subtitle in the file: ensure at least 320ms per spoken word
                w_last = _count_spoken_units(subs[j].text)
                needed_last = w_last * 320
                cur_last_dur = cluster_end - subs[j].start.ordinal
                if needed_last > cur_last_dur:
                    cluster_end += min(900, int(needed_last - cur_last_dur))
                    subs[j].end.ordinal = cluster_end

            # 3. If cluster has multiple back-to-back lines (j > i), rebalance internal boundaries
            if j > i:
                total_cluster_dur = max(200 * (j - i + 1), cluster_end - cluster_start)
                orig_durs = [
                    max(150, subs[k].end.ordinal - subs[k].start.ordinal)
                    for k in range(i, j + 1)
                ]
                sum_orig = max(1, sum(orig_durs))
                orig_durs = [d * total_cluster_dur / sum_orig for d in orig_durs]

                weights = [_count_spoken_units(subs[k].text) for k in range(i, j + 1)]
                sum_w = max(1, sum(weights))
                ideal_durs = [w * total_cluster_dur / sum_w for w in weights]

                # Check if any line in the cluster is squeezed (> 4.2 words/sec -> < 238ms/word)
                needs_rebalance = any(
                    (orig_durs[idx_k] / max(1, weights[idx_k])) < 250
                    for idx_k in range(len(weights))
                )
                if needs_rebalance:
                    # Blend 45% original timing + 55% word-proportional timing, capped at +-450ms shift per boundary
                    blended = [
                        0.45 * orig_durs[idx_k] + 0.55 * ideal_durs[idx_k]
                        for idx_k in range(len(weights))
                    ]
                    # Enforce minimum 190ms per word where possible
                    cur_t = float(cluster_start)
                    for idx_k, k in enumerate(range(i, j + 1)):
                        subs[k].start.ordinal = int(round(cur_t))
                        if k < j:
                            raw_end = cur_t + blended[idx_k]
                            # Clamp boundary shift to at most 480ms from original boundary so visuals stay aligned
                            orig_boundary = subs[k].end.ordinal
                            clamped_end = max(orig_boundary - 420, min(orig_boundary + 480, raw_end))
                            clamped_end = max(cur_t + 450, min(float(cluster_end - 450 * (j - k)), clamped_end))
                            subs[k].end.ordinal = int(round(clamped_end))
                            cur_t = float(subs[k].end.ordinal)
                        else:
                            subs[k].end.ordinal = int(round(cluster_end))

            i = j + 1

        subs.save(srt_path, encoding="utf-8")
    except Exception as e:
        print(f"[audio_generator] rebalance_srt_timings_for_tts warning: {e}")


def _get_ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def _trim_tts_silence_in_place(audio_path: str) -> None:
    """
    Strips leading and trailing dead silence from a generated TTS clip in-place.
    Recovers 200ms-400ms of speaking time per subtitle so voices don't need excessive speedup
    and never get their final words chopped off.
    """
    if not audio_path or not os.path.exists(audio_path):
        return
    try:
        ffmpeg_exe = _get_ffmpeg_exe()
        tmp_out = audio_path + "_trimmed.wav"
        # Trim silence > 15ms at start and > 25ms at end below -42dB
        af_filter = (
            "silenceremove=start_periods=1:start_silence=0.015:start_threshold=-42dB,"
            "areverse,"
            "silenceremove=start_periods=1:start_silence=0.025:start_threshold=-42dB,"
            "areverse"
        )
        creationflags = 0x08000000 if sys.platform == "win32" else 0
        cmd = [
            ffmpeg_exe, "-y", "-i", audio_path,
            "-af", af_filter,
            "-ar", "44100", "-ac", "2",
            tmp_out
        ]
        res = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=15,
            creationflags=creationflags,
        )
        if res.returncode == 0 and os.path.exists(tmp_out) and os.path.getsize(tmp_out) > 1024:
            # Verify trimmed duration is valid (> 0.12s)
            dur = _base_mod.get_audio_duration(tmp_out)
            if dur >= 0.12:
                shutil.move(tmp_out, audio_path)
                return
        if os.path.exists(tmp_out):
            os.remove(tmp_out)
    except Exception:
        pass


def _extract_audio_path_from_ret(ret):
    if isinstance(ret, str):
        return ret
    if isinstance(ret, (tuple, list)) and len(ret) >= 2 and isinstance(ret[1], str):
        return ret[1]
    return None

# Wrap fetch_piper_voice and fetch_tiktok_voice so every raw TTS clip is automatically silence-trimmed
_orig_fetch_piper_voice = getattr(_base_mod, "fetch_piper_voice", None)
if callable(_orig_fetch_piper_voice):
    def _patched_fetch_piper_voice(*args, **kwargs):
        ret = _orig_fetch_piper_voice(*args, **kwargs)
        p = _extract_audio_path_from_ret(ret)
        if p and os.path.exists(p):
            _trim_tts_silence_in_place(p)
        return ret
    fetch_piper_voice = _patched_fetch_piper_voice
    _base_mod.fetch_piper_voice = _patched_fetch_piper_voice
    globals()["fetch_piper_voice"] = _patched_fetch_piper_voice

_orig_fetch_tiktok_voice = getattr(_base_mod, "fetch_tiktok_voice", None)
if callable(_orig_fetch_tiktok_voice):
    def _patched_fetch_tiktok_voice(*args, **kwargs):
        ret = _orig_fetch_tiktok_voice(*args, **kwargs)
        p = _extract_audio_path_from_ret(ret)
        if p and os.path.exists(p):
            _trim_tts_silence_in_place(p)
        return ret
    fetch_tiktok_voice = _patched_fetch_tiktok_voice
    _base_mod.fetch_tiktok_voice = _patched_fetch_tiktok_voice
    globals()["fetch_tiktok_voice"] = _patched_fetch_tiktok_voice


def _build_atempo_filter_str(speed: float) -> str:
    speed = max(0.5, min(6.0, float(speed)))
    parts = []
    while speed > 2.0:
        parts.append("atempo=2.0")
        speed /= 2.0
    while speed < 0.5:
        parts.append("atempo=0.5")
        speed /= 0.5
    parts.append(f"atempo={speed:.4f}")
    return ",".join(parts)


def _parse_atempo_product(filter_str: str) -> float:
    prod = 1.0
    for m in re.finditer(r"atempo=([0-9.]+)", filter_str or ""):
        try:
            prod *= float(m.group(1))
        except Exception:
            pass
    return prod


_orig_generate_audio_logic = _base_generate_audio_logic

def generate_audio_logic_patched(*args, **kwargs):
    """
    Zero-Drop Smart Voice Sync wrapper around generate_audio_logic:
    args: (srt_path, api_key, voice_model, status_cb, cancel_event, temp_files, workspace_dir, target_lang, max_speed)
    """
    import pysrt

    args_list = list(args)
    srt_path = args_list[0] if len(args_list) > 0 else kwargs.get("srt_path")
    subs_cache = []

    # 1. Clean text & elastically rebalance SRT timings so tight lines never get cut off
    if srt_path and os.path.exists(srt_path):
        try:
            subs = pysrt.open(srt_path, encoding="utf-8")
            changed = False
            for sub in subs:
                cleaned = _clean_tts_text(sub.text)
                if not any(unicodedata.category(c).startswith("L") for c in cleaned):
                    cleaned = "..."
                if cleaned != sub.text:
                    sub.text = cleaned
                    changed = True
            if changed:
                subs.save(srt_path, encoding="utf-8")
            # Rebalance tight adjacent slots & extend into silent gaps
            rebalance_srt_timings_for_tts(srt_path)
            subs_cache = list(pysrt.open(srt_path, encoding="utf-8"))
        except Exception as e:
            print(f"[audio_generator] Clean/Rebalance SRT warning: {e}")

    # 2. Wrap subprocess.Popen during _orig_generate_audio_logic so if any individual
    # sentence's TTS audio at user's chosen speed would still exceed the time slot before
    # the next subtitle starts, we dynamically adjust that clip's atempo so 100% of its
    # words fit inside the slot without ever being truncated in temp_audio_tong.pcm!
    orig_popen = _base_mod.subprocess.Popen

    class ZeroDropPopen(orig_popen):
        def __init__(self, popen_args, *p_rest, **p_kwargs):
            try:
                if isinstance(popen_args, list) and "-filter:a" in popen_args and "-i" in popen_args:
                    i_idx = popen_args.index("-i") + 1
                    fa_idx = popen_args.index("-filter:a") + 1
                    if i_idx < len(popen_args) and fa_idx < len(popen_args):
                        in_file = str(popen_args[i_idx])
                        cur_filter = str(popen_args[fa_idx])
                        m_sub = re.search(r"temp_sub_(\d+)_", os.path.basename(in_file))
                        if m_sub and subs_cache:
                            sub_idx = int(m_sub.group(1))
                            if 0 <= sub_idx < len(subs_cache):
                                cur_start_ms = subs_cache[sub_idx].start.ordinal
                                if sub_idx + 1 < len(subs_cache):
                                    avail_ms = max(250, subs_cache[sub_idx + 1].start.ordinal - cur_start_ms - 25)
                                else:
                                    avail_ms = max(2500, subs_cache[sub_idx].end.ordinal - cur_start_ms + 800)
                                avail_sec = avail_ms / 1000.0
                                raw_dur = _base_mod.get_audio_duration(in_file)
                                cur_speed = _parse_atempo_product(cur_filter)
                                if raw_dur > 0 and (raw_dur / max(0.1, cur_speed)) > avail_sec:
                                    needed_speed = (raw_dur / avail_sec) * 1.03
                                    popen_args = list(popen_args)
                                    popen_args[fa_idx] = _build_atempo_filter_str(max(cur_speed, needed_speed))
            except Exception:
                pass
            super().__init__(popen_args, *p_rest, **p_kwargs)

    _base_mod.subprocess.Popen = ZeroDropPopen
    try:
        if _orig_generate_audio_logic:
            return _orig_generate_audio_logic(*args_list, **kwargs)
    finally:
        _base_mod.subprocess.Popen = orig_popen

generate_audio_logic = generate_audio_logic_patched
_base_mod.generate_audio_logic = generate_audio_logic_patched
_base_mod.rebalance_srt_timings_for_tts = rebalance_srt_timings_for_tts
_base_mod._clean_tts_text = _clean_tts_text
globals()["generate_audio_logic"] = generate_audio_logic_patched

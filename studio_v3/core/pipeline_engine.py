"""
Core State-Machine Pipeline Engine for Hikari Tsukimi v3.0.
Each step (0: Transcribe, 1: Translate, 2: TTS, 3: Export 1080p) caches its intermediate output
and can be run independently or resumed after an error. Never logs sensitive credentials.
"""

import os
import sys
import time
import threading

# Allow importing existing core modules from parent root D:\HikariDub
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)


class PipelineContext:
    def __init__(self, video_path: str, output_dir: str, config: dict):
        self.video_path = video_path
        self.output_dir = output_dir
        self.config = dict(config or {})
        base = os.path.splitext(os.path.basename(video_path))[0][:64]
        self.workspace_dir = os.path.join(output_dir, base)
        self.data_dir = os.path.join(self.workspace_dir, "Data")
        os.makedirs(self.data_dir, exist_ok=True)
        self.orig_srt = os.path.join(self.data_dir, "temp_original.srt")
        self.trans_srt = os.path.join(self.data_dir, "temp_translated.srt")
        self.audio_wav = os.path.join(self.workspace_dir, "dubbed_voice.wav")
        self.bgm_wav = ""
        self.final_mp4 = ""


class PipelineEngine:
    """Executes and caches the 4 dubbing stages with pre-flight validation."""

    @staticmethod
    def validate_inputs(ctx: PipelineContext, step: int = None) -> None:
        if not ctx.video_path or not os.path.exists(ctx.video_path):
            raise ValueError("Vui lòng chọn file video nguồn hợp lệ trước khi xử lý.")
        try:
            import imageio_ffmpeg
            ff = imageio_ffmpeg.get_ffmpeg_exe()
            if not ff or not os.path.exists(ff):
                raise RuntimeError("Không tìm thấy thực thi FFmpeg.")
        except Exception as e:
            raise ValueError(f"Chưa sẵn sàng FFmpeg: {e}")

        voice_id = str(ctx.config.get("voice_id") or "piper:banmai")
        if step in (None, 2) and voice_id.startswith("tiktok:"):
            sid = str(ctx.config.get("tiktok_session_id") or "").strip()
            if not sid:
                raise ValueError("Giọng đọc TikTok yêu cầu nhập TikTok Session ID.")

    @staticmethod
    def run_step_0_transcribe(ctx: PipelineContext, log_cb, cancel_ev: threading.Event) -> str:
        import subprocess
        import imageio_ffmpeg
        import pysrt
        import ctranslate2
        from faster_whisper import WhisperModel

        audio_src = ctx.video_path
        if ctx.config.get("vocal_sep"):
            from app.core.vocal_separator import separate_vocals_and_bgm
            voc, bgm = separate_vocals_and_bgm(ctx.video_path, ctx.workspace_dir, status_cb=log_cb)
            if voc and os.path.exists(voc):
                audio_src = voc
            if bgm and os.path.exists(bgm):
                ctx.bgm_wav = bgm

        if cancel_ev.is_set():
            raise InterruptedError("Đã hủy bóc băng.")

        synced_wav = os.path.join(ctx.data_dir, "stt_synced_16k.wav")
        ff = imageio_ffmpeg.get_ffmpeg_exe()
        subprocess.run(
            [ff, "-y", "-i", audio_src, "-vn", "-ac", "1", "-ar", "16000", "-af", "aresample=async=1:first_pts=0", synced_wav],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False
        )
        if os.path.exists(synced_wav) and os.path.getsize(synced_wav) > 1000:
            audio_src = synced_wav

        model_size = ctx.config.get("whisper_model", "small")
        device = "cuda" if ctranslate2.get_cuda_device_count() > 0 else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        log_cb(f"Đang nạp mô hình Whisper ({model_size}, {device})...")
        model = WhisperModel(model_size, device=device, compute_type=compute_type)

        src_lang = ctx.config.get("source_lang", "auto")
        lang_arg = None if src_lang in ("auto", "Tự động", "") else src_lang
        segments, _ = model.transcribe(
            audio_src,
            language=lang_arg,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=250, speech_pad_ms=60, threshold=0.45),
            word_timestamps=True,
            condition_on_previous_text=False,
        )

        subs = pysrt.SubRipFile()
        prev_end_ms = 0
        idx = 0
        for seg in segments:
            if cancel_ev.is_set():
                raise InterruptedError("Đã hủy bóc băng.")
            txt = (seg.text or "").strip()
            if not txt:
                continue
            words = getattr(seg, "words", None) or []
            if words:
                s_sec = float(words[0].start)
                e_sec = float(words[-1].end)
                if len(words) >= 2 and (float(words[1].start) - s_sec) > 1.2:
                    s_sec = max(s_sec, float(words[1].start) - 0.35)
            else:
                s_sec, e_sec = float(seg.start), float(seg.end)

            max_dur = max(2.8, len(txt) * 0.28)
            if (e_sec - s_sec) > max_dur + 1.5:
                s_sec = max(s_sec, e_sec - max_dur)

            s_ms = max(prev_end_ms, int(round(s_sec * 1000)))
            e_ms = max(s_ms + 120, int(round(e_sec * 1000)))
            prev_end_ms = e_ms
            idx += 1
            subs.append(pysrt.SubRipItem(idx, pysrt.SubRipTime.from_ordinal(s_ms), pysrt.SubRipTime.from_ordinal(e_ms), txt))

        subs.save(ctx.orig_srt, encoding="utf-8")
        log_cb(f"✓ Bóc băng hoàn tất ({len(subs)} câu).")
        return ctx.orig_srt

    @staticmethod
    def run_step_1_translate(ctx: PipelineContext, log_cb, cancel_ev: threading.Event) -> str:
        from app.core.ai_translator import translate_logic

        if not os.path.exists(ctx.orig_srt):
            raise FileNotFoundError("Chưa có phụ đề gốc. Hãy chạy Bước 1 (Bóc băng) trước.")
        api_key = str(ctx.config.get("gemini_api_key") or "").strip()
        keys = [api_key] if api_key else ["FREE_MODE"]
        out = translate_logic(
            ctx.orig_srt,
            keys,
            log_cb,
            cancel_ev,
            ctx.workspace_dir,
            prompt_style=ctx.config.get("translate_style", "Tự nhiên"),
            custom_prompt_text=ctx.config.get("custom_prompt", ""),
            target_lang=ctx.config.get("target_lang", "Tiếng Việt"),
        )
        if not out or not os.path.exists(out):
            raise RuntimeError("Không tạo được file phụ đề dịch.")
        ctx.trans_srt = out
        return out

    @staticmethod
    def run_step_2_tts(ctx: PipelineContext, log_cb, cancel_ev: threading.Event) -> str:
        from app.core.audio_generator import generate_audio_logic

        srt_use = ctx.trans_srt if os.path.exists(ctx.trans_srt) else ctx.orig_srt
        if not os.path.exists(srt_use):
            raise FileNotFoundError("Chưa có phụ đề để tạo giọng đọc.")
        sid = str(ctx.config.get("tiktok_session_id") or "").strip()
        voice_id = ctx.config.get("voice_id", "piper:banmai")
        max_spd = max(1.0, float(ctx.config.get("voice_speed", 100)) / 100.0 * 1.35)
        out_wav = generate_audio_logic(
            srt_use, sid, voice_id, log_cb, cancel_ev, [], ctx.workspace_dir,
            ctx.config.get("target_lang", "Tiếng Việt"), max_spd
        )
        if not out_wav or not os.path.exists(out_wav):
            raise RuntimeError("Không tạo được file âm thanh lồng tiếng.")
        ctx.audio_wav = out_wav
        return out_wav

    @staticmethod
    def run_step_3_render(ctx: PipelineContext, log_cb, cancel_ev: threading.Event) -> str:
        from app.core.video_renderer import render_logic

        srt_use = ctx.trans_srt if os.path.exists(ctx.trans_srt) else ctx.orig_srt
        v_cfg = {
            "orig_audio_volume": ctx.config.get("orig_volume", 35),
            "voice_audio_volume": ctx.config.get("voice_volume", 100),
            "bgm_path": ctx.bgm_wav,
            "watermark_text": ctx.config.get("watermark_text", ""),
        }
        out_mp4 = render_logic(
            ctx.video_path, srt_use, ctx.audio_wav, ctx.output_dir,
            log_cb, cancel_ev, "premium", v_cfg
        )
        if not out_mp4 or not os.path.exists(out_mp4):
            raise RuntimeError("Không xuất được video MP4.")
        ctx.final_mp4 = out_mp4
        return out_mp4

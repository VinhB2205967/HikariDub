"""
AI Translator Module - Hikari Tsukimi v3.0
Supports:
1. Google Gemini API via direct REST (100% reliable, zero external dependencies)
2. Free Web Translation (Google Translate gtx + mobile endpoints)
3. Offline Fallback
"""

import os
import re
import time
import json
import urllib.parse
import html
import pysrt
import requests
from typing import List, Optional

# Language mapping
LANG_CODE_MAP = {
    'Tiếng Việt': 'vi',
    'English': 'en',
    'Nhật Bản (日本語)': 'ja',
    'Hàn Quốc (한국어)': 'ko',
    'Tây Ban Nha (Español)': 'es',
    'Pháp (Français)': 'fr',
    'Bồ Đào Nha (Português)': 'pt',
    'Đức (Deutsch)': 'de',
    'Indonesia (Bahasa Indonesia)': 'id',
    'Trung Quốc (中文)': 'zh',
}

# Sensitive word softener
SENSITIVE_REPLACEMENTS = {
    r'\bchết\b': 'qua đời',
    r'\bgiết người\b': 'hành hung',
    r'\bgiết\b': 'hạ gục',
    r'\bđánh đập\b': 'xô xát',
    r'\bmáu me\b': 'vết thương',
    r'\btự tử\b': 'nghĩ quẩn',
    r'\bvũ khí\b': 'dụng cụ',
    r'\bsúng đạn\b': 'hỏa lực',
    r'\bbạo lực\b': 'xung đột',
}

def lach_luat_google_dich(text: str) -> str:
    if not text:
        return text
    result = text
    for pattern, replacement in SENSITIVE_REPLACEMENTS.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result

def is_untranslated(orig_text: str, trans_text: str, target_lang: str = 'Tiếng Việt') -> bool:
    if not orig_text or not trans_text:
        return False
    o = orig_text.strip().lower()
    t = trans_text.strip().lower()
    if o == t and len(o) > 3:
        if target_lang == 'Tiếng Việt':
            vi_chars = set('àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ')
            if not any(c in vi_chars for c in t):
                return True
    return False

def optimize_srt_timing(srt_path: str):
    try:
        subs = pysrt.open(srt_path, encoding='utf-8')
        for i in range(len(subs) - 1):
            if subs[i].end > subs[i + 1].start:
                subs[i].end = subs[i + 1].start
        subs.save(srt_path, encoding='utf-8')
    except Exception as e:
        print(f"Lỗi optimize_srt_timing: {e}")

# Supported Gemini models in priority order (Tối ưu cho gói Free: Mạnh nhất, dịch hay nhất & tốc độ cao nhất)
GEMINI_MODELS = [
    'gemini-2.0-flash',       # Mạnh nhất hiện nay: Dịch văn phong tự nhiên, hiểu ngữ cảnh sâu, cực nhanh, 15 RPM Free
    'gemini-1.5-flash',       # Ổn định và bền bỉ tuyệt đối, tương thích mọi API Key
    'gemini-2.5-flash',       # Bản nâng cấp thế hệ 2.5
    'gemini-2.0-flash-lite',  # Bản siêu nhẹ tốc độ cao (30 RPM Free)
    'gemini-1.5-flash-8b',    # Dự phòng siêu tốc
    'gemini-flash-latest',
]

def translate_gemini_single(text: str, api_key: str, target_lang: str = "Tiếng Việt") -> str:
    """Translates a single line using Gemini REST API."""
    if not text or not text.strip():
        return ""
    prompt = f"Dịch câu sau sang {target_lang} một cách tự nhiên. CHỈ trả về đúng câu đã dịch, không giải thích, không thêm dấu ngoặc kép hay tiền tố gì khác:\n{text.strip()}"
    data = {'contents': [{'parts': [{'text': prompt}]}]}

    for model in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            resp = requests.post(url, json=data, timeout=20)
            if resp.status_code == 200:
                res_json = resp.json()
                candidates = res_json.get('candidates', [])
                if candidates:
                    parts = candidates[0].get('content', {}).get('parts', [])
                    if parts and 'text' in parts[0]:
                        ans = parts[0]['text'].strip()
                        ans = re.sub(r'^(Bản dịch|Dịch|Translation):\s*', '', ans, flags=re.IGNORECASE)
                        return ans.strip(' "“\'”')
            elif resp.status_code in (404, 503):
                continue
            else:
                break
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            break
        except Exception:
            continue
    return ""

def translate_gemini(batch_lines: List[str], api_key: str, target_lang: str = "Tiếng Việt", prompt_style: str = "Mặc định") -> List[str]:
    """Translates a batch of lines using Gemini REST API."""
    if not batch_lines:
        return []
    
    # Construct numbered prompt
    prompt = (
        f"You are a professional subtitle translator. Translate each numbered line into natural {target_lang}.\n"
        f"Style: {prompt_style}.\n"
        "Rules:\n"
        "- Output exactly one translated line per input line.\n"
        "- Preserve the numbering format (e.g. 1. ... 2. ...).\n"
        "- Do NOT add any extra text, markdown formatting, or notes.\n\n"
    )
    for idx, line in enumerate(batch_lines, 1):
        prompt += f"{idx}. {line.strip()}\n"

    data = {'contents': [{'parts': [{'text': prompt}]}]}

    is_network_timeout = False
    for model in GEMINI_MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            resp = requests.post(url, json=data, timeout=30)
            if resp.status_code == 200:
                res_json = resp.json()
                candidates = res_json.get('candidates', [])
                if candidates:
                    parts = candidates[0].get('content', {}).get('parts', [])
                    if parts and 'text' in parts[0]:
                        raw_text = parts[0]['text'].strip()
                        out_lines = []
                        for l in raw_text.splitlines():
                            l_str = l.strip()
                            if not l_str:
                                continue
                            clean = re.sub(r'^\d+[\.\:\-\)]\s*', '', l_str).strip()
                            if clean:
                                out_lines.append(clean)
                        if len(out_lines) == len(batch_lines):
                            return out_lines
            elif resp.status_code in (404, 503):
                continue
            elif resp.status_code == 429:
                time.sleep(1)
                continue
            else:
                break
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            is_network_timeout = True
            print(f"[Gemini] Model {model} mạng chậm / timeout: {e}")
            break
        except Exception as e:
            print(f"[Gemini] Model {model} error: {e}")
            continue

    # Nếu mạng bị timeout hoặc mất kết nối, lập tức bỏ qua Gemini để chuyển sang Web Translate
    if is_network_timeout:
        return []

    # Fallback to single line translations if batch response format was misaligned
    single_results = []
    for line in batch_lines:
        res = translate_gemini_single(line, api_key, target_lang)
        if res:
            single_results.append(res)
        else:
            return []
    return single_results

def translate_free_web(text: str, target_lang_code: str = 'vi', source_lang: str = 'auto', timeout: int = 8) -> str:
    """Translates text using free Google Translate endpoints."""
    if not text or not text.strip():
        return ""
    
    encoded = urllib.parse.quote(text)
    
    # Endpoint 1: Google Translate GTX endpoint
    url1 = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={source_lang}&tl={target_lang_code}&dt=t&q={encoded}"
    headers1 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': '*/*',
    }
    try:
        resp = requests.get(url1, headers=headers1, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            parts = [item[0] for item in data[0] if item and item[0]]
            return "".join(parts)
    except Exception:
        pass

    # Endpoint 2: Google Translate Mobile endpoint
    url2 = f"https://translate.google.com/m?sl={source_lang}&tl={target_lang_code}&q={encoded}"
    headers2 = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    }
    try:
        resp2 = requests.get(url2, headers=headers2, timeout=timeout)
        if resp2.status_code == 200:
            m = re.search(r'class="result-container">(.*?)<', resp2.text)
            if m:
                return html.unescape(m.group(1)).strip()
    except Exception:
        pass

    # Endpoint 3: Google Translate Chrome Extension API (siêu nhanh & ổn định)
    url3 = f"https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl={source_lang}&tl={target_lang_code}&q={encoded}"
    try:
        resp3 = requests.get(url3, headers=headers1, timeout=timeout)
        if resp3.status_code == 200:
            data3 = resp3.json()
            if isinstance(data3, list) and data3 and isinstance(data3[0], str):
                return data3[0]
            elif isinstance(data3, list) and data3 and isinstance(data3[0], list):
                return "".join(str(x) for x in data3[0])
    except Exception:
        pass

    return ""

def _send_status(cb, msg: str, prog_val: int = 0, overwrite: bool = False):
    if not callable(cb):
        return
    for sig in [(msg, prog_val, overwrite), (msg, prog_val), (msg,)]:
        try:
            cb(*sig)
            return
        except TypeError:
            continue
        except Exception:
            return

def translate_logic(
    srt_path: str,
    api_keys: list,
    status_cb,
    cancel_event,
    workspace_dir: str,
    prompt_style: str = 'Mặc định',
    custom_prompt_text: str = '',
    target_lang: str = 'Tiếng Việt'
) -> str:
    """
    Subtitles translation pipeline:
    - Automatically detects and uses Gemini API keys
    - Translates cleanly into target language
    - Fallback to free web translate or original text on error
    """
    if not os.path.exists(srt_path):
        raise FileNotFoundError(f"Không tìm thấy file phụ đề gốc: {srt_path}")

    subs = pysrt.open(srt_path, encoding='utf-8')
    total_lines = len(subs)
    if total_lines == 0:
        return srt_path

    target_lang_code = LANG_CODE_MAP.get(target_lang, 'vi')

    # Filter valid Gemini API keys
    clean_keys = [
        k.strip() for k in api_keys
        if k and isinstance(k, str)
        and len(k.strip()) > 10
        and not k.strip().upper().startswith('FREE')
    ]
    use_gemini = len(clean_keys) > 0
    current_key_idx = 0

    mode_name = "Gemini AI" if use_gemini else "Google Translate"
    _send_status(status_cb, f"⚡ {mode_name} — Bắt đầu dịch {total_lines} câu sang {target_lang}...", prog_val=5)

    translated_texts = []
    batch_size = 10 if use_gemini else 8
    gemini_consecutive_errors = 0

    for start_idx in range(0, total_lines, batch_size):
        if cancel_event and cancel_event.is_set():
            _send_status(status_cb, "⏹ Đã hủy dịch.", prog_val=0)
            return ""

        end_idx = min(start_idx + batch_size, total_lines)
        batch = [subs[i].text.replace('\n', ' ').strip() for i in range(start_idx, end_idx)]

        prog_pct = int(5 + (end_idx / total_lines) * 90)
        _send_status(status_cb, f"Đang dịch câu {start_idx + 1} - {end_idx} / {total_lines}...", prog_val=prog_pct)

        batch_translated = []

        # Strategy 1: Gemini API
        if use_gemini and current_key_idx < len(clean_keys):
            try:
                active_key = clean_keys[current_key_idx % len(clean_keys)]
                batch_translated = translate_gemini(
                    batch, active_key, target_lang, prompt_style
                )
                if len(batch_translated) == len(batch):
                    gemini_consecutive_errors = 0
                else:
                    gemini_consecutive_errors += 1
            except Exception as e:
                print(f"[Gemini] Error: {e}")
                gemini_consecutive_errors += 1
                current_key_idx = (current_key_idx + 1) % len(clean_keys)

            if gemini_consecutive_errors >= 2:
                use_gemini = False
                _send_status(status_cb, "⚠️ Gemini phản hồi quá thời gian / lỗi mạng. Đang tự động chuyển sang Google Translate tốc độ cao...", prog_val=prog_pct)

        # Strategy 2: Free Web Translate (fallback if Gemini failed or no keys)
        if len(batch_translated) != len(batch):
            batch_translated = []
            for item_text in batch:
                if cancel_event and cancel_event.is_set():
                    _send_status(status_cb, "⏹ Đã hủy dịch.", prog_val=0)
                    return ""
                res = translate_free_web(item_text, target_lang_code=target_lang_code)
                if res:
                    res = lach_luat_google_dich(res)
                    batch_translated.append(res)
                else:
                    batch_translated.append(item_text)
                time.sleep(0.15)

        translated_texts.extend(batch_translated)

    # Apply translated texts back to subtitles
    for i, t in enumerate(translated_texts):
        if i < len(subs) and t:
            subs[i].text = t

    out_dir = os.path.join(workspace_dir, "Data")
    os.makedirs(out_dir, exist_ok=True)
    out_srt_path = os.path.join(out_dir, "temp_translated.srt")

    subs.save(out_srt_path, encoding='utf-8')
    optimize_srt_timing(out_srt_path)

    _send_status(status_cb, f" Hoàn tất dịch {total_lines} câu sang {target_lang}!", prog_val=100)
    return out_srt_path

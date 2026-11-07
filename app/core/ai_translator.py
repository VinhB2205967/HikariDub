"""
AI Translator Module - Hikari Tsukimi v3.4
Supports:
1. Google Gemini / Argon API via REST (AI Studio v1beta & Vertex AI Express v1/v1beta1)
   - Optimized for Gemini 2.5 Flash (thinkingBudget=0 for fast 1.5s response, thought-part filtering, partial batch recovery to respect 5 RPM quota)
2. Full-Context Dubbing Screenwriter Prompt System (Mặc định, Đời thường, Tấu hài, Review, Nghiêm túc, Cổ trang, Tùy chỉnh)
3. Smart Chinese Colloquial & Idiom Localization + Post-Translation Vietnamese Dubbing Polisher
"""

import os
import re
import time
import json
import urllib.parse
import html
import pysrt
import requests
from typing import List, Optional, Tuple

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

# Sensitive word softener (only for severe platform-violation terms, preserving dramatic/comedic expressions)
SENSITIVE_REPLACEMENTS = {
    r'\bgiết người\b': 'hành hung',
    r'\btự tử\b': 'nghĩ quẩn',
    r'\bmáu me\b': 'vết thương',
}

# Regex to strip accidental trailing language tags from web translators (e.g. "Nói hay khôngzh-CN")
_TRAILING_LANG_TAG_RE = re.compile(
    r'(?:zh-CN|zh-TW|zh-HK|zh-Hans|zh-Hant|en-US|en-GB|ja-JP|ko-KR|vi-VN)\s*$',
    flags=re.IGNORECASE,
)

def strip_stray_lang_tags(text: str) -> str:
    if not text:
        return ""
    return _TRAILING_LANG_TAG_RE.sub('', text).strip()

def lach_luat_google_dich(text: str) -> str:
    if not text:
        return text
    result = strip_stray_lang_tags(text)
    for pattern, replacement in SENSITIVE_REPLACEMENTS.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    return result

def is_untranslated(orig_text: str, trans_text: str, target_lang: str = 'Tiếng Việt') -> bool:
    if not orig_text or not trans_text:
        return False
    o = orig_text.strip().lower()
    t = strip_stray_lang_tags(trans_text).lower()
    if o == t and len(o) > 2:
        if target_lang == 'Tiếng Việt':
            vi_chars = set('àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ')
            if not any(c in vi_chars for c in t):
                return True
    if target_lang == 'Tiếng Việt' and re.search(r'[\u4e00-\u9fff]', t):
        return True
    return False

def optimize_srt_timing(srt_path: str):
    """
    Optimizes subtitle timing so lines don't overlap.
    """
    try:
        subs = pysrt.open(srt_path, encoding='utf-8')
        n = len(subs)
        if n == 0:
            return
        for i in range(n - 1):
            if subs[i].end.ordinal > subs[i + 1].start.ordinal:
                subs[i].end = subs[i + 1].start
        subs.save(srt_path, encoding='utf-8')
    except Exception as e:
        print(f"Lỗi optimize_srt_timing: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# Rich Dubbing Style Instructions (Phong cách Dịch)
# ─────────────────────────────────────────────────────────────────────────────
DUBBING_STYLE_INSTRUCTIONS = {
    'Mặc định': (
        "PHONG CÁCH: Đời thường, Tự nhiên, Chuẩn Lồng Tiếng (Khuyên dùng).\n"
        "- Dịch thoát ý tự nhiên như người Việt nói chuyện ngoài đời thực, câu văn gãy gọn, giàu cảm xúc.\n"
        "- Tuyệt đối KHÔNG dịch word-by-word kiểu Google Dịch (VD: KHÔNG dịch 'Bạn có ý gì, bạn hỏi?', 'Chỉ cần hỏi tôi nếu tôi muốn nói với bạn', 'Bạn không hỏi à?').\n"
        "- Tuyệt đối KHÔNG dùng đại từ 'Bạn' cứng nhắc trong hội thoại phim/clip ngắn; hãy dùng 'Anh / Tôi', 'Ông / Tôi', hoặc 'Mày / Tao' tùy tình huống.\n"
        "- Dùng đúng các từ cảm thán tự nhiên trong tiếng Việt: 'thôi mà!', 'luôn rồi!', 'ghê!', 'cái nỗi gì chứ!', 'thì bảo!', 'mới được chứ!'."
    ),
    'Đời thường': (
        "PHONG CÁCH: Hội thoại Đời thường & Viral TikTok/Douyin.\n"
        "- Lời thoại tự nhiên, sống động, bắt đúng tâm lý nhân vật đang bực bội, bất lực, tra hỏi, ngạc nhiên hay hài hước.\n"
        "- Chuyển ngữ mượt mà các thành ngữ/khẩu ngữ tiếng Trung sang đúng câu cửa miệng tiếng Việt tương đương."
    ),
    'Tấu hài': (
        "PHONG CÁCH: Tấu hài, Cà khịa, Lầy lội (Viral TikTok / Hài Douyin).\n"
        "- Dịch giọng điệu hài hước, lầy lội, nhấn mạnh sự bất lực hoặc cà khịa duyên dáng.\n"
        "- Ưu tiên các cách nói cửa miệng cực cuốn như: 'Có khai không thì bảo?!', 'Đánh tôi suốt ba ngày ba đêm, chỉ hỏi mỗi câu có nói hay không!', 'Mà nói cái gì mới được?!', 'Ủa anh chưa hỏi à?!', 'Hỏi cái gì cơ?!', 'Đã bảo... thôi mà!', 'Giờ thì hay rồi!', 'Tôi chịu hết nổi rồi!'."
    ),
    'Review': (
        "PHONG CÁCH: Kể chuyện / Review Phim (Kịch tính, Lôi cuốn).\n"
        "- Câu văn nhịp nhanh, súc tích, giàu tính gợi hình và cuốn hút người xem từ giây đầu tiên."
    ),
    'Nghiêm túc': (
        "PHONG CÁCH: Điện ảnh / Chính kịch (Nghiêm túc, Chuẩn xác).\n"
        "- Ngôn từ điện ảnh chỉn chu, tự nhiên, giữ trọn vẹn sắc thái cảm xúc và chiều sâu của lời thoại gốc."
    ),
    'Cổ trang': (
        "PHONG CÁCH: Cổ trang / Tiên hiệp / Kiếm hiệp.\n"
        "- Dùng từ vựng Hán Việt và đại từ xưng hô cổ trang chuẩn mực (Ta - Ngươi, Huynh - Đệ, Tại hạ, Các hạ, Bản tọa, Đạo hữu)."
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
# Chinese Colloquial & Idiom Localization Engine (Pre & Post Translation)
# ─────────────────────────────────────────────────────────────────────────────
_ZH_EXACT_OR_PATTERN_RULES: List[Tuple[re.Pattern, str]] = [
    # Interrogation / Comedy skit patterns ("说不说 / 打了我三天三夜 / 就问我说不说")
    (re.compile(r'^(你)?到底说不说[！!？?。，,\s]*$'), 'Rốt cuộc có khai không thì bảo?!'),
    (re.compile(r'^说不说[！!？?。，,\s]*$'), 'Có nói không thì bảo?!'),
    (re.compile(r'^你不说(，|,|\s)*我也不说[！!？?。，,\s]*$'), 'Anh không nói thì tôi cũng chẳng nói!'),
    (re.compile(r'^什么意思[？?，,\s]*你问(吧|啊|呀)[！!？?。，,\s]*$'), 'Ý gì đây? Có gì thì hỏi đi!'),
    (re.compile(r'^打了我三天三夜[！!？?。，,\s]*$'), 'Đánh tôi suốt ba ngày ba đêm,'),
    (re.compile(r'^就问我说不说[！!？?。，,\s]*$'), 'Chỉ hỏi mỗi câu là có nói hay không!'),
    (re.compile(r'^说什么(呀|啊|呢)?[！!？?。，,\s]*$'), 'Mà nói cái gì chứ?!'),
    (re.compile(r'^你(难道)?没问(他|她|我)?吗[！!？?。，,\s]*$'), 'Ủa, anh chưa hỏi à?!'),
    (re.compile(r'^你倒是问(啊|呀|吧)[！!？?。，,\s]*$'), 'Thì anh phải hỏi đi chứ!'),
    (re.compile(r'^问什么(呀|啊|呢)?[！!？?。，,\s]*$'), 'Hỏi cái gì cơ?!'),

    # Smart car / AI comedy skit patterns
    (re.compile(r'^我就说买车买低配的[！!。，,\s]*$'), 'Đã bảo mua xe bản tiêu chuẩn thôi mà!'),
    (re.compile(r'^我就说买低配的[！!。，,\s]*$'), 'Đã bảo mua bản tiêu chuẩn thôi mà!'),
    (re.compile(r'^你就是不听[！!。，,\s]*$'), 'Anh cứ nhất quyết không nghe!'),
    (re.compile(r'^这下好了(吧|呀|啊)?[！!。，,\s]*$'), 'Giờ thì hay rồi!'),
    (re.compile(r'^要成为[他它她]的智能饭盒了吧[！!。，,\s]*$'), 'Sắp thành hộp cơm thông minh của nó luôn rồi!'),
    (re.compile(r'^(我)?真服了这玩意(儿)?[！!。，,\s]*$'), 'Tôi cũng chịu cái thứ này luôn!'),
    (re.compile(r'^想跟别人展示的时候打不开[！!。，,\s]*$'), 'Đến lúc muốn khoe với người ta thì nó lại không mở!'),
    (re.compile(r'^偏偏这时候相当灵敏[！!。，,\s]*$'), 'Thế mà đúng lúc này lại nhạy bén ghê!'),
    (re.compile(r'^这哪(里)?是人工智能(啊|呀|呢)?[！!？?。，,\s]*$'), 'AI cái nỗi gì chứ!'),
    (re.compile(r'^分明是人工智障(啊|呀|吧)?[！!。，,\s]*$'), 'Rõ ràng là trí tuệ nhân tạo bị thiểu năng!'),
    (re.compile(r'^等我过了这(一)?关[！!。，,\s]*$'), 'Đợi tôi qua được cửa ải này đã!'),
    (re.compile(r'^非把这(辆)?车砸了不可[！!。，,\s]*$'), 'Tôi nhất định đập nát cái xe này!'),
    (re.compile(r'^(我)?(真是|真)?服了(了)?[！!。，,\s]*$'), 'Tôi chịu hết nổi rồi!'),
    (re.compile(r'^(我)?真服了你(了)?[！!。，,\s]*$'), 'Tôi cũng đến chịu anh luôn rồi!'),
    (re.compile(r'^搞什么鬼(啊|呀)?[！!？?。，,\s]*$'), 'Làm cái trò quái gì thế này!'),
    (re.compile(r'^开什么玩笑[！!？?。，,\s]*$'), 'Đùa nhau đấy à!'),
    (re.compile(r'^真是无语(了)?[！!。，,\s]*$'), 'Đúng là cạn lời thật sự!'),
]

_ZH_COLLOQUIAL_GLOSSARY = [
    ('就问我说不说', 'chỉ hỏi mỗi câu là có nói hay không'),
    ('打了我三天三夜', 'Đánh tôi suốt ba ngày ba đêm'),
    ('三天三夜', 'suốt ba ngày ba đêm'),
    ('什么意思你问吧', 'Ý gì đây, có gì thì hỏi đi'),
    ('你不说我也不说', 'Anh không nói thì tôi cũng chẳng nói'),
    ('买车买低配的', 'mua xe bản tiêu chuẩn thôi mà'),
    ('买低配的', 'mua bản tiêu chuẩn'),
    ('低配版', 'bản tiêu chuẩn'),
    ('低配', 'bản tiêu chuẩn'),
    ('高配版', 'bản cao cấp'),
    ('高配', 'bản cao cấp'),
    ('顶配', 'bản full option'),
    ('智能饭盒', 'hộp cơm thông minh'),
    ('人工智障', 'trí tuệ nhân tạo bị thiểu năng'),
    ('这下好了', 'Giờ thì hay rồi'),
    ('我真服了这玩意', 'Tôi cũng chịu cái thứ này luôn'),
    ('真服了这玩意', 'Chịu cái thứ này luôn'),
    ('这玩意儿', 'cái thứ này'),
    ('这玩意', 'cái thứ này'),
    ('偏偏这时候', 'Thế mà đúng lúc này lại'),
    ('相当灵敏', 'nhạy bén ghê'),
    ('过了这关', 'qua được cửa ải này đã'),
    ('过了这一关', 'qua được cửa ải này đã'),
]

def match_chinese_colloquial_exact(orig_text: str) -> Optional[str]:
    if not orig_text:
        return None
    s = orig_text.strip()
    for pat, repl in _ZH_EXACT_OR_PATTERN_RULES:
        if pat.match(s):
            return repl
    return None

def preprocess_chinese_for_web_translate(orig_text: str) -> str:
    if not orig_text or not re.search(r'[\u4e00-\u9fff]', orig_text):
        return orig_text
    s = orig_text.strip()
    exact = match_chinese_colloquial_exact(s)
    if exact:
        return exact

    s = re.sub(r'^就问我(.+?)不\1[！!？?。，,\s]*$', r'Chỉ hỏi tôi mỗi câu có \1 hay không!', s)
    s = re.sub(r'^就问我(.+?)$', r'Chỉ hỏi tôi là \1', s)
    s = re.sub(r'^什么意思[？?，,\s]*你(.+?)吧[！!？?。，,\s]*$', r'Ý gì đây, anh cứ \1 đi!', s)
    s = re.sub(r'^我就说(.+?)$', r'Đã bảo là \1 thôi mà!', s)
    s = re.sub(r'^你就是不(.+?)$', r'Anh cứ nhất quyết không \1!', s)
    s = re.sub(r'^这哪(里)?是(.+?)[啊呀呢]?$', r'\2 cái nỗi gì chứ!', s)
    s = re.sub(r'^分明是(.+?)[啊呀吧]?$', r'Rõ ràng là \1!', s)
    s = re.sub(r'^非把(.+?)不可$', r'Tôi nhất định phải đem \1!', s)
    s = re.sub(r'^等我过了这(一)?关$', r'Đợi tôi qua được cửa ải này đã!', s)

    for zh_term, vi_term in _ZH_COLLOQUIAL_GLOSSARY:
        if zh_term in s:
            s = s.replace(zh_term, f" {vi_term} ")
    return s

def polish_vietnamese_dubbing(orig_text: str, trans_text: str, prompt_style: str = 'Mặc định') -> str:
    if not trans_text:
        return trans_text

    t = strip_stray_lang_tags(trans_text)
    orig = strip_stray_lang_tags(orig_text or '')

    exact = match_chinese_colloquial_exact(orig)
    if exact:
        return exact

    t_lower = t.lower().strip(' .!?')
    if t_lower in ('nói hay không', 'có nói hay không'):
        return 'Có nói không thì bảo?!'
    if t_lower in ('anh không nói thì em cũng không nói', 'bạn không nói thì tôi cũng không nói'):
        return 'Anh không nói thì tôi cũng chẳng nói!'
    if t_lower in ('bạn có ý gì, bạn hỏi', 'ý bạn là gì, bạn hỏi', 'bạn có ý gì, hãy hỏi'):
        return 'Ý gì đây? Có gì thì hỏi đi!'
    if t_lower in ('đánh tôi ba ngày ba đêm', 'đánh đập tôi ba ngày ba đêm'):
        return 'Đánh tôi suốt ba ngày ba đêm,'
    if 'chỉ cần hỏi tôi nếu tôi muốn nói' in t_lower or '就问我说不说' in orig:
        return 'Chỉ hỏi mỗi câu là có nói hay không!'
    if t_lower in ('nói cái gì', 'nói gì'):
        return 'Mà nói cái gì chứ?!'
    if t_lower in ('bạn không hỏi à', 'bạn đã không hỏi à', 'anh không hỏi à'):
        return 'Ủa, anh chưa hỏi à?!'
    if t_lower in ('hỏi gì', 'hỏi cái gì'):
        return 'Hỏi cái gì cơ?!'

    if '服了' in orig:
        if '玩意' in orig:
            return 'Tôi cũng chịu cái thứ này luôn!'
        if re.search(r'\b(thuyết phục|thích điều này|khâm phục)\b', t, flags=re.IGNORECASE):
            return 'Tôi chịu hết nổi rồi!'

    if '这下好了' in orig and re.search(r'\b(tốt hơn rồi|tốt rồi)\b', t, flags=re.IGNORECASE):
        return 'Giờ thì hay rồi!'

    if '低配' in orig:
        t = re.sub(r'\b(xe\s+)?cấp thấp\b', 'xe bản tiêu chuẩn', t, flags=re.IGNORECASE)
        t = re.sub(r'^Tôi chỉ nói rằng khi mua xe hãy mua\s*', 'Đã bảo mua ', t, flags=re.IGNORECASE)

    if '你就是不听' in orig or re.match(r'^Bạn chỉ không lắng nghe\.?$', t, flags=re.IGNORECASE):
        return 'Anh cứ nhất quyết không nghe!'

    if '智能饭盒' in orig:
        t = re.sub(r'hộp cơm trưa thông minh', 'hộp cơm thông minh', t, flags=re.IGNORECASE)
        if '要成为' in orig:
            return 'Sắp thành hộp cơm thông minh của nó luôn rồi!'

    if '展示' in orig and '打不开' in orig:
        return 'Đến lúc muốn khoe với người ta thì nó lại không mở!'

    if '偏偏' in orig and '灵敏' in orig:
        return 'Thế mà đúng lúc này lại nhạy bén ghê!'

    if '哪是' in orig and '人工智能' in orig:
        return 'AI cái nỗi gì chứ!'

    if '人工智障' in orig or 'chậm phát triển nhân tạo' in t_lower:
        return 'Rõ ràng là trí tuệ nhân tạo bị thiểu năng!'

    if '过了这关' in orig or 'vượt qua cấp độ này' in t_lower:
        return 'Đợi tôi qua được cửa ải này đã!'

    if '非把' in orig and '砸了' in orig:
        return 'Tôi nhất định đập nát cái xe này!'

    t = re.sub(r'^Tôi chỉ nói rằng\s+', 'Đã bảo là ', t, flags=re.IGNORECASE)
    t = re.sub(r'^Bạn chỉ không\s+', 'Anh cứ nhất quyết không ', t, flags=re.IGNORECASE)
    t = re.sub(r'^Bạn có ý gì,\s*bạn hỏi\??', 'Ý gì đây? Có gì thì hỏi đi!', t, flags=re.IGNORECASE)
    t = re.sub(r'^Chỉ cần hỏi tôi nếu tôi muốn nói với bạn\.?', 'Chỉ hỏi mỗi câu là có nói hay không!', t, flags=re.IGNORECASE)
    t = re.sub(r'\bhộp cơm trưa thông minh\b', 'hộp cơm thông minh', t, flags=re.IGNORECASE)
    t = re.sub(r'\bchậm phát triển nhân tạo\b', 'trí tuệ nhân tạo bị thiểu năng', t, flags=re.IGNORECASE)
    t = re.sub(r'\bTôi thực sự bị thuyết phục\.?$', 'Tôi chịu hết nổi rồi!', t, flags=re.IGNORECASE)

    if prompt_style != 'Cổ trang':
        t = re.sub(r'^Bạn\s+', 'Anh ', t)
        t = re.sub(r'\bbạn\b', 'anh', t)

    t = re.sub(r'\s+', ' ', t).strip()
    if t and t[0].islower():
        t = t[0].upper() + t[1:]

    return t


def harmonize_vietnamese_dialogue_batch(orig_lines: List[str], trans_lines: List[str], prompt_style: str = 'Mặc định') -> List[str]:
    polished = [
        polish_vietnamese_dubbing(orig, trans, prompt_style)
        for orig, trans in zip(orig_lines, trans_lines)
    ]
    for i in range(1, len(polished)):
        if orig_lines[i].strip() == orig_lines[i - 1].strip() and orig_lines[i].strip().startswith('说不说'):
            polished[i - 1] = 'Khai hay không?!'
            polished[i] = 'Có nói không thì bảo?!'
    return polished


# ─────────────────────────────────────────────────────────────────────────────
# Supported Gemini & Argon models (real Google AI Studio model IDs)
# ─────────────────────────────────────────────────────────────────────────────
ARGON_MODEL_ID = 'gemini-4-argon'

GEMINI_MODELS = [
    ARGON_MODEL_ID,            # Gemini 4 Argon (cần bật thanh toán – Free tier limit = 0)
    'gemini-3.5-flash',        # Nhanh (~2s), dịch hay, có Free tier
    'gemini-3.5-flash-lite',   # Siêu tốc (~1s)
    'gemini-flash-latest',     # Alias luôn trỏ tới bản Flash mới nhất
    'gemini-2.5-flash',        # Tương thích ngược
]

# Legacy config values -> real model IDs
_MODEL_ALIASES = {
    'argon': ARGON_MODEL_ID,
    'gemini-argon': ARGON_MODEL_ID,
    'gemini-4-argon': ARGON_MODEL_ID,
    'gemini-2.0-flash': 'gemini-3.5-flash',        # 2.0 đã bị Google ngừng
    'gemini-2.0-flash-lite': 'gemini-3.5-flash-lite',
    'gemini-1.5-flash': 'gemini-flash-latest',
}

MODEL_DISPLAY_NAMES = {
    'argon': 'Gemini 4 Argon',
    ARGON_MODEL_ID: 'Gemini 4 Argon',
    'gemini-3.5-flash': 'Gemini 3.5 Flash',
    'gemini-3.5-flash-lite': 'Gemini 3.5 Flash Lite',
    'gemini-flash-latest': 'Gemini Flash Latest',
    'gemini-2.5-flash': 'Gemini 2.5 Flash',
    'auto': 'Auto (Đa mô hình)',
}

_SAFETY_SETTINGS_BLOCK_NONE = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

_AISTUDIO_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
_VERTEX_URL = "https://aiplatform.googleapis.com/v1/publishers/google/models/{model}:generateContent"

# Persistent HTTP session (keep-alive -> no TLS handshake on every request)
_HTTP = requests.Session()
_HTTP.headers.update({'Content-Type': 'application/json'})

# (key, model) pairs known to be unusable this session (quota limit 0 / 404 / 403) -> skipped instantly
_DEAD_COMBOS: dict = {}
# Last (key -> model) that succeeded, tried first next time
_LAST_GOOD_MODEL: dict = {}


def resolve_model_id(model: str) -> str:
    m = (model or '').strip()
    return _MODEL_ALIASES.get(m.lower(), m)


def get_active_gemini_models() -> List[str]:
    """Returns prioritized list of real Google API model IDs based on user selection."""
    selected = 'argon'
    try:
        from app.common.config_manager import get_config
        selected = (get_config('gemini_model', 'argon') or 'argon').strip()
    except Exception:
        pass

    fallback_chain = ['gemini-3.5-flash', 'gemini-3.5-flash-lite', 'gemini-flash-latest', 'gemini-2.5-flash']
    if not selected or selected == 'auto':
        return [ARGON_MODEL_ID] + fallback_chain

    primary = resolve_model_id(selected)
    return [primary] + [m for m in fallback_chain if m != primary]


def _generation_config(model: str, level: int) -> dict:
    """level 0: fastest thinking settings; level 1: plain config (if model rejects thinking params)."""
    cfg = {'temperature': 0.3}
    if level == 0:
        if model.startswith('gemini-2.5'):
            cfg['thinkingConfig'] = {'thinkingBudget': 0}
        elif 'flash' in model or 'argon' in model:
            cfg['thinkingConfig'] = {'thinkingLevel': 'low'}
    return cfg


def _describe_api_error(resp) -> str:
    try:
        msg = resp.json().get('error', {}).get('message', '')
    except Exception:
        msg = resp.text or ''
    return msg.strip().splitlines()[0][:160] if msg else f"HTTP {resp.status_code}"


def _gemini_generate(api_key: str, prompt: str, timeout_read: int = 30, status_cb=None) -> Tuple[str, str]:
    """
    Calls Gemini generateContent as fast as possible:
    - AI Studio endpoint first (works with both AIza... and AQ.... keys), Vertex only on 401/403
    - Skips (key, model) combos already known dead (quota limit 0, 404, ...)
    - 429/503 -> move to next model immediately (no sleeping)
    Returns (text, model_used) or ("", "").
    """
    key_s = (api_key or '').strip()
    if not key_s:
        return "", ""

    models = get_active_gemini_models()
    last_good = _LAST_GOOD_MODEL.get(key_s)
    if last_good in models:
        models = [last_good] + [m for m in models if m != last_good]

    for model in models:
        if _DEAD_COMBOS.get((key_s, model)):
            continue
        for base_url in (_AISTUDIO_URL, _VERTEX_URL):
            url = base_url.format(model=model)
            moved_on = False
            for level in (0, 1):
                payload = {
                    'contents': [{'role': 'user', 'parts': [{'text': prompt}]}],
                    'safetySettings': _SAFETY_SETTINGS_BLOCK_NONE,
                    'generationConfig': _generation_config(model, level),
                }
                try:
                    resp = _HTTP.post(url, json=payload, headers={'x-goog-api-key': key_s},
                                      timeout=(5, timeout_read))
                except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                    print(f"[Gemini] {model} timeout/kết nối lỗi: {e}")
                    moved_on = True
                    break

                if resp.status_code == 200:
                    text = _extract_gemini_text(resp.json().get('candidates', []))
                    if text:
                        _LAST_GOOD_MODEL[key_s] = model
                        return text, model
                    moved_on = True
                    break

                if resp.status_code == 400 and level == 0:
                    continue  # retry without thinking params

                err = _describe_api_error(resp)
                if resp.status_code == 429:
                    body = resp.text or ''
                    if 'limit: 0' in body or 'PerDay' in body:
                        _DEAD_COMBOS[(key_s, model)] = True
                        note = "hết hạn mức (Free tier = 0 / hết lượt ngày)"
                    else:
                        note = "chạm giới hạn RPM"
                    _send_status(status_cb, f"⚠️ {MODEL_DISPLAY_NAMES.get(model, model)} {note} → chuyển model kế tiếp...")
                    moved_on = True
                    break
                if resp.status_code in (404,):
                    _DEAD_COMBOS[(key_s, model)] = True
                    moved_on = True
                    break
                if resp.status_code in (401, 403) and base_url == _AISTUDIO_URL:
                    break  # try Vertex endpoint for this model
                if resp.status_code in (401, 403):
                    _DEAD_COMBOS[(key_s, model)] = True
                print(f"[Gemini] {model} lỗi {resp.status_code}: {err}")
                moved_on = True
                break
            if moved_on:
                break
    return "", ""


def _build_gemini_endpoints(model: str, api_key: str) -> List[Tuple[str, dict]]:
    """Kept for backward compatibility."""
    key_s = api_key.strip()
    h = {'Content-Type': 'application/json', 'x-goog-api-key': key_s}
    return [(_AISTUDIO_URL.format(model=model), h), (_VERTEX_URL.format(model=model), h)]


def _extract_gemini_text(candidates: list) -> str:
    """
    Extracts the response text from Gemini candidates, skipping any internal
    'thought' parts produced by Gemini 2.5 thinking models.
    """
    if not candidates or not isinstance(candidates, list):
        return ""
    content = candidates[0].get('content') or {}
    parts = content.get('parts') or []
    if not parts:
        return ""
    non_thought_texts = [
        p['text'].strip()
        for p in parts
        if isinstance(p, dict) and 'text' in p and not p.get('thought') and p['text'].strip()
    ]
    if non_thought_texts:
        return "\n".join(non_thought_texts)
    # Fallback to last part with text
    for p in reversed(parts):
        if isinstance(p, dict) and p.get('text'):
            return p['text'].strip()
    return ""

def _build_dubbing_batch_prompt(
    batch_lines: List[str],
    target_lang: str = "Tiếng Việt",
    prompt_style: str = "Mặc định",
    custom_prompt_text: str = "",
    batch_durations: Optional[List[float]] = None,
) -> str:
    n_lines = len(batch_lines)
    if prompt_style == 'Tùy chỉnh' and custom_prompt_text and custom_prompt_text.strip():
        style_block = f"YÊU CẦU PHONG CÁCH RIÊNG CỦA NGƯỜI DÙNG:\n{custom_prompt_text.strip()}"
    else:
        style_block = DUBBING_STYLE_INSTRUCTIONS.get(prompt_style, DUBBING_STYLE_INSTRUCTIONS['Mặc định'])

    if target_lang == "Tiếng Việt":
        prompt = (
            f"Bạn là Biên kịch Lồng tiếng Video chuyên nghiệp hàng đầu Việt Nam.\n"
            f"Nhiệm vụ: Dịch {n_lines} câu phụ đề dưới đây sang Tiếng Việt để lồng tiếng.\n\n"
            f"{style_block}\n\n"
            "QUY TẮC SỐNG CÒN:\n"
            f"1. Đưa vào {n_lines} dòng đánh số từ 1 đến {n_lines} -> BẮT BUỘC trả ra đúng {n_lines} dòng đánh số tương ứng (1. ... 2. ...). Ngay cả khi 2 câu gốc giống hệt nhau (VD: câu 1 và câu 2 cùng là '说不说'), vẫn BẮT BUỘC phải in đủ cả dòng 1. và dòng 2., tuyệt đối không gộp dòng!\n"
            "2. Đọc toàn bộ đoạn hội thoại trước khi dịch để hiểu rõ mạch truyện, tình huống, sự tung hứng giữa các nhân vật và thống nhất đại từ xưng hô (VD: Anh - Tôi, Ông - Tôi, Mày - Tao; TUYỆT ĐỐI KHÔNG dùng 'Bạn' máy móc).\n"
            "3. Mỗi câu có nhãn [Xs] là thời lượng nói của câu đó. Hãy chọn cách diễn đạt khẩu ngữ gọn gàng, đắt giá để diễn viên lồng tiếng đọc vừa vặn trong [Xs] mà KHÔNG làm mất ý nghĩa.\n"
            "4. TUYỆT ĐỐI KHÔNG dịch máy móc từng chữ kiểu Google Dịch. Các thành ngữ/khẩu ngữ tiếng Trung phải chuyển sang câu cửa miệng tiếng Việt tự nhiên:\n"
            "   - '说不说 / 说不说' -> 'Khai hay không?! / Có nói không thì bảo?!'\n"
            "   - '你不说我也不说' -> 'Anh không nói thì tôi cũng chẳng nói!'\n"
            "   - '什么意思你问吧' -> 'Ý gì đây? Có gì thì hỏi đi!'\n"
            "   - '打了我三天三夜 / 就问我说不说 / 说什么' -> 'Đánh tôi suốt ba ngày ba đêm, / Chỉ hỏi mỗi câu là có nói hay không! / Mà nói cái gì chứ?!'\n"
            "   - '你没问吗 / 问什么' -> 'Ủa, anh chưa hỏi à?! / Hỏi cái gì cơ?!'\n"
            "   - '我就说买车买低配的' -> 'Đã bảo mua xe bản tiêu chuẩn thôi mà!'\n"
            "   - '你就是不听' -> 'Anh cứ nhất quyết không nghe!'\n"
            "   - '这下好了' -> 'Giờ thì hay rồi!'\n"
            "   - '这哪是人工智能啊 / 分明是人工智障啊' -> 'AI cái nỗi gì chứ! / Rõ ràng là trí tuệ nhân tạo bị thiểu năng!'\n"
            "5. CHỈ in ra danh sách các câu đã dịch (1. ... 2. ...), KHÔNG in lời dẫn, KHÔNG in lại chữ Trung, KHÔNG in lại nhãn [Xs].\n\n"
            f"DỮ LIỆU GỐC ({n_lines} CÂU):\n"
        )
    else:
        prompt = (
            f"You are a professional dubbing scriptwriter. Translate these {n_lines} subtitle lines into natural, idiomatic spoken {target_lang}.\n"
            f"Style: {style_block}\n"
            "Rules:\n"
            f"- Output exactly {n_lines} numbered lines (1. ... 2. ...). Never merge duplicate lines.\n"
            "- Match the speaking duration [Xs] naturally without robotic literal translation.\n"
            "- Do NOT repeat the [Xs] tag in the output.\n\n"
        )

    for idx, line in enumerate(batch_lines, 1):
        dur_tag = ""
        if batch_durations and idx - 1 < len(batch_durations):
            dur_tag = f"[{batch_durations[idx - 1]:.1f}s] "
        prompt += f"{idx}. {dur_tag}{line.strip()}\n"

    return prompt

def _parse_numbered_llm_output(
    raw_text: str,
    n_lines: int,
    batch_lines: Optional[List[str]] = None,
    target_lang: str = "Tiếng Việt",
    prompt_style: str = "Mặc định",
) -> List[str]:
    """
    Robustly extracts N translated lines from LLM output.
    Even if the LLM merges an identical line or omits 1-2 numbers, recovers all
    valid numbered lines from the batch response instead of discarding it!
    """
    if not raw_text:
        return []

    indexed_map = {}
    fallback_lines = []
    for l in raw_text.splitlines():
        l_str = l.strip().strip('*`')
        if not l_str:
            continue
        if re.match(r'^(Dưới đây là|Đây là bản dịch|Bản dịch|Here is|Sure|Chắc chắn)', l_str, flags=re.IGNORECASE):
            continue

        m = re.match(r'^(?:Câu\s*|Line\s*)?(\d+)[\.\:\-\)]\s*(.+)$', l_str, flags=re.IGNORECASE)
        if m:
            idx = int(m.group(1))
            val = m.group(2).strip()
            val = re.sub(r'^\[\d+(?:\.\d+)?s\]\s*', '', val).strip(' "“\'”*')
            val = strip_stray_lang_tags(val)
            if 1 <= idx <= n_lines and val:
                indexed_map[idx] = val

        clean = re.sub(r'^(?:Câu\s*|Line\s*)?\d+[\.\:\-\)]\s*', '', l_str, flags=re.IGNORECASE).strip()
        clean = re.sub(r'^\[\d+(?:\.\d+)?s\]\s*', '', clean).strip(' "“\'”*')
        clean = strip_stray_lang_tags(clean)
        if clean:
            fallback_lines.append(clean)

    if len(indexed_map) == n_lines:
        return [indexed_map[i] for i in range(1, n_lines + 1)]
    if len(fallback_lines) == n_lines:
        return fallback_lines

    # Partial recovery: if LLM returned >= 60% of numbered lines (e.g. merged duplicate lines),
    # preserve every line Gemini translated and fill only the missing slots!
    if batch_lines and len(indexed_map) >= max(1, int(n_lines * 0.6)):
        recovered = []
        for i in range(1, n_lines + 1):
            if i in indexed_map:
                recovered.append(indexed_map[i])
            else:
                orig_i = batch_lines[i - 1].strip()
                # Check if an identical source line was already translated in this batch
                found_dup = None
                for j in range(1, n_lines + 1):
                    if j in indexed_map and batch_lines[j - 1].strip() == orig_i:
                        found_dup = indexed_map[j]
                        break
                if found_dup:
                    recovered.append(found_dup)
                else:
                    lang_code = LANG_CODE_MAP.get(target_lang, 'vi')
                    recovered.append(translate_free_web(orig_i, target_lang_code=lang_code, prompt_style=prompt_style) or orig_i)
        return recovered

    return []

def translate_gemini_single(text: str, api_key: str, target_lang: str = "Tiếng Việt", prompt_style: str = "Mặc định") -> str:
    """Translates a single line using Gemini / Argon REST API with dubbing polish."""
    if not text or not text.strip():
        return ""
    if target_lang == "Tiếng Việt":
        exact = match_chinese_colloquial_exact(text)
        if exact:
            return exact

    style_desc = DUBBING_STYLE_INSTRUCTIONS.get(prompt_style, DUBBING_STYLE_INSTRUCTIONS['Mặc định'])
    prompt = (
        f"Bạn là biên kịch lồng tiếng chuyên nghiệp. Hãy dịch câu thoại sau sang {target_lang} "
        f"theo văn phong khẩu ngữ đời thường tự nhiên, giàu cảm xúc, khớp ngữ cảnh nói chuyện.\n"
        f"{style_desc}\n"
        f"CHỈ trả về đúng 1 dòng kết quả đã dịch, không giải thích, không thêm ngoặc kép:\n{text.strip()}"
    )
    ans, _model = _gemini_generate(api_key, prompt, timeout_read=20)
    if not ans:
        return ""
    ans = re.sub(r'^(Bản dịch|Dịch|Translation):\s*', '', ans.strip(), flags=re.IGNORECASE)
    ans = strip_stray_lang_tags(ans.strip(' "“\'”'))
    if target_lang == 'Tiếng Việt':
        ans = polish_vietnamese_dubbing(text, ans, prompt_style)
    return ans

def translate_gemini(
    batch_lines: List[str],
    api_key: str,
    target_lang: str = "Tiếng Việt",
    prompt_style: str = "Mặc định",
    custom_prompt_text: str = "",
    batch_durations: Optional[List[float]] = None,
    status_cb=None,
) -> List[str]:
    """
    Translates a batch of lines using Gemini / Argon REST API with full conversational context.
    Uses a single fast request (keep-alive session, low thinking, dead-model skipping).
    """
    if not batch_lines:
        return []

    n_lines = len(batch_lines)
    prompt = _build_dubbing_batch_prompt(
        batch_lines,
        target_lang=target_lang,
        prompt_style=prompt_style,
        custom_prompt_text=custom_prompt_text,
        batch_durations=batch_durations,
    )

    raw_text, model_used = _gemini_generate(api_key, prompt, timeout_read=40, status_cb=status_cb)
    if not raw_text:
        return []

    out_lines = _parse_numbered_llm_output(
        raw_text,
        n_lines,
        batch_lines=batch_lines,
        target_lang=target_lang,
        prompt_style=prompt_style,
    )
    if len(out_lines) != n_lines:
        print(f"[Gemini] {model_used} trả {len(out_lines)}/{n_lines} dòng, bỏ qua kết quả lô này.")
        return []
    if target_lang == 'Tiếng Việt':
        out_lines = harmonize_vietnamese_dialogue_batch(batch_lines, out_lines, prompt_style)
    _send_status(status_cb, f"✓ Đã dịch {n_lines} câu bằng {MODEL_DISPLAY_NAMES.get(model_used, model_used)}")
    return out_lines



def translate_free_llm_batch(
    batch_lines: List[str],
    target_lang: str = "Tiếng Việt",
    prompt_style: str = "Mặc định",
    custom_prompt_text: str = "",
    batch_durations: Optional[List[float]] = None,
) -> List[str]:
    """
    Secondary AI LLM Dubbing engine when all user API keys are exhausted or invalid.
    """
    if not batch_lines:
        return []

    if target_lang == "Tiếng Việt":
        exact_all = [match_chinese_colloquial_exact(l) for l in batch_lines]
        if all(x is not None for x in exact_all):
            return harmonize_vietnamese_dialogue_batch(batch_lines, [x for x in exact_all if x], prompt_style)

    n_lines = len(batch_lines)
    prompt = _build_dubbing_batch_prompt(
        batch_lines,
        target_lang=target_lang,
        prompt_style=prompt_style,
        custom_prompt_text=custom_prompt_text,
        batch_durations=batch_durations,
    )

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0 Safari/537.36',
    }
    for model_name in ('openai', 'mistral'):
        payload = {
            'model': model_name,
            'messages': [
                {
                    'role': 'system',
                    'content': 'Bạn là biên kịch lồng tiếng chuyên nghiệp. Chỉ trả về đúng danh sách các câu thoại đã dịch được đánh số thứ tự tương ứng, tự nhiên, giàu cảm xúc, không giải thích.',
                },
                {'role': 'user', 'content': prompt},
            ],
            'temperature': 0.3,
        }
        try:
            resp = requests.post(
                'https://text.pollinations.ai/openai',
                headers=headers,
                json=payload,
                timeout=16,
            )
            if resp.status_code == 200:
                data = resp.json()
                choices = data.get('choices', [])
                if choices:
                    raw_text = choices[0].get('message', {}).get('content', '').strip()
                    out_lines = _parse_numbered_llm_output(
                        raw_text,
                        n_lines,
                        batch_lines=batch_lines,
                        target_lang=target_lang,
                        prompt_style=prompt_style,
                    )
                    if len(out_lines) == n_lines:
                        if target_lang == 'Tiếng Việt':
                            out_lines = harmonize_vietnamese_dialogue_batch(batch_lines, out_lines, prompt_style)
                        return out_lines
        except Exception:
            continue

    return []


def translate_free_web_batch(
    batch_lines: List[str],
    target_lang_code: str = 'vi',
    source_lang: str = 'auto',
    timeout: int = 8,
    prompt_style: str = 'Mặc định',
) -> List[str]:
    if not batch_lines:
        return []

    prep_lines = [
        preprocess_chinese_for_web_translate(l) if target_lang_code == 'vi' else l.strip()
        for l in batch_lines
    ]
    joined_query = "\n".join(prep_lines)
    encoded = urllib.parse.quote(joined_query)
    url1 = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={source_lang}&tl={target_lang_code}&dt=t&q={encoded}"
    headers1 = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': '*/*',
    }
    try:
        resp = requests.get(url1, headers=headers1, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and data and isinstance(data[0], list):
                parts = [str(item[0]) for item in data[0] if item and item[0]]
                full_trans = "".join(parts)
                split_lines = [strip_stray_lang_tags(x.strip()) for x in full_trans.split('\n') if x.strip()]
                if len(split_lines) == len(batch_lines):
                    if target_lang_code == 'vi':
                        return harmonize_vietnamese_dialogue_batch(batch_lines, split_lines, prompt_style)
                    return split_lines
    except Exception:
        pass
    return []


def translate_free_web(
    text: str,
    target_lang_code: str = 'vi',
    source_lang: str = 'auto',
    timeout: int = 8,
    prompt_style: str = 'Mặc định',
) -> str:
    if not text or not text.strip():
        return ""

    orig_text = strip_stray_lang_tags(text.strip())
    if target_lang_code == 'vi':
        exact = match_chinese_colloquial_exact(orig_text)
        if exact:
            return exact
        prep_text = preprocess_chinese_for_web_translate(orig_text)
        if not re.search(r'[\u4e00-\u9fff]', prep_text):
            return polish_vietnamese_dubbing(orig_text, prep_text, prompt_style)
    else:
        prep_text = orig_text

    encoded = urllib.parse.quote(prep_text)
    raw_translated = ""

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
            parts = [str(item[0]) for item in data[0] if item and item[0]]
            raw_translated = "".join(parts)
    except Exception:
        pass

    # Endpoint 2: Google Translate Mobile endpoint
    if not raw_translated:
        url2 = f"https://translate.google.com/m?sl={source_lang}&tl={target_lang_code}&q={encoded}"
        headers2 = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        }
        try:
            resp2 = requests.get(url2, headers=headers2, timeout=timeout)
            if resp2.status_code == 200:
                m = re.search(r'class="result-container">(.*?)<', resp2.text)
                if m:
                    raw_translated = html.unescape(m.group(1)).strip()
        except Exception:
            pass

    # Endpoint 3: Google Translate Chrome Extension API (only take element [0], never detected lang [1])
    if not raw_translated:
        url3 = f"https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl={source_lang}&tl={target_lang_code}&q={encoded}"
        try:
            resp3 = requests.get(url3, headers=headers1, timeout=timeout)
            if resp3.status_code == 200:
                data3 = resp3.json()
                if isinstance(data3, list) and data3:
                    if isinstance(data3[0], str):
                        raw_translated = data3[0]
                    elif isinstance(data3[0], list) and data3[0]:
                        parts3 = [str(seg[0]) for seg in data3 if isinstance(seg, list) and seg and seg[0]]
                        raw_translated = "".join(parts3)
        except Exception:
            pass

    raw_translated = strip_stray_lang_tags(raw_translated)
    if raw_translated and target_lang_code == 'vi':
        raw_translated = polish_vietnamese_dubbing(orig_text, raw_translated, prompt_style)

    return raw_translated

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
    - Connects directly to configured Gemini / Argon API keys (with thinkingBudget=0 for fast batch translation & partial recovery so 5 RPM limit is respected)
    - Keeps trying API keys across batches instead of permanently disabling API mode
    """
    if not os.path.exists(srt_path):
        raise FileNotFoundError(f"Không tìm thấy file phụ đề gốc: {srt_path}")

    subs = pysrt.open(srt_path, encoding='utf-8')
    total_lines = len(subs)
    if total_lines == 0:
        return srt_path

    target_lang_code = LANG_CODE_MAP.get(target_lang, 'vi')

    # Also load keys directly from config_manager if caller passed empty or outdated keys
    if not api_keys or api_keys == ["FREE_MODE"]:
        try:
            from app.common.config_manager import get_config
            cfg_keys = get_config('gemini_keys', [])
            if cfg_keys:
                api_keys = cfg_keys
        except Exception:
            pass

    clean_keys = [
        k.strip() for k in (api_keys or [])
        if k and isinstance(k, str)
        and len(k.strip()) > 10
        and not k.strip().upper().startswith('FREE')
    ]
    use_gemini = len(clean_keys) > 0
    current_key_idx = 0

    selected_m = 'argon'
    try:
        from app.common.config_manager import get_config
        selected_m = (get_config('gemini_model', 'argon') or 'argon').strip()
    except Exception:
        pass
    model_disp = MODEL_DISPLAY_NAMES.get(selected_m, selected_m)
    mode_name = f"Kết nối API ({model_disp}) · Phong cách: {prompt_style}" if use_gemini else f"AI Dubbing ({prompt_style})"
    _send_status(status_cb, f"⚡ {mode_name} — Đang dịch {total_lines} câu sang {target_lang}...", prog_val=5)

    translated_texts = []
    # Use batch_size=35 so short/medium videos (9-35 lines) are translated in a SINGLE API request (respecting 5 RPM limit!)
    batch_size = 35

    for start_idx in range(0, total_lines, batch_size):
        if cancel_event and cancel_event.is_set():
            _send_status(status_cb, "⏹ Đã hủy dịch.", prog_val=0)
            return ""

        end_idx = min(start_idx + batch_size, total_lines)
        batch = [strip_stray_lang_tags(subs[i].text.replace('\n', ' ').strip()) for i in range(start_idx, end_idx)]
        batch_durations = [
            max(0.5, (subs[i].end.ordinal - subs[i].start.ordinal) / 1000.0)
            for i in range(start_idx, end_idx)
        ]

        prog_pct = int(5 + (end_idx / total_lines) * 90)
        _send_status(status_cb, f"🔗 Đang kết nối API ({model_disp}) dịch câu {start_idx + 1} - {end_idx} / {total_lines}...", prog_val=prog_pct)

        batch_translated = []

        # Primary: Direct API connection (Gemini / Argon API keys)
        if use_gemini and clean_keys:
            for _attempt in range(len(clean_keys)):
                try:
                    active_key = clean_keys[current_key_idx % len(clean_keys)]
                    batch_translated = translate_gemini(
                        batch,
                        active_key,
                        target_lang=target_lang,
                        prompt_style=prompt_style,
                        custom_prompt_text=custom_prompt_text,
                        batch_durations=batch_durations,
                        status_cb=status_cb,
                    )
                    if len(batch_translated) == len(batch):
                        break
                    else:
                        current_key_idx = (current_key_idx + 1) % len(clean_keys)
                except Exception as e:
                    print(f"[API] Error: {e}")
                    current_key_idx = (current_key_idx + 1) % len(clean_keys)

        # Secondary API endpoint if primary key quota (20 RPD) is temporarily full
        if len(batch_translated) != len(batch):
            batch_translated = translate_free_llm_batch(
                batch,
                target_lang=target_lang,
                prompt_style=prompt_style,
                custom_prompt_text=custom_prompt_text,
                batch_durations=batch_durations,
            )

        # Tertiary: Contextual Multi-Line Web Translate + Dubbing Harmonizer
        if len(batch_translated) != len(batch):
            batch_translated = translate_free_web_batch(
                batch,
                target_lang_code=target_lang_code,
                prompt_style=prompt_style,
            )

        # Final safety net: Line-by-line Colloquial Localization + Web Translate + Batch Harmonizer
        if len(batch_translated) != len(batch):
            raw_fallback = []
            for item_text in batch:
                if cancel_event and cancel_event.is_set():
                    _send_status(status_cb, "⏹ Đã hủy dịch.", prog_val=0)
                    return ""
                res = translate_free_web(
                    item_text,
                    target_lang_code=target_lang_code,
                    prompt_style=prompt_style,
                )
                if res:
                    raw_fallback.append(lach_luat_google_dich(res))
                else:
                    raw_fallback.append(polish_vietnamese_dubbing(item_text, item_text, prompt_style))
                time.sleep(0.05)
            if target_lang_code == 'vi':
                batch_translated = harmonize_vietnamese_dialogue_batch(batch, raw_fallback, prompt_style)
            else:
                batch_translated = raw_fallback

        translated_texts.extend(batch_translated)

    for i, t in enumerate(translated_texts):
        if i < len(subs) and t:
            subs[i].text = lach_luat_google_dich(strip_stray_lang_tags(t))

    out_dir = os.path.join(workspace_dir, "Data")
    os.makedirs(out_dir, exist_ok=True)
    out_srt_path = os.path.join(out_dir, "temp_translated.srt")

    subs.save(out_srt_path, encoding='utf-8')
    optimize_srt_timing(out_srt_path)

    _send_status(status_cb, f"✅ Hoàn tất dịch API {total_lines} câu sang {target_lang} ({prompt_style})!", prog_val=100)
    return out_srt_path

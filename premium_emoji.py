"""
Telegram Premium (custom animatsion) emoji'larni qo'llab-quvvatlash.

Ishlashi uchun shart: botni yaratgan Telegram hisobingizda PREMIUM obuna bo'lishi kerak
(bu — Telegram'ning o'zining talabi, kodga bog'liq emas).

Qanday ishlatiladi:
1. get_emoji_id.py skriptini ishga tushiring, botga premium emoji yuboring —
   u sizga har bir emoji'ning ID raqamini beradi.
2. Shu ID'larni pastdagi PREMIUM_EMOJI_IDS lug'atiga (yoki .env fayliga) joylang.
3. Agar biror emoji uchun ID kiritilmagan bo'lsa, oddiy (standart) emoji ishlatilaveradi —
   bot hech qachon "buzilmaydi", faqat premium bo'lmagan hollarda oddiy ko'rinishda qoladi.
"""
import os

# Standart (oddiy) emoji -> shu emoji uchun premium ID saqlanadigan .env o'zgaruvchisi nomi.
# .env faylida masalan: PREMIUM_EMOJI_VIDEO=5368324170671202286
_EMOJI_ENV_KEYS = {
    "🎬": "PREMIUM_EMOJI_VIDEO",
    "💰": "PREMIUM_EMOJI_MONEY",
    "🛒": "PREMIUM_EMOJI_CART",
    "🌐": "PREMIUM_EMOJI_GLOBE",
    "🔙": "PREMIUM_EMOJI_BACK",
    "❌": "PREMIUM_EMOJI_CROSS",
    "✅": "PREMIUM_EMOJI_CHECK",
    "📤": "PREMIUM_EMOJI_SEND",
    "🎁": "PREMIUM_EMOJI_GIFT",
    "⏳": "PREMIUM_EMOJI_HOURGLASS",
    "🎙": "PREMIUM_EMOJI_MIC",
    "🖼": "PREMIUM_EMOJI_IMAGE",
    "🔗": "PREMIUM_EMOJI_LINK",
    "📦": "PREMIUM_EMOJI_BOX",
    "💳": "PREMIUM_EMOJI_CARD",
    "📸": "PREMIUM_EMOJI_CAMERA",
    "🎨": "PREMIUM_EMOJI_ART",
    "📷": "PREMIUM_EMOJI_PHOTO",
    "⏱": "PREMIUM_EMOJI_TIMER",
}

# Dastur ishga tushganda .env'dan o'qib olinadi
PREMIUM_EMOJI_IDS = {
    emoji: os.getenv(env_key, "")
    for emoji, env_key in _EMOJI_ENV_KEYS.items()
}


def e(emoji_char: str) -> str:
    """
    Berilgan oddiy emoji uchun, agar .env'da premium ID sozlangan bo'lsa,
    Telegram HTML premium-emoji tegini qaytaradi. Aks holda, o'zgarishsiz emoji qaytaradi.
    Bot xabarlarida parse_mode="HTML" bilan ishlatilishi kerak (bizning botda shunday).

    DIQQAT: Bu faqat ODDIY XABARLARDA (message.answer/edit_text) ishlaydi.
    Telegram tugmalari (ReplyKeyboardMarkup/KeyboardButton) HTML formatlashni
    qo'llab-quvvatlamaydi — shuning uchun tugma matnlarida bu funksiya ISHLATILMAYDI.
    """
    emoji_id = PREMIUM_EMOJI_IDS.get(emoji_char)
    if emoji_id:
        return f'<tg-emoji emoji-id="{emoji_id}">{emoji_char}</tg-emoji>'
    return emoji_char


def apply_premium_emojis(text: str) -> str:
    """
    Matndagi barcha tanish emoji'larni (agar ular uchun .env'da premium ID sozlangan bo'lsa)
    premium versiyasiga almashtiradi. Faqat XABAR MATNI uchun, tugma matni uchun emas.
    """
    for emoji_char, emoji_id in PREMIUM_EMOJI_IDS.items():
        if emoji_id and emoji_char in text:
            text = text.replace(emoji_char, e(emoji_char))
    return text

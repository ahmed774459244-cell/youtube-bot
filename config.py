"""
Konfiguratsiya fayli — barcha API kalitlar shu yerda saqlanadi.
Haqiqiy qiymatlarni .env faylida yoki muhit o'zgaruvchilarida (environment variables) saqlang,
hech qachon kodni to'g'ridan-to'g'ri kalit bilan repo'ga qo'ymang.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Telegram bot ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# --- Skript yozish uchun (Gemini API) ---
# Google AI Studio (aistudio.google.com) dan bepul olinadi
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# --- Fon rasm/video uchun (Pexels — bepul, cheksiz) ---
# https://www.pexels.com/api/ dan bepul ro'yxatdan o'tib olinadi
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# --- Video sozlamalari ---
VIDEO_WIDTH = int(os.getenv("VIDEO_WIDTH", "1280"))
VIDEO_HEIGHT = int(os.getenv("VIDEO_HEIGHT", "720"))
VIDEO_FPS = 30

# ffmpeg necha protsessor yadrosidan foydalansin. Server RAM/CPU'siga qarab sozlang:
# kichik server (0.5-1 CPU) -> 1, o'rtacha/katta server (2+ CPU) -> 2 yoki undan ko'p.
VIDEO_THREADS = os.getenv("VIDEO_THREADS", "2")

# --- Subtitr sozlamalari ---
SUBTITLES_ENABLED = os.getenv("SUBTITLES_ENABLED", "true").lower() == "true"
SUBTITLE_FONT_SIZE = int(os.getenv("SUBTITLE_FONT_SIZE", "22"))
SUBTITLE_FONT_NAME = os.getenv("SUBTITLE_FONT_NAME", "DejaVu Sans")
# ASS rang formati: &HAABBGGRR (AA=shaffoflik, BGR — teskari tartibda)
SUBTITLE_PRIMARY_COLOR = os.getenv("SUBTITLE_PRIMARY_COLOR", "&H00FFFFFF")   # oq matn
SUBTITLE_OUTLINE_COLOR = os.getenv("SUBTITLE_OUTLINE_COLOR", "&H00000000")  # qora kontur
SUBTITLE_HIGHLIGHT_COLOR = os.getenv("SUBTITLE_HIGHLIGHT_COLOR", "&H0000D7FF")  # oltin-sariq (urg'u so'zlar uchun, kelajakda)

# Ovoz tili (edge-tts formatida). Bir nechta til orasidan tanlash mumkin:
# O'zbek:   "uz-UZ-SardorNeural" (erkak) yoki "uz-UZ-MadinaNeural" (ayol)
# Ingliz:   "en-US-AriaNeural" (ayol) yoki "en-US-GuyNeural" (erkak)
# Rus:      "ru-RU-SvetlanaNeural"
TTS_VOICE = "uz-UZ-SardorNeural"

# Skript qaysi tilda yozilishi kerak (script_generator.py shunga qarab yozadi)
SCRIPT_LANGUAGE = "Uzbek"

# Vaqtinchalik fayllar papkasi
TEMP_DIR = "temp_files"
OUTPUT_DIR = "output_videos"

# --- AI-generatsiya rasmlar (Pexels stock o'rniga original vizual) ---
# true bo'lsa, har bir sahna uchun Gemini orqali original rasm chiziladi.
# Agar generatsiya muvaffaqiyatsiz bo'lsa, avtomatik ravishda Pexels'ga qaytadi (zaxira reja).
USE_AI_IMAGES = os.getenv("USE_AI_IMAGES", "true").lower() == "true"
AI_IMAGE_MODEL = os.getenv("AI_IMAGE_MODEL", "gemini-2.5-flash-image")

# Rasm chizish uslubi — har bir sahna promptiga shu qo'shimcha qo'shiladi.
# Masalan: "cinematic photo" (realistik), yoki "simple hand-drawn stick-figure cartoon,
# black line art on plain background" (YouTube'dagi "explainer" videolar uslubi).
IMAGE_STYLE = os.getenv(
    "IMAGE_STYLE",
    "simple hand-drawn cartoon illustration, black line art, minimalist flat colors, "
    "plain background, explainer-video style",
)

# --- Local Telegram Bot API server (2GB fayl limiti uchun, ixtiyoriy) ---
# Agar telegram-bot-api.exe serverini ishga tushirgan bo'lsangiz, buni true qiling.
# Aks holda standart Telegram serveri ishlatiladi (50MB limit, lekin qo'shimcha sozlash shart emas).
USE_LOCAL_API_SERVER = os.getenv("USE_LOCAL_API_SERVER", "false").lower() == "true"
LOCAL_API_SERVER_URL = os.getenv("LOCAL_API_SERVER_URL", "http://localhost:8081")

# --- Bir vaqtda nechta video parallel ishlanishi (qolganlari avtomatik navbatda kutadi) ---
# Server resurslariga qarab sozlang: 2GB RAM ~ 1, 4GB RAM ~ 2, 8GB RAM ~ 3-4.
MAX_CONCURRENT_JOBS = int(os.getenv("MAX_CONCURRENT_JOBS", "2"))

# --- To'lov tizimi ---
# Har bir yangi foydalanuvchiga beriladigan bepul daqiqalar (masalan: 5x10min yoki 25x2min = 50 daqiqa)
FREE_MINUTES = float(os.getenv("FREE_MINUTES", "50"))

# Sotib olish uchun kredit paketlari (narxlarni o'zingizga moslang)
PACKAGES = [
    {"id": "p1", "minutes": 30, "price": 15000},
    {"id": "p2", "minutes": 60, "price": 25000},
    {"id": "p3", "minutes": 150, "price": 50000},
]

# Sizning shaxsiy Telegram ID'ingiz (qo'lda tasdiqlash uchun bildirishnomalar shu yerga keladi).
# Aniqlash uchun @userinfobot ga yozing, u sizga ID'ingizni beradi.
ADMIN_TELEGRAM_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))

# Qo'lda to'lov qilish uchun foydalanuvchiga ko'rsatiladigan ko'rsatma (Click raqami/karta va h.k.)
PAYMENT_INSTRUCTIONS = os.getenv(
    "PAYMENT_INSTRUCTIONS",
    "Click: +998 XX XXX XX XX\nyoki karta: XXXX XXXX XXXX XXXX",
)

# --- Click.uz avtomatik to'lov (ixtiyoriy — domen + SSL sertifikat talab qiladi, README'ga qarang) ---
CLICK_MERCHANT_ID = os.getenv("CLICK_MERCHANT_ID", "")
CLICK_SERVICE_ID = os.getenv("CLICK_SERVICE_ID", "")
CLICK_SECRET_KEY = os.getenv("CLICK_SECRET_KEY", "")
CLICK_MERCHANT_USER_ID = os.getenv("CLICK_MERCHANT_USER_ID", "")
CLICK_ENABLED = bool(CLICK_MERCHANT_ID and CLICK_SERVICE_ID and CLICK_SECRET_KEY)

# --- Tezkor to'ldirish: SMS orqali avtomatik aniqlash (Click shartnomasi shart emas) ---
# Foydalanuvchi istalgan summani kiritadi, shu kartaga to'laydi, bank SMS'i orqali avtomatik tasdiqlanadi.
PAYMENT_CARD_NUMBER = os.getenv("PAYMENT_CARD_NUMBER", "9860 XXXX XXXX XXXX")
PAYMENT_CARD_OWNER = os.getenv("PAYMENT_CARD_OWNER", "")
RATE_PER_MINUTE = int(os.getenv("RATE_PER_MINUTE", "500"))  # 1 video-daqiqasi narxi (so'm)
MIN_TOPUP_AMOUNT = int(os.getenv("MIN_TOPUP_AMOUNT", "1000"))
SMS_WEBHOOK_SECRET = os.getenv("SMS_WEBHOOK_SECRET", "")  # SMS forwarder ilovasi shu tokenni yuborishi kerak
SMS_MATCH_WINDOW_MINUTES = int(os.getenv("SMS_MATCH_WINDOW_MINUTES", "30"))

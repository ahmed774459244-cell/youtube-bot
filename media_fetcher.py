"""
Har bir sahna uchun media (fon rasm/video) tayyorlaydi.
Ustuvorlik: 1) AI-generatsiya original rasm (Gemini), 2) Pexels video, 3) Pexels rasm (zaxira rejalar).
"""
import os
import random
import time
import logging
import requests
import concurrent.futures
from google import genai
from google.genai import types
from config import PEXELS_API_KEY, GEMINI_API_KEY, USE_AI_IMAGES, AI_IMAGE_MODEL, IMAGE_STYLE

logger = logging.getLogger(__name__)

HEADERS = {"Authorization": PEXELS_API_KEY}

MAX_RETRIES = 4
RETRY_DELAY_SECONDS = 3
REQUEST_TIMEOUT = 60  # sekundda - sekin internet uchun oshirilgan

AI_IMAGE_TIMEOUT_SECONDS = 45  # bitta AI rasm so'rovi uchun maksimal kutish vaqti
AI_IMAGE_MAX_RETRIES = 2


def _generate_ai_image_once(prompt: str, output_path: str) -> bool:
    """Bitta urinish — hech qanday qayta urinish yoki timeout logikasi shu yerda yo'q."""
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model=AI_IMAGE_MODEL,
        contents=f"{prompt}. Style: {IMAGE_STYLE}. High quality, detailed, visually striking, suitable for a YouTube video background.",
        config=types.GenerateContentConfig(response_modalities=["Text", "Image"]),
    )
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            with open(output_path, "wb") as f:
                f.write(part.inline_data.data)
            return True
    return False


def generate_ai_image(prompt: str, output_path: str) -> bool:
    """
    Gemini orqali original (AI-chizilgan) rasm yaratadi. Muvaffaqiyatli bo'lsa True qaytaradi.
    Agar so'rov AI_IMAGE_TIMEOUT_SECONDS ichida javob bermasa yoki xatolik chiqsa,
    qayta uriniladi (AI_IMAGE_MAX_RETRIES marta); baribir ishlamasa, False qaytariladi
    (chaqiruvchi tomon Pexels'ga o'tadi — jarayon HECH QACHON abadiy "osilib" qolmaydi).
    """
    last_error = None
    for attempt in range(1, AI_IMAGE_MAX_RETRIES + 1):
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_generate_ai_image_once, prompt, output_path)
                return future.result(timeout=AI_IMAGE_TIMEOUT_SECONDS)
        except concurrent.futures.TimeoutError:
            last_error = f"{AI_IMAGE_TIMEOUT_SECONDS}s ichida javob kelmadi (timeout)"
            logger.warning(f"AI rasm generatsiyasi urinish {attempt}/{AI_IMAGE_MAX_RETRIES}: {last_error}")
        except Exception as e:
            last_error = e
            logger.warning(f"AI rasm generatsiyasi urinish {attempt}/{AI_IMAGE_MAX_RETRIES} muvaffaqiyatsiz: {e}")

    logger.warning(f"AI rasm generatsiyasi butunlay muvaffaqiyatsiz bo'ldi: {last_error}")
    return False


def _request_with_retry(method, url, **kwargs):
    """requests so'rovini vaqtinchalik tarmoq xatolarida avtomatik qayta uradi."""
    kwargs.setdefault("timeout", REQUEST_TIMEOUT)
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = method(url, **kwargs)
            resp.raise_for_status()
            return resp
        except Exception as e:
            last_error = e
            logger.warning(f"So'rov urinish {attempt}/{MAX_RETRIES} muvaffaqiyatsiz ({url}): {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS * attempt)
    raise RuntimeError(f"So'rov muvaffaqiyatsiz ({MAX_RETRIES} urinishdan keyin): {last_error}")


def fetch_background_video(query: str, output_path: str, min_duration: int = 5) -> bool:
    """
    Pexels'dan query bo'yicha fon video qidiradi va yuklab oladi.
    Muvaffaqiyatli bo'lsa True, topilmasa False qaytaradi.
    """
    url = "https://api.pexels.com/videos/search"
    params = {"query": query, "per_page": 5, "orientation": "landscape"}
    resp = _request_with_retry(requests.get, url, headers=HEADERS, params=params)
    data = resp.json()

    videos = data.get("videos", [])
    if not videos:
        return False

    video = random.choice(videos)
    # HD sifatdagi eng mos fayl linkini tanlaymiz
    files = sorted(
        [f for f in video["video_files"] if f.get("width", 0) >= 1280],
        key=lambda f: f["width"],
    )
    if not files:
        files = video["video_files"]

    video_url = files[0]["link"]
    r = _request_with_retry(requests.get, video_url)
    with open(output_path, "wb") as f:
        f.write(r.content)
    return True


def fetch_background_image(query: str, output_path: str) -> bool:
    """Video topilmasa, muqobil sifatida rasm yuklab oladi."""
    url = "https://api.pexels.com/v1/search"
    params = {"query": query, "per_page": 5, "orientation": "landscape"}
    resp = _request_with_retry(requests.get, url, headers=HEADERS, params=params)
    data = resp.json()

    photos = data.get("photos", [])
    if not photos:
        return False

    photo = random.choice(photos)
    image_url = photo["src"]["large2x"]
    r = _request_with_retry(requests.get, image_url)
    with open(output_path, "wb") as f:
        f.write(r.content)
    return True


def fetch_media_for_scene(query: str, output_dir: str, scene_index: int, image_prompt: str = None,
                           use_ai_images: bool = None) -> dict:
    """
    Sahna uchun media tayyorlaydi.
    Ustuvorlik: AI-generatsiya rasm (agar yoqilgan bo'lsa) -> Pexels video -> Pexels rasm.
    use_ai_images=None bo'lsa, config.py'dagi standart qiymat ishlatiladi (har bir chaqiruvda alohida bekor qilish mumkin).
    Qaytaradi: {"type": "video"|"image", "path": "...", "source": "ai"|"pexels"}
    """
    should_use_ai = USE_AI_IMAGES if use_ai_images is None else use_ai_images

    if should_use_ai and image_prompt:
        ai_path = os.path.join(output_dir, f"scene_{scene_index}_ai.png")
        if generate_ai_image(image_prompt, ai_path):
            return {"type": "image", "path": ai_path, "source": "ai"}
        logger.warning("AI rasm ishlamadi, Pexels'ga (zaxira) o'tilmoqda...")

    video_path = os.path.join(output_dir, f"scene_{scene_index}.mp4")
    if fetch_background_video(query, video_path):
        return {"type": "video", "path": video_path, "source": "pexels"}

    image_path = os.path.join(output_dir, f"scene_{scene_index}.jpg")
    if fetch_background_image(query, image_path):
        return {"type": "image", "path": image_path, "source": "pexels"}

    raise RuntimeError(f"'{query}' bo'yicha hech qanday media topilmadi (AI ham, Pexels ham muvaffaqiyatsiz)")

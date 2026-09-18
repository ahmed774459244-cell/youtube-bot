"""
Matnni ovozga aylantiradi (Text-to-Speech).
Avval edge-tts (sifatliroq) sinaladi. Agar tarmoq/websocket muammosi tufayli ishlamasa,
avtomatik ravishda gTTS (oddiy HTTPS so'rov, ko'proq tarmoqlarda ishlaydi) ga o'tiladi.
"""
import asyncio
import logging
import edge_tts
from gtts import gTTS
from config import TTS_VOICE

logger = logging.getLogger(__name__)

MAX_RETRIES = 1  # VPS serverlarda edge-tts odatda bloklangan (403), tez gTTS'ga o'tamiz
RETRY_DELAY_SECONDS = 1

# edge-tts ovoz kodidan gTTS til kodiga taxminiy moslashtirish (zaxira reja uchun).
# DIQQAT: gTTS'da o'zbek tili yo'q, shuning uchun agar edge-tts o'zbekcha ovoz bilan
# ishlamay qolsa, zaxira sifatida ruscha ovozga tushadi (o'zbekcha emas, lekin ishlaydi).
_EDGE_TO_GTTS_LANG = {
    "uz-UZ-SardorNeural": "ru",
    "uz-UZ-MadinaNeural": "ru",
    "ru-RU-SvetlanaNeural": "ru",
    "en-US-AriaNeural": "en",
    "en-US-GuyNeural": "en",
}


async def _generate_edge_async(text: str, output_path: str, voice: str):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)


async def _generate_edge_with_retry(text: str, output_path: str, voice: str):
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            await _generate_edge_async(text, output_path, voice)
            return output_path
        except Exception as e:
            last_error = e
            logger.warning(f"edge-tts urinish {attempt}/{MAX_RETRIES} muvaffaqiyatsiz: {e}")
            if attempt < MAX_RETRIES:
                await asyncio.sleep(RETRY_DELAY_SECONDS)
    raise RuntimeError(str(last_error))


def _generate_gtts(text: str, output_path: str, voice: str):
    lang = _EDGE_TO_GTTS_LANG.get(voice, "ru")
    tts = gTTS(text=text, lang=lang)
    tts.save(output_path)
    return output_path


def generate_voice(text: str, output_path: str, voice: str = TTS_VOICE):
    """
    Berilgan matnni ovoz fayliga (mp3) aylantiradi.
    Avval edge-tts (sifatliroq), muvaffaqiyatsiz bo'lsa gTTS (barqarorroq) ishlatiladi.
    """
    try:
        return asyncio.run(_generate_edge_with_retry(text, output_path, voice))
    except Exception as e:
        logger.warning(f"edge-tts butunlay ishlamadi, gTTS'ga o'tilmoqda: {e}")
        return _generate_gtts(text, output_path, voice)


if __name__ == "__main__":
    generate_voice("Salom, bu test ovozi.", "test_voice.mp3", voice="ru-RU-SvetlanaNeural")
    print("Tayyor: test_voice.mp3")

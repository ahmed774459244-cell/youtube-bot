"""
Mavzu asosida YouTube video uchun skript (ssenariy) yaratadi.
Skript sahnalarga bo'linadi — har bir sahna uchun: matn (voiceover) + tasvir uchun kalit so'z.
"""
import json
import re
from google import genai
from config import GEMINI_API_KEY, SCRIPT_LANGUAGE


def _extract_json(text: str) -> str:
    """Modeldan qaytgan javobdan JSON qismini ajratib oladi (``` bloklarni tozalaydi)."""
    text = text.strip()
    text = re.sub(r"^```json\s*", "", text)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"```$", "", text)
    return text.strip()


def generate_script(topic: str, target_minutes: int = 10, script_language: str = None) -> list[dict]:
    """
    Mavzu bo'yicha video skriptini yaratadi.

    Qaytaradi: [{"text": "sahna matni", "image_query": "pexels qidiruv so'zi"}, ...]
    """
    client = genai.Client(api_key=GEMINI_API_KEY)
    lang = script_language or SCRIPT_LANGUAGE

    # O'rtacha diktor tezligi ~140 so'z/daqiqa. Amaliyotda Gemini so'ralgan so'z sonining
    # taxminan 60-65% ini yozib qo'yishi kuzatildi (uzunroq matn so'ralganda ham qisqartirib yuboradi),
    # shuning uchun 1.6x koeffitsient bilan haqiqiy maqsadga yetkazamiz.
    CORRECTION_FACTOR = 1.6
    target_words = int(target_minutes * 140 * CORRECTION_FACTOR)
    approx_scenes = max(10, int(target_minutes * 4 * CORRECTION_FACTOR))
    words_per_scene_min = int((target_words / approx_scenes) * 0.85)
    words_per_scene_max = int((target_words / approx_scenes) * 1.15)

    prompt = f"""You are a professional YouTube documentary-style scriptwriter, in the vein of narrated educational/factual channels.
Topic: "{topic}"

Write a script for a {target_minutes}-minute video on this topic.
IMPORTANT: Write the ENTIRE script (the "text" field) in {lang}, regardless of the language the topic was given in.

NARRATIVE STYLE GUIDE (apply this throughout):
- Open with a vivid, sensory scene or relatable moment that pulls the viewer in, then pivot into a driving question the video will explore.
- Use short, punchy sentences mixed with longer explanatory ones for natural rhythm — avoid monotone, uniform sentence lengths.
- Ground claims in specific, concrete details (dates, places, names, numbers) to build credibility, as a documentary narrator would.
- Practice epistemic humility on uncertain points — phrases like "we can't be certain", "researchers still debate this", "what we do know is..." — rather than overstating confidence.
- Use rhetorical questions and short transitional sentences ("So what happened next?", "But there's a complication.") to move between sections smoothly.
- Occasionally use parallel/repeated sentence structures for emphasis and rhythm.
- Address the viewer directly at points ("imagine...", "picture...", "you might...") to create intimacy.
- Close by circling back to the opening scene or idea, tying the historical/factual content back to the present or to the viewer's own life.

STRICT LENGTH REQUIREMENT (read carefully, this is critical):
- Total script length: approximately {target_words} words across all scenes combined. Do NOT undershoot this — it is common for scripts to come out too short, so err on the side of writing MORE detail, more examples, and more depth per scene rather than less.
- Split the script into exactly {approx_scenes} scenes.
- EACH scene's "text" field must be between {words_per_scene_min} and {words_per_scene_max} words. A scene with fewer words than this is NOT acceptable — expand it with more detail, examples, or explanation until it reaches the required length.
- Before finalizing your answer, mentally count the words in each scene and verify it meets the minimum. If a scene is too short, rewrite it longer.

For each scene provide:
1. "text" — the narrator's voiceover text in {lang} (clear, engaging, factual, natural spoken style, meeting the word count above)
2. "image_prompt" — a detailed, vivid ENGLISH prompt (10-20 words) for an AI image generator to create an original illustration matching this scene. Describe composition, style (e.g. "cinematic photo", "digital illustration", "3D render"), subject, mood, and lighting. Be specific and visual.
3. "image_query" — a 2-4 word ENGLISH search query as a backup for stock footage search, in case AI image generation is unavailable

Respond ONLY in the following JSON format, no other text:

[
  {{"text": "...", "image_prompt": "...", "image_query": "..."}},
  {{"text": "...", "image_prompt": "...", "image_query": "..."}}
]
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )

    raw = _extract_json(response.text)
    scenes = json.loads(raw)
    return scenes


def generate_youtube_metadata(topic: str, script_language: str = None) -> dict:
    """
    Video uchun YouTube'ga yuklashga tayyor sarlavha (3 variant), tavsif va hashtag'lar yaratadi.
    Qaytaradi: {"titles": [...], "description": "...", "hashtags": [...]}
    """
    client = genai.Client(api_key=GEMINI_API_KEY)
    lang = script_language or SCRIPT_LANGUAGE

    prompt = f"""You are a YouTube SEO expert.
Topic: "{topic}"

Generate YouTube metadata for a video on this topic, in {lang}:
1. "titles" — 3 different catchy, click-worthy title options (each under 70 characters)
2. "description" — a 2-3 paragraph YouTube description, engaging, with a hook in the first line (SEO-friendly)
3. "hashtags" — 8-10 relevant hashtags (without # symbol, just the words)

Respond ONLY in this JSON format, no other text:
{{"titles": ["...", "...", "..."], "description": "...", "hashtags": ["...", "..."]}}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )
    raw = _extract_json(response.text)
    return json.loads(raw)


def generate_channel_branding(niche: str, script_language: str = None) -> dict:
    """
    Kanal mavzusi (niche) asosida kanal nomi variantlari va tavsifini yaratadi.
    Qaytaradi: {"names": [...], "description": "...", "logo_prompt": "...", "banner_prompt": "..."}
    """
    client = genai.Client(api_key=GEMINI_API_KEY)
    lang = script_language or SCRIPT_LANGUAGE

    prompt = f"""You are a YouTube branding expert.
Channel niche/topic: "{niche}"

Generate original branding for a NEW YouTube channel in this niche, in {lang}:
1. "names" — 5 catchy, memorable, original channel name ideas (short, brandable, not copying any existing real channel or brand)
2. "description" — a 2-3 paragraph "About" section for the channel (engaging, explains what viewers will get)
3. "logo_prompt" — a detailed ENGLISH prompt (15-25 words) for an AI image generator to create an original, simple, iconic, square logo/icon representing this channel (describe style, symbol, colors — no text/letters in the image)
4. "banner_prompt" — a detailed ENGLISH prompt (15-25 words) for an AI image generator to create an original, wide, visually striking YouTube channel banner/header image representing this niche (describe style, mood, colors, composition — no text in the image)

Respond ONLY in this JSON format, no other text:
{{"names": ["...", "...", "...", "...", "..."], "description": "...", "logo_prompt": "...", "banner_prompt": "..."}}
"""

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )
    raw = _extract_json(response.text)
    return json.loads(raw)


if __name__ == "__main__":
    # Tezkor test uchun
    scenes = generate_script("Quyosh tizimi haqida qiziqarli faktlar", target_minutes=2)
    for i, s in enumerate(scenes, 1):
        print(f"{i}. [{s['image_query']}] {s['text'][:60]}...")

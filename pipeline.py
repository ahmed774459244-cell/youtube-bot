"""
Butun jarayonni boshqaradigan asosiy funksiya:
mavzu -> skript -> ovoz -> fon media -> sahna kliplari -> yakuniy video
"""
import os
import shutil
import uuid

from config import TEMP_DIR, OUTPUT_DIR, USE_LOCAL_API_SERVER
from script_generator import generate_script
from tts_generator import generate_voice
from media_fetcher import fetch_media_for_scene
from video_builder import build_scene_clip, concatenate_clips, compress_if_needed


def create_video(topic: str, target_minutes: int = 10, progress_callback=None,
                  voice: str = None, script_language: str = None, use_ai_images: bool = None) -> str:
    """
    To'liq pipeline: mavzudan yakuniy video fayligacha.
    progress_callback(str) — jarayon haqida foydalanuvchiga xabar berish uchun (ixtiyoriy).
    voice / script_language — agar berilmasa, config.py'dagi standart qiymat ishlatiladi.
    use_ai_images — True: AI-chizilgan (masalan multfilm) rasm, False: Pexels stock, None: config.py standart qiymati.

    Qaytaradi: yakuniy video faylining yo'li.
    """
    def report(msg):
        if progress_callback:
            progress_callback(msg)

    job_id = str(uuid.uuid4())[:8]
    job_temp_dir = os.path.join(TEMP_DIR, job_id)
    os.makedirs(job_temp_dir, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    try:
        # 1. Skript yaratish
        report("📝 Skript yozilmoqda...")
        scenes = generate_script(topic, target_minutes=target_minutes, script_language=script_language)
        report(f"✅ Skript tayyor: {len(scenes)} ta sahna")

        clip_paths = []
        total = len(scenes)
        for i, scene in enumerate(scenes, 1):
            # 2. Ovoz yaratish
            report(f"🎙️ Sahna {i}/{total}: ovoz yaratilmoqda...")
            audio_path = os.path.join(job_temp_dir, f"audio_{i}.mp3")
            if voice:
                generate_voice(scene["text"], audio_path, voice=voice)
            else:
                generate_voice(scene["text"], audio_path)

            # 3. Fon media yuklab olish
            report(f"🖼️ Sahna {i}/{total}: fon video/rasm qidirilmoqda...")
            media = fetch_media_for_scene(
                scene["image_query"], job_temp_dir, i, image_prompt=scene.get("image_prompt"),
                use_ai_images=use_ai_images,
            )

            # 4. Sahna klipini yig'ish
            report(f"🎬 Sahna {i}/{total}: klip yig'ilmoqda...")
            clip_path = os.path.join(job_temp_dir, f"clip_{i}.mp4")
            build_scene_clip(media, audio_path, clip_path, scene_index=i, subtitle_text=scene["text"])
            clip_paths.append(clip_path)

        # 5. Barcha kliplarni birlashtirish
        report("🔗 Video qismlar birlashtirilmoqda...")
        final_path = os.path.join(OUTPUT_DIR, f"video_{job_id}.mp4")
        concatenate_clips(clip_paths, final_path, job_temp_dir)

        # 6. Fayl hajmi limitidan oshsa siqamiz.
        # Oddiy Telegram serveri: 45MB (xavfsizlik zaxirasi bilan, chunki limit 50MB).
        # Local Bot API server ishlatilsa: 1900MB (limit 2000MB, deyarli hech qachon kerak bo'lmaydi).
        max_size_mb = 1900 if USE_LOCAL_API_SERVER else 45
        size_mb = os.path.getsize(final_path) / (1024 * 1024)
        if size_mb > max_size_mb:
            report(f"📦 Video hajmi {size_mb:.0f}MB — limit uchun siqilmoqda...")
            final_path = compress_if_needed(final_path, max_size_mb=max_size_mb)

        report("✅ Video tayyor!")
        return final_path

    finally:
        # Vaqtinchalik fayllarni tozalash
        shutil.rmtree(job_temp_dir, ignore_errors=True)


if __name__ == "__main__":
    path = create_video("Quyosh tizimi haqida qiziqarli faktlar", target_minutes=2, progress_callback=print)
    print(f"Natija: {path}")

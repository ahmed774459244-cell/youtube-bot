"""
Har bir sahna uchun (fon video/rasm + ovoz) alohida klip tayyorlaydi,
so'ng hammasini bitta yakuniy videoga birlashtiradi. ffmpeg orqali ishlaydi.
"""
import os
import re
import subprocess
from config import (
    VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, VIDEO_THREADS,
    SUBTITLES_ENABLED, SUBTITLE_FONT_SIZE, SUBTITLE_FONT_NAME,
    SUBTITLE_PRIMARY_COLOR, SUBTITLE_OUTLINE_COLOR,
)


def _get_audio_duration(audio_path: str) -> float:
    """ffprobe orqali audio faylning davomiyligini (soniyada) aniqlaydi."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", audio_path,
    ]
    out = subprocess.check_output(cmd).decode().strip()
    return float(out)


def _format_srt_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def _generate_srt(text: str, duration: float, srt_path: str, words_per_chunk: int = 6):
    """
    Matnni o'qishga qulay kichik bo'laklarga bo'lib, har bir bo'lakka video davomiyligi
    bo'yicha teng taqsimlangan vaqt oralig'i bilan SRT subtitr fayli yaratadi.
    """
    words = text.split()
    chunks = [
        " ".join(words[i:i + words_per_chunk])
        for i in range(0, len(words), words_per_chunk)
    ] or [text]

    chunk_duration = duration / len(chunks)
    lines = []
    for i, chunk in enumerate(chunks):
        start = i * chunk_duration
        end = (i + 1) * chunk_duration
        lines.append(str(i + 1))
        lines.append(f"{_format_srt_timestamp(start)} --> {_format_srt_timestamp(end)}")
        lines.append(chunk)
        lines.append("")

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return srt_path


def _subtitles_filter(srt_path: str) -> str:
    """ffmpeg 'subtitles' filtri uchun tayyor qism — chiroyli, konturli, soyali uslub bilan."""
    # ffmpeg filtr sintaksisida maxsus belgilarni ekranlash kerak
    escaped_path = srt_path.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    style = (
        f"FontName={SUBTITLE_FONT_NAME},FontSize={SUBTITLE_FONT_SIZE},"
        f"PrimaryColour={SUBTITLE_PRIMARY_COLOR},OutlineColour={SUBTITLE_OUTLINE_COLOR},"
        f"BorderStyle=1,Outline=2,Shadow=1,Bold=1,Alignment=2,MarginV=60"
    )
    return f"subtitles='{escaped_path}':force_style='{style}'"


def build_scene_clip(media: dict, audio_path: str, output_path: str, scene_index: int = 0,
                      subtitle_text: str = None):
    """
    Bitta sahna uchun klip yaratadi: fon (video yoki rasm, kerakli uzunlikka cho'zilgan/kesilgan) + ovoz.
    Rasm bo'lsa, "Ken Burns" effekti (asta-sekin zoom) qo'llaniladi — statik rasm harakatli video kabi ko'rinadi.
    Agar subtitle_text berilsa va SUBTITLES_ENABLED yoqilgan bo'lsa, ovozga sinxron subtitr ham qo'shiladi.
    """
    duration = _get_audio_duration(audio_path)
    scale_filter = f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=increase,crop={VIDEO_WIDTH}:{VIDEO_HEIGHT}"

    srt_path = None
    if SUBTITLES_ENABLED and subtitle_text:
        srt_path = output_path.replace(".mp4", ".srt")
        _generate_srt(subtitle_text, duration, srt_path)

    if media["type"] == "video":
        vf = scale_filter
        if srt_path:
            vf = f"{vf},{_subtitles_filter(srt_path)}"
        cmd = [
            "ffmpeg", "-y",
            "-stream_loop", "-1", "-i", media["path"],   # fon video kerak bo'lsa qaytariladi
            "-i", audio_path,
            "-t", str(duration),
            "-vf", vf,
            "-r", str(VIDEO_FPS),
            "-c:v", "libx264", "-preset", "veryfast", "-threads", str(VIDEO_THREADS),
            "-c:a", "aac",
            "-map", "0:v:0", "-map", "1:a:0",
            "-shortest",
            output_path,
        ]
    else:  # rasm — Ken Burns effekti (asta-sekin zoom in/out) bilan
        total_frames = max(int(duration * VIDEO_FPS), 1)
        zoom_in = (scene_index % 2 == 0)  # sahnalar orasida zoom yo'nalishini almashtirib, xilma-xillik beramiz

        if zoom_in:
            zoom_expr = "min(zoom+0.0015,1.5)"
        else:
            zoom_expr = "if(eq(on,1),1.5,max(zoom-0.0015,1.0))"

        ken_burns_filter = (
            f"scale=2560:1440,"
            f"zoompan=z='{zoom_expr}':d={total_frames}:"
            f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:fps={VIDEO_FPS},"
            f"setsar=1"
        )
        if srt_path:
            ken_burns_filter = f"{ken_burns_filter},{_subtitles_filter(srt_path)}"

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", media["path"],
            "-i", audio_path,
            "-t", str(duration),
            "-vf", ken_burns_filter,
            "-r", str(VIDEO_FPS),
            "-c:v", "libx264", "-preset", "veryfast", "-threads", str(VIDEO_THREADS),
            "-c:a", "aac",
            "-pix_fmt", "yuv420p",
            "-shortest",
            output_path,
        ]

    subprocess.run(cmd, check=True, capture_output=True)
    if srt_path and os.path.exists(srt_path):
        os.remove(srt_path)
    return output_path


def concatenate_clips(clip_paths: list[str], output_path: str, temp_dir: str):
    """Barcha sahna kliplarini bitta yakuniy videoga birlashtiradi."""
    concat_list_path = os.path.join(temp_dir, "concat_list.txt")
    with open(concat_list_path, "w") as f:
        for path in clip_paths:
            f.write(f"file '{os.path.abspath(path)}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_list_path,
        "-c", "copy",
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def compress_if_needed(input_path: str, max_size_mb: int = 45) -> str:
    """
    Agar fayl Telegram limitidan (50MB) katta bo'lsa, sifatni bir oz pasaytirib siqadi.
    max_size_mb=45 — xavfsiz zaxira bilan (Telegram metama'lumotlari uchun joy qoldiriladi).
    """
    size_mb = os.path.getsize(input_path) / (1024 * 1024)
    if size_mb <= max_size_mb:
        return input_path

    duration = _get_audio_duration(input_path)  # ffprobe umumiy davomiylikni ham to'g'ri qaytaradi
    # Maqsadli umumiy bitreyt (video+audio), xavfsizlik zaxirasi bilan
    target_total_kbps = int((max_size_mb * 8192) / duration * 0.92)
    audio_kbps = 128
    video_kbps = max(target_total_kbps - audio_kbps, 300)  # juda past bo'lib ketmasin

    compressed_path = input_path.replace(".mp4", "_compressed.mp4")
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-b:v", f"{video_kbps}k",
        "-maxrate", f"{int(video_kbps * 1.2)}k",
        "-bufsize", f"{video_kbps * 2}k",
        "-b:a", f"{audio_kbps}k",
        "-c:v", "libx264", "-preset", "veryfast", "-threads", str(VIDEO_THREADS),
        "-c:a", "aac",
        compressed_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    os.remove(input_path)
    return compressed_path

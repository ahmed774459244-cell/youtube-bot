# Render.com'da "Background Worker" sifatida ishga tushirish uchun.
# Bu fayl botga kerakli barcha narsalarni (Python, ffmpeg) o'z ichiga olgan
# muhitni avtomatik tayyorlaydi — qo'lda o'rnatish shart emas.

FROM python:3.12-slim

# ffmpeg, shrift va boshqa kerakli tizim paketlarini o'rnatish (shrift — subtitr chizish uchun shart)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    fonts-dejavu-core \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Avval faqat requirements.txt'ni nusxalab o'rnatamiz (Docker keshi tezroq ishlashi uchun)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Qolgan barcha loyiha fayllarini nusxalaymiz
COPY . .

# Vaqtinchalik va chiqish papkalarini oldindan yaratib qo'yamiz
RUN mkdir -p temp_files output_videos

CMD ["python", "bot.py"]

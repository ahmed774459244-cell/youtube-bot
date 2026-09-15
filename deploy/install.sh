#!/bin/bash
# VPS serverida BIR MARTA ishga tushiriladigan o'rnatish skripti.
# Ishlatish: bash install.sh

set -e

echo "=== Paketlar ro'yxatini yangilash ==="
apt update

echo "=== Python, pip va ffmpeg o'rnatish ==="
apt install -y python3 python3-pip python3-venv ffmpeg curl

echo "=== Docker o'rnatish (2GB fayl limiti uchun telegram-bot-api serveriga kerak) ==="
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
else
    echo "Docker allaqachon o'rnatilgan, o'tkazib yuborilmoqda."
fi

echo "=== Python virtual muhit yaratish ==="
cd "$(dirname "$0")/.."
python3 -m venv venv
source venv/bin/activate

echo "=== Python kutubxonalarini o'rnatish ==="
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=== O'rnatish tugadi! ==="
echo "Keyingi qadamlar:"
echo "1. .env faylini to'ldiring (agar hali qilmagan bo'lsangiz)"
echo "2. 2GB fayl limiti uchun (ixtiyoriy, lekin tavsiya etiladi):"
echo "     cd deploy && docker compose up -d"
echo "   va .env faylida USE_LOCAL_API_SERVER=true qiling"
echo "3. Botni doim ishlab turadigan qilish:"
echo "     sudo cp deploy/youtube-bot.service /etc/systemd/system/"
echo "     sudo systemctl daemon-reload"
echo "     sudo systemctl enable youtube-bot"
echo "     sudo systemctl start youtube-bot"

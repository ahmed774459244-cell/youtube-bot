"""
VPS serveringizda "local Telegram Bot API" konteynerini ishga tushiradi (2GB fayl limiti uchun)
va asosiy botni shu serverga ulanadigan qilib qayta ishga tushiradi.

Ishlatishdan oldin: pip install paramiko (agar hali o'rnatilmagan bo'lsa)
Ishga tushirish: python setup_local_api.py
"""
import paramiko
import sys

# ==================== SOZLAMALAR ====================
VPS_IP = "13.39.137.123"
VPS_USER = "ubuntu"
VPS_PASSWORD = "x9WC@N5Pfjvqoh9#5^6uPASV"

# my.telegram.org'dan olingan qiymatlar (avval Windows'da ishlatgan)
TELEGRAM_API_ID = "31025748"
TELEGRAM_API_HASH = "81a38fcaf86a9cbeec85dbf1274743eb"
# ======================================================


def run_command(client, command, description):
    print(f"\n>>> {description}")
    stdin, stdout, stderr = client.exec_command(command, get_pty=True)
    for line in iter(stdout.readline, ""):
        print(line, end="")
    exit_status = stdout.channel.recv_exit_status()
    if exit_status != 0:
        print(f"⚠️  Xatolik: {stderr.read().decode()}")
        return False
    return True


def main():
    print(f"🔌 {VPS_IP} serveriga ulanmoqda...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=VPS_IP, username=VPS_USER, password=VPS_PASSWORD, timeout=15)
    print("✅ Ulandi!")

    # 1. Eski local-api konteynerini tozalab, yangisini ishga tushiramiz.
    # --network host: bot va local-server bir xil "localhost" orqali gaplashishi uchun eng oddiy usul.
    run_command(client, "sudo docker stop telegram-bot-api 2>/dev/null; sudo docker rm telegram-bot-api 2>/dev/null; true", "Eski local-api konteynerini tozalash")
    run_command(
        client,
        (
            "sudo docker run -d --name telegram-bot-api --restart unless-stopped --network host "
            f"-e TELEGRAM_API_ID={TELEGRAM_API_ID} -e TELEGRAM_API_HASH={TELEGRAM_API_HASH} "
            "-e TELEGRAM_LOCAL=true aiogram/telegram-bot-api:latest"
        ),
        "2GB fayl limiti uchun local Bot API serverini ishga tushirish",
    )

    # 2. .env faylida USE_LOCAL_API_SERVER=true qilamiz
    run_command(
        client,
        (
            "grep -q '^USE_LOCAL_API_SERVER=' ~/youtube-bot/.env "
            "&& sed -i 's|^USE_LOCAL_API_SERVER=.*|USE_LOCAL_API_SERVER=true|' ~/youtube-bot/.env "
            "|| echo 'USE_LOCAL_API_SERVER=true' >> ~/youtube-bot/.env"
        ),
        ".env faylida USE_LOCAL_API_SERVER=true qilish",
    )
    run_command(
        client,
        (
            "grep -q '^LOCAL_API_SERVER_URL=' ~/youtube-bot/.env "
            "&& sed -i 's|^LOCAL_API_SERVER_URL=.*|LOCAL_API_SERVER_URL=http://localhost:8081|' ~/youtube-bot/.env "
            "|| echo 'LOCAL_API_SERVER_URL=http://localhost:8081' >> ~/youtube-bot/.env"
        ),
        ".env faylida LOCAL_API_SERVER_URL'ni to'g'rilash",
    )

    # 3. Botni ham --network host bilan qayta ishga tushiramiz, shunda localhost:8081'ga yeta oladi
    run_command(client, "sudo docker stop youtube-bot 2>/dev/null; sudo docker rm youtube-bot 2>/dev/null; true", "Eski bot konteynerini tozalash")
    run_command(
        client,
        (
            "sudo docker run -d --name youtube-bot --restart unless-stopped --network host "
            "--env-file ~/youtube-bot/.env youtube-bot"
        ),
        "Botni 2GB limit bilan qayta ishga tushirish",
    )

    print("\n🎉 2GB fayl limiti yoqildi! Endi katta videolar ham siqilmasdan yuboriladi.")
    print("Tekshirish uchun: python check_logs.py")

    client.close()


if __name__ == "__main__":
    main()

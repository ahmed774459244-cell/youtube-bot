"""
Bu skript SSH orqali VPS serveringizga ulanadi va botni avtomatik joylashtiradi.
Terminaldagi klaviatura muammosini butunlay chetlab o'tadi — parol shu skript ichida
yoziladi, qo'lda kiritish shart emas.

Ishlatishdan oldin:
  pip install paramiko

Ishga tushirish:
  python deploy_vps.py
"""
import paramiko
import sys

# ==================== SOZLAMALAR — o'zingiznikiga moslang ====================
VPS_IP = "13.39.137.123"
VPS_USER = "ubuntu"
VPS_PASSWORD = "x9WC@N5Pfjvqoh9#5^6uPASV"

GITHUB_REPO_URL = "https://github.com/ahmed774459244-cell/youtube-bot.git"
LOCAL_ENV_PATH = r"C:\youtube_bot\youtube_bot\.env"  # kompyuteringizdagi .env faylining yo'li
# ================================================================================


def run_command(client, command, description):
    """Bitta buyruqni serverda ishga tushiradi, natijasini ko'rsatadi."""
    print(f"\n{'='*60}")
    print(f">>> {description}")
    print(f"{'='*60}")
    stdin, stdout, stderr = client.exec_command(command, get_pty=True)

    for line in iter(stdout.readline, ""):
        print(line, end="")

    exit_status = stdout.channel.recv_exit_status()
    if exit_status != 0:
        error_output = stderr.read().decode()
        print(f"\n⚠️  Xatolik (exit code {exit_status}): {error_output}")
        return False
    return True


def main():
    print(f"🔌 {VPS_IP} serveriga ulanmoqda...")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostname=VPS_IP, username=VPS_USER, password=VPS_PASSWORD, timeout=15)
        print("✅ Muvaffaqiyatli ulandi!")
    except Exception as e:
        print(f"❌ Ulanib bo'lmadi: {e}")
        sys.exit(1)

    run_command(client, "sudo apt update -y", "Paketlar ro'yxatini yangilash")
    run_command(client, "sudo apt install -y docker.io git", "Docker va Git o'rnatish")
    run_command(client, "sudo systemctl enable docker && sudo systemctl start docker", "Docker'ni ishga tushirish")
    run_command(client, f"sudo usermod -aG docker {VPS_USER}", "Docker huquqlarini berish")

    run_command(client, f"rm -rf ~/youtube-bot && git clone {GITHUB_REPO_URL} ~/youtube-bot", "Kodni GitHub'dan yuklash")

    # 3. .env faylini kompyuteringizdan serverga yuklaymiz (SFTP orqali)
    print(f"\n{'='*60}")
    print(">>> .env faylini serverga yuklash")
    print(f"{'='*60}")
    try:
        sftp = client.open_sftp()
        sftp.put(LOCAL_ENV_PATH, "/home/ubuntu/youtube-bot/.env")
        sftp.close()
        print("✅ .env fayli muvaffaqiyatli yuklandi.")
    except Exception as e:
        print(f"❌ .env faylini yuklab bo'lmadi: {e}")
        print(f"   Tekshiring: {LOCAL_ENV_PATH} kompyuteringizda mavjudmi?")
        client.close()
        sys.exit(1)

    # Windows'da tahrirlangan .env faylida "\r" (carriage return) belgilari qolib ketishi mumkin,
    # bu esa kalitlarning oxiriga yopishib, ularni buzib qo'yadi. Shuni tozalaymiz.
    run_command(client, "sed -i 's/\\r$//' ~/youtube-bot/.env", ".env faylidagi Windows qator belgilarini tozalash")

    # 4. Docker image qurish
    run_command(client, "cd ~/youtube-bot && sudo docker build -t youtube-bot .", "Docker image qurilmoqda (bir necha daqiqa davom etishi mumkin)")

    # 5. Eski konteynerni to'xtatib, yangisini ishga tushirish
    run_command(client, "sudo docker stop youtube-bot 2>/dev/null; sudo docker rm youtube-bot 2>/dev/null; true", "Eski konteyner (agar bo'lsa) tozalanmoqda")
    run_command(
        client,
        "sudo docker run -d --name youtube-bot --restart unless-stopped --network host --env-file ~/youtube-bot/.env youtube-bot",
        "Bot ishga tushirilmoqda (doim ishlab turadigan rejimda)",
    )

    print(f"\n{'='*60}")
    print("🎉 Bot serverda ishga tushdi!")
    print("Loglarni ko'rish uchun keyinroq shuni ishlatishingiz mumkin:")
    print("  ssh ubuntu@" + VPS_IP)
    print("  sudo docker logs -f youtube-bot")
    print(f"{'='*60}")

    client.close()


if __name__ == "__main__":
    main()

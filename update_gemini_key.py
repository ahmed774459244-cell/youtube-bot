"""
Serverdagi GEMINI_API_KEY qiymatini yangilaydi va botni qayta ishga tushiradi.
Butun o'rnatishni (Docker, Git) qaytadan bajarmaydi — faqat tezkor yangilash.

Ishga tushirish:
  python update_gemini_key.py
"""
import paramiko
import sys

# ==================== SOZLAMALAR ====================
VPS_IP = "13.39.137.123"
VPS_USER = "ubuntu"
VPS_PASSWORD = "x9WC@N5Pfjvqoh9#5^6uPASV"

NEW_GEMINI_API_KEY = "AQ.Ab8RN6J7Zhm_pCCQU_SLheIRy-Ryx7P4aoJ4-mSzjccZY5p6JQ"
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

    # .env faylida GEMINI_API_KEY qatorini yangilaymiz (sed orqali)
    sed_cmd = (
        f"sed -i 's|^GEMINI_API_KEY=.*|GEMINI_API_KEY={NEW_GEMINI_API_KEY}|' "
        f"~/youtube-bot/.env"
    )
    run_command(client, sed_cmd, "Gemini kalitini .env faylida yangilash")

    # Tekshirish uchun (kalitning o'zi ko'rsatilmaydi, faqat mavjudligi)
    run_command(client, "grep -c GEMINI_API_KEY ~/youtube-bot/.env", "Tekshirish")

    # Konteynerni qayta ishga tushiramiz — .env qayta o'qilishi uchun
    run_command(client, "sudo docker stop youtube-bot", "Botni to'xtatish")
    run_command(client, "sudo docker rm youtube-bot", "Eski konteynerni o'chirish")
    run_command(
        client,
        "sudo docker run -d --name youtube-bot --restart unless-stopped --env-file ~/youtube-bot/.env youtube-bot",
        "Botni yangi kalit bilan qayta ishga tushirish",
    )

    print("\n🎉 Bot yangi Gemini kaliti bilan qayta ishga tushirildi!")
    print("Loglarni ko'rish uchun: ssh ubuntu@" + VPS_IP + " so'ng: sudo docker logs -f youtube-bot")

    client.close()


if __name__ == "__main__":
    main()

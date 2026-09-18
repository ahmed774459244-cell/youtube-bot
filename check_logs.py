"""
Serverdagi botning so'nggi loglarini ko'rsatadi — terminalga parol yozish shart emas.

Ishga tushirish:
  python check_logs.py
"""
import paramiko

VPS_IP = "13.39.137.123"
VPS_USER = "ubuntu"
VPS_PASSWORD = "x9WC@N5Pfjvqoh9#5^6uPASV"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname=VPS_IP, username=VPS_USER, password=VPS_PASSWORD, timeout=15)

stdin, stdout, stderr = client.exec_command("sudo docker logs --tail 300 youtube-bot", get_pty=True)
all_output = []
for line in iter(stdout.readline, ""):
    all_output.append(line)

# Eng muhim (sozlash) qatorlarni alohida, tepada ko'rsatamiz
print("=" * 60)
print("MUHIM SOZLASH QATORLARI:")
print("=" * 60)
found_important = False
for line in all_output:
    if "Local Bot API" in line or "Standart Telegram" in line or "Premium emoji" in line:
        print(line, end="")
        found_important = True
if not found_important:
    print("(Topilmadi — botni yaqinda qayta ishga tushirmagan bo'lishingiz mumkin, "
          "yoki bu qatorlar 300 qatordan oldinroq bo'lgan)")

print("\n" + "=" * 60)
print("OXIRGI 30 QATOR (umumiy holat):")
print("=" * 60)
for line in all_output[-30:]:
    print(line, end="")

client.close()

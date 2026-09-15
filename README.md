# AI YouTube Video Bot

Telegram orqali mavzu yuborasiz — bot skript yozadi, ovoz yaratadi, fon video/rasm topadi va hammasini bitta YouTube video qilib beradi.

## 1. Kerakli API kalitlarni olish (barchasi BEPUL)

### Telegram bot token
1. Telegram'da **@BotFather** ga yozing
2. `/newbot` buyrug'ini yuboring, bot nomini tanlang
3. Sizga beriladigan tokenni saqlab qo'ying

### Gemini API kalit (skript yozish uchun)
1. https://aistudio.google.com ga kiring
2. "Get API key" tugmasini bosing
3. Bepul limit: kuniga yetarlicha so'rov (shaxsiy loyihalar uchun yetarli)

### Pexels API kalit (fon video/rasm uchun)
1. https://www.pexels.com/api/ ga kiring, ro'yxatdan o'ting
2. API kalitni oling — bu **butunlay bepul va cheksiz** (rate-limit bilan)

## 2. O'rnatish

```bash
cd youtube_bot
pip install -r requirements.txt
```

**Muhim:** ffmpeg kompyuteringizda o'rnatilgan bo'lishi kerak:
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Windows: https://ffmpeg.org/download.html dan yuklab, PATH'ga qo'shing
```

## 3. Kalitlarni sozlash

`.env.example` faylini `.env` nomiga nusxalang va haqiqiy kalitlaringizni kiriting:

```bash
cp .env.example .env
```

`.env` faylini oching va to'ldiring:
```
TELEGRAM_BOT_TOKEN=sizning_tokeningiz
GEMINI_API_KEY=sizning_kalitingiz
PEXELS_API_KEY=sizning_kalitingiz
```

## 4. Ishga tushirish

```bash
python bot.py
```

Bot ishga tushadi. Telegram'da botingizga o'ting, `/start` bosing — pastda tugmali menyu chiqadi. "🎬 Video yaratish" tugmasini bosib, davomiylikni tanlang, so'ng mavzuni yozib yuboring.

## Fayllar tuzilishi

| Fayl | Vazifasi |
|---|---|
| `bot.py` | Telegram bot — foydalanuvchi bilan muloqot |
| `pipeline.py` | Butun jarayonni boshqaradi (skript→ovoz→video) |
| `script_generator.py` | Gemini orqali skript yozadi |
| `tts_generator.py` | Matnni ovozga aylantiradi (edge-tts) |
| `media_fetcher.py` | Pexels'dan fon video/rasm topadi |
| `video_builder.py` | ffmpeg orqali video yig'adi |
| `config.py` | Barcha sozlamalar shu yerda |

## Muhim eslatmalar

- **Ovoz tili:** edge-tts'da o'zbek tili yo'q, hozircha rus tiliga (`ru-RU-SvetlanaNeural`) sozlangan. `config.py` da `TTS_VOICE` ni o'zgartirib, boshqa tilga o'tkazishingiz mumkin. O'zbek tilida diktor kerak bo'lsa — ElevenLabs kabi pullik TTS xizmati kerak bo'ladi.
- **Sinov uchun** avval "⏱ 2 daqiqa" tugmasini tanlab tekshiring — bu tez va Gemini/Pexels limitlarini kam sarflaydi.
- **Ko'p foydalanuvchi kutilsa:** hozirgi versiya videolarni ketma-ket (bittadan) yasaydi. Katta yuklama uchun navbat tizimi (masalan Redis+Celery) qo'shish kerak bo'ladi — bu keyingi bosqich.
- **Xarajat:** Gemini va Pexels bepul, faqat server (kompyuter/VPS) ishlab turishi kerak. Demak MVP bosqichida deyarli **$0 xarajat**.

## Keyingi qadamlar (ixtiyoriy yaxshilashlar)

1. Subtitr (subtitle) qo'shish
2. Fon musiqa qo'shish
3. ~~Navbat tizimi (bir vaqtda ko'p foydalanuvchi uchun)~~ ✅ Qo'shildi — pastga qarang
4. To'lov tizimi (agar botni boshqalarga ham ochmoqchi bo'lsangiz)
5. O'zbek tilida sifatli TTS integratsiyasi

---

## Qo'shimcha: Navbat tizimi (ko'p foydalanuvchi uchun)

Bot endi bir vaqtda faqat cheklangan sondagi videoni parallel ishlaydi (standart: 2 ta). Qolgan foydalanuvchilar avtomatik navbatda kutadi va "Sizdan oldin N ta video" degan xabar ko'radi.

`.env` faylida sozlash mumkin:
```
MAX_CONCURRENT_JOBS=2
```

**Qancha qiymat qo'yish kerak — serveringiz RAM'iga qarab:**
| Server RAM | Tavsiya etilgan MAX_CONCURRENT_JOBS |
|---|---|
| 2GB | 1 |
| 4GB | 2 |
| 8GB | 3-4 |

Ko'proq qiymat = ko'proq video bir vaqtda tayyorlanadi (o'rtacha kutish vaqti qisqaradi), lekin server resurslari (RAM, CPU) shunga yarasha ko'proq band bo'ladi. Juda yuqori qiymat qo'ysangiz, server sekinlashishi yoki qulab tushishi mumkin — ehtiyot bo'ling.

---

## Qo'shimcha: 2GB fayl limiti (45MB o'rniga)

Standart Telegram serveri 50MB'dan katta faylni qabul qilmaydi, shuning uchun bot katta videolarni avtomatik siqadi. Agar siqishni butunlay yo'qotib, **to'liq sifatda 2GB gacha** fayl yuborishni xohlasangiz:

1. **my.telegram.org**'da shaxsiy Telegram hisobingiz bilan kirib, "API development tools" orqali **api_id** va **api_hash** oling
2. GitHub'dan **"Bezdarnost01/telegram-bot-api-windows"** repositoriysining tayyor `.exe` faylini yuklab, `youtube_bot/telegram-bot-api/telegram-bot-api.exe` sifatida joylashtiring
3. `.env` faylida quyidagilarni o'zgartiring:
   ```
   USE_LOCAL_API_SERVER=true
   ```
4. `start_hidden.vbs` faylini ochib, ichidagi `YOUR_API_ID` va `YOUR_API_HASH`ni haqiqiy qiymatlaringizga almashtiring

---

## Qo'shimcha: Botni oynasiz (yashirin) va avtomatik ishga tushirish

Hozirgi holatda botni ishga tushirish uchun CMD oynasini ochiq ushlab turishingiz kerak. Agar buni istamasangiz:

### A) Oynasiz ishga tushirish (qo'lda)
`start_hidden.vbs` faylini ikki marta bosing — bot va (agar sozlangan bo'lsa) local server **hech qanday ko'rinadigan oynasiz** orqa fonda ishga tushadi. To'xtatish uchun Task Manager'dan `python.exe` / `pythonw.exe` va `telegram-bot-api.exe` jarayonlarini tugatish kerak bo'ladi.

### B) Kompyuter yoqilganda avtomatik ishga tushirish
1. Windows qidiruvida **"Task Scheduler"** (Vazifalar rejalashtiruvchisi) deb yozib oching
2. O'ng tomonda **"Create Task..."** bosing
3. **"General"** bo'limida: nom bering (masalan "YouTube Bot"), **"Run whether user is logged on or not"** ni tanlang
4. **"Triggers"** bo'limida: **"New..."** → **"At log on"** ni tanlang
5. **"Actions"** bo'limida: **"New..."** → Program/script sifatida `start_hidden.vbs` faylining to'liq yo'lini ko'rsating (masalan `C:\youtube_bot\youtube_bot\start_hidden.vbs`)
6. **"OK"** bosib saqlang

Shundan keyin, kompyuter yoqilib, siz tizimga kirishingiz bilan (hech qanday oyna ochmasdan) bot avtomatik ishga tushadi va orqa fonda ishlab turadi — kompyuter yoniq turgan holda, hech narsani qo'lda ochib o'tirish shart emas.

**Eslatma:** Bot ishlashi uchun baribir **kompyuter yoqiq va internetga ulangan** bo'lishi kerak. Agar kompyuterni butunlay o'chirsangiz — bot ham to'xtaydi. Kompyuterni 24/7 o'chirmasdan ishlatish istamasangiz, botni arzon VPS (virtual server, oyiga ~$5) ga joylashtirish kerak bo'ladi — quyida qadamlar berilgan.

---

## Qo'shimcha: Botni VPS'ga (masofaviy serverga) joylashtirish

Bu — botni kompyuteringizdan mustaqil, 24/7 ishlaydigan qiladi.

### 1. Fayllarni serverga yuklash

Brauzer konsoli yoki SSH orqali serverga ulangach, loyiha fayllarini serverga yuklang. Eng oson yo'l — bu papkani (`youtube_bot`) zip qilib, keyin server konsolida:

```bash
cd /root
# faylni yuklab olish uchun WinSCP yoki Timeweb panelidagi fayl yuklash vositasidan foydalaning
unzip youtube_bot.zip
cd youtube_bot
```

### 2. `.env` faylini to'ldiring

```bash
nano .env
```

Barcha kalitlaringizni kiriting (`TELEGRAM_BOT_TOKEN`, `GEMINI_API_KEY`, `PEXELS_API_KEY`). `USE_LOCAL_API_SERVER=false` qoldiring (Linux'da 2GB serverni sozlash alohida, murakkabroq bosqich — kerak bo'lsa keyinroq qo'shamiz). Saqlash: `Ctrl+O`, Enter, `Ctrl+X`.

### 3. O'rnatish skriptini ishga tushiring

```bash
bash deploy/install.sh
```

Bu Python, ffmpeg, Docker va barcha kerakli kutubxonalarni avtomatik o'rnatadi.

### 4. (Tavsiya etiladi) 2GB fayl limitini yoqish

Windows'dagidek qo'lda `.exe` qidirish shart emas — Linux'da Docker orqali bir buyruq bilan ishga tushadi.

1. `my.telegram.org`'dan olingan `api_id` va `api_hash`ni `.env` fayliga qo'shing:
   ```
   TELEGRAM_API_ID=sizning_api_id
   TELEGRAM_API_HASH=sizning_api_hash
   ```
2. Serverni ishga tushiring:
   ```bash
   cd deploy
   docker compose --env-file ../.env up -d
   cd ..
   ```
3. `.env` faylida:
   ```
   USE_LOCAL_API_SERVER=true
   LOCAL_API_SERVER_URL=http://localhost:8081
   ```

Ishlayotganini tekshirish: `docker ps` — "telegram-bot-api" konteyneri "Up" holatida ko'rinishi kerak.

### 5. Botni "doim ishlab tursin" rejimida ishga tushiring

```bash
sudo cp deploy/youtube-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable youtube-bot
sudo systemctl start youtube-bot
```

### 6. Ishlayotganini tekshirish

```bash
sudo systemctl status youtube-bot
```

Yashil "active (running)" yozuvi chiqsa — bot ishlayapti. Loglarni ko'rish uchun:

```bash
journalctl -u youtube-bot -f
```

Shu bilan — bot endi serverda **24/7**, kompyuteringiz yoqiq yoki o'chiq bo'lishidan qat'iy nazar ishlab turadi. Server qayta yoqilsa ham (masalan yangilanishdan keyin), bot va Docker konteyneri **avtomatik qayta ishga tushadi** (`restart: always` va systemd tufayli).


## Qo'shimcha: To'lov tizimi (bepul limit + kredit sotib olish)

Bot endi har bir yangi foydalanuvchiga **50 daqiqa bepul** video balansi beradi (`.env`dagi `FREE_MINUTES` bilan sozlanadi). Tugagach, foydalanuvchi "🛒 Kredit sotib olish" tugmasi orqali qo'shimcha kredit sotib oladi.

### Buyruqlar
- "💰 Balans" tugmasi — joriy balansni ko'rsatadi
- "🛒 Kredit sotib olish" tugmasi — kredit paketlarini ko'rsatadi (narxlarni `config.py`dagi `PACKAGES` ro'yxatida o'zgartirasiz)

### To'lov usuli 1 — Qo'lda tasdiqlash (darhol ishlaydi, qo'shimcha sozlash shart emas)

1. Foydalanuvchi paket tanlaydi → "📸 To'lov skrinshotini yuborish" bosadi
2. Bot unga `.env`dagi `PAYMENT_INSTRUCTIONS` (Click raqamingiz/karta) ni ko'rsatadi
3. Foydalanuvchi to'lov qilib, skrinshot yuboradi
4. Skrinshot avtomatik ravishda **sizga** (`.env`dagi `ADMIN_TELEGRAM_ID`) "✅ Tasdiqlash / ❌ Rad etish" tugmalari bilan yuboriladi
5. Tasdiqlasangiz — foydalanuvchi balansi avtomatik yangilanadi

**Sozlash:** `.env` faylida:
```
ADMIN_TELEGRAM_ID=sizning_telegram_id_raqamingiz
```
ID'ingizni bilish uchun Telegram'da **@userinfobot** ga yozing.

### To'lov usuli 2 — Click.uz avtomatik to'lov (qo'shimcha sozlash talab qiladi)

Bu — foydalanuvchi to'lasa, hech kim aralashmasdan balans avtomatik yangilanadigan usul. Lekin buning uchun:

1. **Click bilan tadbirkor sifatida shartnoma tuzish kerak** — click.uz saytida "Biznes uchun" bo'limidan ariza qoldirasiz, ular sizga `merchant_id`, `service_id`, `secret_key` beradi
2. **Domen nomi kerak** (masalan `sizning-kanal.uz`) — bu bilan bog'liq bo'lgan **SSL sertifikat** kerak
3. Serveringizda webhook'ni ishga tushirasiz:
   ```bash
   pip install fastapi uvicorn
   uvicorn click_webhook:app --host 0.0.0.0 --port 8000
   ```
4. Nginx orqali bu portni ochiq (443, SSL bilan) manzilga yo'naltirasiz (masalan `https://sizning-kanal.uz/click/prepare`)
5. Click kabinetida shu manzillarni ko'rsatasiz:
   - Prepare URL: `https://sizning-kanal.uz/click/prepare`
   - Complete URL: `https://sizning-kanal.uz/click/complete`
6. `.env` faylida:
   ```
   CLICK_MERCHANT_ID=...
   CLICK_SERVICE_ID=...
   CLICK_SECRET_KEY=...
   ```

**Muhim:** `click_webhook.py` — umumiy hujjatlashtirilgan Click sxemasi asosida yozilgan. Haqiqiy pul bilan ishga tushirishdan oldin, Click'ning rasmiy hujjatlari (docs.click.uz) va **test (sandbox) muhitida** albatta sinab ko'ring.

Ikkala usul **bir vaqtda** ishlaydi — agar Click sozlanmagan bo'lsa, foydalanuvchiga faqat "qo'lda tasdiqlash" tugmasi ko'rsatiladi, Click sozlangach ikkalasi ham chiqadi.

## Qo'shimcha: Tezkor to'ldirish — SMS orqali avtomatik aniqlash (Click shartnomasisiz)

Bu — Click bilan rasmiy shartnoma tuzmasdan, shaxsiy kartangiz orqali **avtomatik** to'lov qabul qilish usuli. Foydalanuvchi istalgan summani kiritadi, kartangizga to'laydi, bank yuborgan SMS orqali avtomatik tasdiqlanadi.

### Qanday ishlaydi
1. Foydalanuvchi "💳 O'zim summa kiritaman" tugmasini bosadi, summani yozadi (masalan `10000`)
2. Bot unga karta raqamingizni va aynan shu summani ko'rsatadi
3. Foydalanuvchi to'laydi → bankingiz **sizning telefoningizga** SMS yuboradi
4. Telefoningizdagi SMS-forward ilovasi shu SMS matnini serverga yuboradi
5. Server SMS ichidan summani o'qib, mos so'rovni topib, **balansni avtomatik to'ldiradi**

### Sozlash

**1. `.env` faylida:**
```
PAYMENT_CARD_NUMBER=8600 1234 5678 9012
PAYMENT_CARD_OWNER=Ism Familiya
RATE_PER_MINUTE=500
SMS_WEBHOOK_SECRET=uzun-tasodifiy-maxfiy-parol
```
`RATE_PER_MINUTE` — 1 video-daqiqasi necha so'm turishini belgilaydi (masalan 500 so'm/daqiqa = 10,000 so'm to'lasa 20 daqiqa beriladi).

**2. Serverda webhook'ni ishga tushiring:**
```bash
pip install fastapi uvicorn
uvicorn sms_webhook:app --host 0.0.0.0 --port 8001
```
(Doim ishlab tursin desangiz, buni ham `deploy/youtube-bot.service` kabi systemd xizmatiga aylantirish mumkin — so'rasangiz tayyorlab beraman.)

**3. Telefoningizga SMS-forward ilovasini o'rnating**
Play Market'dan **"SMS Forwarder"** (yoki shunga o'xshash) ilovani yuklab oling. Sozlamalarida:
- Manzil: `http://SIZNING_SERVER_IP:8001/sms/incoming`
- So'rov turi: POST, JSON
- Yuboriladigan ma'lumot: `{"text": "<SMS matni>", "secret": "<SMS_WEBHOOK_SECRET qiymati>"}`

*(Ilovalar formatini turlicha so'rashi mumkin — ilova sozlamalarida "custom body"/"JSON template" bo'limida yuqoridagi formatga moslang.)*

### Muhim eslatmalar
- Bu usul **bankingiz haqiqatan SMS yuborishiga** bog'liq — ba'zi banklar SMS xizmatini pullik qiladi, tekshirib ko'ring
- Telefoningiz **doim yoqiq va internetga ulangan** bo'lishi kerak (SMS'ni forward qilish uchun)
- Xavfsizlik uchun `SMS_WEBHOOK_SECRET`ni albatta uzun va tasodifiy qiling — aks holda boshqa birov soxta SMS yuborib, bepul balans olishi mumkin
- Agar ikkita foydalanuvchi **aynan bir xil summani** bir vaqtda to'lasa, tizim ularni ketma-ketlik bo'yicha (eng birinchi so'ragan) mosligini hisoblaydi — juda kam uchraydigan holat, lekin bilib qo'ying

## Qo'shimcha: AI-generatsiya original rasmlar (Pexels o'rniga)

Endi bot, standart holatda, har bir sahna uchun Pexels'dan tayyor video/rasm olish o'rniga, **Gemini orqali original rasm chizadi**. Bu:
- **Mualliflik huquqi/qayta ishlatilgan kontent xavfini kamaytiradi** — YouTube monetizatsiyasi uchun foydali (avvalgi javobda tushuntirilgan "reused content" siyosati)
- Videoni **100% original** qiladi — hech kim boshqa joydan olinmagan

### Sozlash
`.env` faylida:
```
USE_AI_IMAGES=true
```
`false` qilsangiz, eski tartib (Pexels stock) ishlatiladi.

### Narxi
Bepul emas — har bir rasm taxminan **$0.04-0.07** turadi (Gemini narxiga qarab). 10 daqiqalik video (~40 sahna) uchun rasm xarajati **~$2-3** atrofida bo'ladi. Bu — Pexels'dan (butunlay bepul) qimmatroq, lekin originallik va monetizatsiya xavfsizligi evaziga.

### Zaxira reja (avtomatik)
Agar AI rasm generatsiyasi biror sababdan (limit, xatolik) ishlamasa, bot **avtomatik ravishda Pexels'ga qaytadi** — hech qachon video yaratish to'xtab qolmaydi.

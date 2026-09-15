"""
Bot interfeysi matnlarini turli tillarda saqlaydi.
DIQQAT: Bu — bot MENYUSINING tili (tugmalar, xabarlar). Video ICHIDAGI skript/ovoz tili
bundan MUSTAQIL — u alohida (video yaratish oqimi ichida) tanlanadi.
"""

TEXTS = {
    "uz": {
        "welcome": (
            "👋 Salom! Men AI yordamida YouTube uchun video yarataman.\n\n"
            "🎁 Sizga {free} daqiqalik bepul video balansi berildi!\n\n"
            "Pastdagi tugmalardan foydalaning 👇"
        ),
        "btn_create_video": "🎬 Video yaratish",
        "btn_balance": "💰 Balans",
        "btn_buy": "🛒 Kredit sotib olish",
        "btn_language": "🌐 Bot tili",
        "btn_back": "🔙 Orqaga",
        "btn_cancel": "❌ Bekor qilish",
        "balance_msg": "💰 Balansingiz: <b>{balance} daqiqa</b>\n\nKo'proq kerak bo'lsa: {buy_btn}",
        "choose_interface_language": "🌐 Joriy bot tili: <b>{lang}</b>\n\nYangi tilni tanlang:",
        "interface_language_selected": "✅ Bot tili tanlandi: <b>{lang}</b>",
        "choose_video_language": "🎬 Qaysi tilda video (skript va ovoz) yaratilsin?",
        "video_language_selected": "✅ Video tili: <b>{lang}</b>\n\n🎨 Endi uslubni tanlang:",
        "choose_visual_style": "🎨 Video qanday uslubda bo'lsin?",
        "visual_style_selected": "✅ Uslub: <b>{style}</b>\n\n⏱ Endi davomiylikni tanlang:",
        "duration_selected": "✅ Tanlandi: {minutes} daqiqalik video ({lang}).\n\n📝 Endi video mavzusini yozing:",
        "back_to_menu": "Asosiy menyu 👇",
        "cancelled": "Bekor qilindi. Asosiy menyu 👇",
        "use_buttons_prompt": "Video yaratish uchun pastdagi tugmalardan foydalaning 👇",
        "insufficient_balance": "❌ Balansingiz yetarli emas.\nKerak: {minutes} daqiqa | Balansingiz: {balance} daqiqa\n\nKredit sotib olish uchun: {buy_btn}",
        "queue_msg": "⏳ Navbatdasiz — sizdan oldin {position} ta video ishlanmoqda/kutmoqda. Iltimos kuting, navbat kelganda avtomatik boshlanadi.",
        "preparing_msg": "🎬 \"{topic}\" mavzusida {minutes} daqiqalik video ({lang}) tayyorlanmoqda...",
        "sending_msg": "📤 Video yuborilmoqda...",
        "resend_retry_msg": "📤 Yuborishda vaqt tugadi, qayta urinilmoqda ({attempt}/3)...",
        "video_ready_caption": "✅ \"{topic}\" — tayyor!",
        "error_msg": "❌ Xatolik yuz berdi: {error}\nBalansingiz qaytarildi. Iltimos qaytadan urinib ko'ring.",
        "buy_header": "🛒 Qaysi paketni sotib olmoqchisiz?",
        "package_btn": "{minutes} daqiqa — {price} so'm",
        "package_details": "<b>{minutes} daqiqa — {price} so'm</b>\n\nTo'lov usulini tanlang:",
        "pay_click_btn": "💳 Click orqali to'lash",
        "pay_manual_btn": "📸 To'lov skrinshotini yuborish",
        "manual_pay_instructions": "💳 <b>{price} so'm</b> to'lang:\n\n{instructions}\n\nTo'lovni amalga oshirgach, shu yerga to'lov skrinshotini (rasm sifatida) yuboring. Men uni tekshirib, balansingizni yangilayman.",
        "screenshot_received": "✅ Skrinshot qabul qilindi! Tez orada tekshirilib, balansingiz yangilanadi.",
        "payment_approved": "✅ To'lovingiz tasdiqlandi! Balansingizga {minutes} daqiqa qo'shildi.",
        "payment_rejected": "❌ To'lovingiz tasdiqlanmadi. Skrinshot noto'g'ri yoki to'lov topilmadi. Iltimos qayta urinib ko'ring yoki admin bilan bog'laning.",
        "buy_choose_method": "🛒 Qanday to'ldirmoqchisiz?",
        "btn_fixed_packages": "📦 Tayyor paketlar",
        "btn_custom_amount": "💳 O'zim summa kiritaman",
        "ask_topup_amount": "💰 Necha so'mlik to'lov qilmoqchisiz?\n\nMinimal: {min_amount} so'm\nFaqat raqam kiriting. Masalan: 10000",
        "invalid_amount": "❌ Noto'g'ri summa. Faqat raqam kiriting (minimal {min_amount} so'm). Masalan: 10000",
        "topup_instructions": (
            "💳 To'lov karta: <b>{card}</b>\n"
            "{card_owner_line}"
            "💰 Miqdori: <b>{amount} so'm</b>\n"
            "🎁 Balansingizga qo'shiladi: <b>{minutes} daqiqa</b>\n\n"
            "✅ To'lov qilib bo'lganingizdan so'ng, avtomatik aniqlanadi (odatda 1-5 daqiqa ichida).\n"
            "⚠️ Aynan <b>{amount} so'm</b> yuboring — undan ortiq yoki kam emas."
        ),
        "topup_auto_confirmed": "✅ To'lovingiz avtomatik aniqlandi! Balansingizga {minutes} daqiqa qo'shildi.",
    },
    "en": {
        "welcome": (
            "👋 Hi! I create YouTube videos using AI.\n\n"
            "🎁 You've been given {free} minutes of free video balance!\n\n"
            "Use the buttons below 👇"
        ),
        "btn_create_video": "🎬 Create video",
        "btn_balance": "💰 Balance",
        "btn_buy": "🛒 Buy credits",
        "btn_language": "🌐 Bot language",
        "btn_back": "🔙 Back",
        "btn_cancel": "❌ Cancel",
        "balance_msg": "💰 Your balance: <b>{balance} minutes</b>\n\nNeed more? {buy_btn}",
        "choose_interface_language": "🌐 Current bot language: <b>{lang}</b>\n\nChoose a new language:",
        "interface_language_selected": "✅ Bot language set to: <b>{lang}</b>",
        "choose_video_language": "🎬 Which language should the video (script and voice) be in?",
        "video_language_selected": "✅ Video language: <b>{lang}</b>\n\n🎨 Now choose a style:",
        "choose_visual_style": "🎨 What style should the video be in?",
        "visual_style_selected": "✅ Style: <b>{style}</b>\n\n⏱ Now choose the duration:",
        "duration_selected": "✅ Selected: {minutes}-minute video ({lang}).\n\n📝 Now type the video topic:",
        "back_to_menu": "Main menu 👇",
        "cancelled": "Cancelled. Main menu 👇",
        "use_buttons_prompt": "Please use the buttons below to create a video 👇",
        "insufficient_balance": "❌ Insufficient balance.\nNeeded: {minutes} min | Your balance: {balance} min\n\nTo buy credits: {buy_btn}",
        "queue_msg": "⏳ You're in the queue — {position} video(s) ahead of you. Please wait, it will start automatically.",
        "preparing_msg": "🎬 Preparing a {minutes}-minute video ({lang}) on \"{topic}\"...",
        "sending_msg": "📤 Sending the video...",
        "resend_retry_msg": "📤 Upload timed out, retrying ({attempt}/3)...",
        "video_ready_caption": "✅ \"{topic}\" — ready!",
        "error_msg": "❌ An error occurred: {error}\nYour balance has been refunded. Please try again.",
        "buy_header": "🛒 Which package would you like to buy?",
        "package_btn": "{minutes} min — {price} so'm",
        "package_details": "<b>{minutes} min — {price} so'm</b>\n\nChoose a payment method:",
        "pay_click_btn": "💳 Pay with Click",
        "pay_manual_btn": "📸 Send payment screenshot",
        "manual_pay_instructions": "💳 Please pay <b>{price} so'm</b>:\n\n{instructions}\n\nAfter paying, send a screenshot (as a photo) here. I'll verify it and update your balance.",
        "screenshot_received": "✅ Screenshot received! It will be reviewed shortly and your balance updated.",
        "payment_approved": "✅ Your payment was approved! {minutes} minutes added to your balance.",
        "payment_rejected": "❌ Your payment was not approved. The screenshot was invalid or the payment wasn't found. Please try again or contact the admin.",
        "buy_choose_method": "🛒 How would you like to top up?",
        "btn_fixed_packages": "📦 Fixed packages",
        "btn_custom_amount": "💳 Enter custom amount",
        "ask_topup_amount": "💰 How much would you like to pay?\n\nMinimum: {min_amount} so'm\nEnter numbers only. Example: 10000",
        "invalid_amount": "❌ Invalid amount. Enter numbers only (minimum {min_amount} so'm). Example: 10000",
        "topup_instructions": (
            "💳 Pay to card: <b>{card}</b>\n"
            "{card_owner_line}"
            "💰 Amount: <b>{amount} so'm</b>\n"
            "🎁 Will be added to your balance: <b>{minutes} minutes</b>\n\n"
            "✅ After paying, it will be detected automatically (usually within 1-5 minutes).\n"
            "⚠️ Send exactly <b>{amount} so'm</b> — not more, not less."
        ),
        "topup_auto_confirmed": "✅ Your payment was automatically detected! {minutes} minutes added to your balance.",
    },
    "ru": {
        "welcome": (
            "👋 Привет! Я создаю видео для YouTube с помощью ИИ.\n\n"
            "🎁 Вам начислено {free} минут бесплатного баланса!\n\n"
            "Используйте кнопки ниже 👇"
        ),
        "btn_create_video": "🎬 Создать видео",
        "btn_balance": "💰 Баланс",
        "btn_buy": "🛒 Купить кредиты",
        "btn_language": "🌐 Язык бота",
        "btn_back": "🔙 Назад",
        "btn_cancel": "❌ Отмена",
        "balance_msg": "💰 Ваш баланс: <b>{balance} мин.</b>\n\nНужно больше? {buy_btn}",
        "choose_interface_language": "🌐 Текущий язык бота: <b>{lang}</b>\n\nВыберите новый язык:",
        "interface_language_selected": "✅ Язык бота установлен: <b>{lang}</b>",
        "choose_video_language": "🎬 На каком языке создать видео (сценарий и озвучка)?",
        "video_language_selected": "✅ Язык видео: <b>{lang}</b>\n\n🎨 Теперь выберите стиль:",
        "choose_visual_style": "🎨 В каком стиле сделать видео?",
        "visual_style_selected": "✅ Стиль: <b>{style}</b>\n\n⏱ Теперь выберите длительность:",
        "duration_selected": "✅ Выбрано: видео на {minutes} мин. ({lang}).\n\n📝 Теперь напишите тему видео:",
        "back_to_menu": "Главное меню 👇",
        "cancelled": "Отменено. Главное меню 👇",
        "use_buttons_prompt": "Для создания видео используйте кнопки ниже 👇",
        "insufficient_balance": "❌ Недостаточно баланса.\nНужно: {minutes} мин. | Ваш баланс: {balance} мин.\n\nЧтобы купить кредиты: {buy_btn}",
        "queue_msg": "⏳ Вы в очереди — перед вами {position} видео. Пожалуйста, подождите, начнётся автоматически.",
        "preparing_msg": "🎬 Готовится видео на {minutes} мин. ({lang}) на тему \"{topic}\"...",
        "sending_msg": "📤 Видео отправляется...",
        "resend_retry_msg": "📤 Время ожидания истекло, повторная попытка ({attempt}/3)...",
        "video_ready_caption": "✅ \"{topic}\" — готово!",
        "error_msg": "❌ Произошла ошибка: {error}\nБаланс возвращён. Пожалуйста, попробуйте снова.",
        "buy_header": "🛒 Какой пакет хотите купить?",
        "package_btn": "{minutes} мин. — {price} сум",
        "package_details": "<b>{minutes} мин. — {price} сум</b>\n\nВыберите способ оплаты:",
        "pay_click_btn": "💳 Оплатить через Click",
        "pay_manual_btn": "📸 Отправить скриншот оплаты",
        "manual_pay_instructions": "💳 Оплатите <b>{price} сум</b>:\n\n{instructions}\n\nПосле оплаты отправьте сюда скриншот (фото). Я проверю и обновлю баланс.",
        "screenshot_received": "✅ Скриншот получен! Скоро будет проверен, и баланс обновится.",
        "payment_approved": "✅ Ваш платёж подтверждён! На баланс добавлено {minutes} мин.",
        "payment_rejected": "❌ Платёж не подтверждён. Скриншот неверный или платёж не найден. Попробуйте снова или свяжитесь с администратором.",
        "buy_choose_method": "🛒 Как хотите пополнить баланс?",
        "btn_fixed_packages": "📦 Готовые пакеты",
        "btn_custom_amount": "💳 Ввести свою сумму",
        "ask_topup_amount": "💰 Сколько сум хотите оплатить?\n\nМинимум: {min_amount} сум\nВведите только цифры. Например: 10000",
        "invalid_amount": "❌ Неверная сумма. Введите только цифры (минимум {min_amount} сум). Например: 10000",
        "topup_instructions": (
            "💳 Оплатите на карту: <b>{card}</b>\n"
            "{card_owner_line}"
            "💰 Сумма: <b>{amount} сум</b>\n"
            "🎁 На баланс будет начислено: <b>{minutes} мин.</b>\n\n"
            "✅ После оплаты платёж будет обнаружен автоматически (обычно в течение 1-5 минут).\n"
            "⚠️ Отправьте ровно <b>{amount} сум</b> — не больше и не меньше."
        ),
        "topup_auto_confirmed": "✅ Ваш платёж обнаружен автоматически! На баланс добавлено {minutes} мин.",
    },
}

DEFAULT_UI_LANG = "uz"

# Interfeys tili tanlash tugmalari (har doim shu 3 til, tugma matni o'zgarmaydi)
UI_LANGUAGE_BUTTONS = {
    "uz": "🇺🇿 O'zbekcha",
    "en": "🇬🇧 English",
    "ru": "🇷🇺 Русский",
}
UI_LANG_BUTTON_TO_KEY = {v: k for k, v in UI_LANGUAGE_BUTTONS.items()}


def t(ui_lang: str, key: str, **kwargs) -> str:
    """Berilgan interfeys tilida matnni qaytaradi, kerakli joylarga qiymatlarni qo'yadi."""
    lang_dict = TEXTS.get(ui_lang, TEXTS[DEFAULT_UI_LANG])
    template = lang_dict.get(key, TEXTS[DEFAULT_UI_LANG].get(key, key))
    return template.format(**kwargs) if kwargs else template

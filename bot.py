"""
Telegram bot — foydalanuvchidan mavzu qabul qiladi, video yaratadi va yuboradi.
Ikki xil til mustaqil: BOT INTERFEYSI tili (tugmalar/xabarlar) va VIDEO tili (skript/ovoz).
Barcha boshqaruv tugmalar orqali, "/" buyruqlarsiz.
Ishga tushirish: python bot.py
"""
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message, FSInputFile, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
)
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer

import db
from i18n import t, TEXTS, DEFAULT_UI_LANG, UI_LANGUAGE_BUTTONS, UI_LANG_BUTTON_TO_KEY
from config import (
    TELEGRAM_BOT_TOKEN, USE_LOCAL_API_SERVER, LOCAL_API_SERVER_URL, MAX_CONCURRENT_JOBS,
    FREE_MINUTES, PACKAGES, ADMIN_TELEGRAM_ID, PAYMENT_INSTRUCTIONS,
    CLICK_ENABLED, CLICK_MERCHANT_ID, CLICK_SERVICE_ID,
    PAYMENT_CARD_NUMBER, PAYMENT_CARD_OWNER, RATE_PER_MINUTE, MIN_TOPUP_AMOUNT,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("bot_log.txt", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

UPLOAD_TIMEOUT_SECONDS = 1200
if USE_LOCAL_API_SERVER:
    logger.info(f"Local Bot API server ishlatilyapti: {LOCAL_API_SERVER_URL} (2GB gacha fayl limiti)")
    api_server = TelegramAPIServer.from_base(LOCAL_API_SERVER_URL, is_local=True)
    session = AiohttpSession(api=api_server, timeout=UPLOAD_TIMEOUT_SECONDS)
else:
    logger.info("Standart Telegram serveri ishlatilyapti (50MB fayl limiti)")
    session = AiohttpSession(timeout=UPLOAD_TIMEOUT_SECONDS)

bot = Bot(token=TELEGRAM_BOT_TOKEN, session=session, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

db.init_db()

# --- VIDEO tili (skript + ovoz) — bot interfeysi tilidan MUSTAQIL ---
LANGUAGES = {
    "uz": {"voice": "uz-UZ-SardorNeural", "script_lang": "Uzbek", "label": "O'zbekcha"},
    "en": {"voice": "en-US-AriaNeural", "script_lang": "English", "label": "English"},
    "ru": {"voice": "ru-RU-SvetlanaNeural", "script_lang": "Russian", "label": "Русский"},
}
VIDEO_LANG_BUTTONS = {
    "uz": "🎙 O'zbekcha video",
    "en": "🎙 English video",
    "ru": "🎙 Видео на русском",
}
VIDEO_LANG_BUTTON_TO_KEY = {v: k for k, v in VIDEO_LANG_BUTTONS.items()}

DURATION_BUTTONS = {
    "⏱ 2 min": 2,
    "⏱ 5 min": 5,
    "⏱ 10 min": 10,
}

# Vizual uslub: Stock (Pexels tayyor video/rasm) yoki Multfilm (AI chizgan, harakatli-kamera uslubi)
STYLE_BUTTONS = {
    "stock": "📷 Stock",
    "cartoon": "🎨 Multfilm",
}
STYLE_BUTTON_TO_KEY = {v: k for k, v in STYLE_BUTTONS.items()}
STYLE_LABELS = {"stock": "Stock", "cartoon": "Multfilm"}
# Har bir uslub uchun: use_ai_images qiymati (fetch_media_for_scene'ga uzatiladi)
STYLE_USE_AI_IMAGES = {"stock": False, "cartoon": True}

# Har bir asosiy tugma barcha interfeys tillaridagi variantlarini o'z ichiga oladi —
# shunda foydalanuvchi qaysi tilda ko'rayotgan bo'lsa ham tugma to'g'ri ishlaydi.
BTN_SETS = {
    "create_video": {TEXTS[l]["btn_create_video"] for l in TEXTS},
    "balance": {TEXTS[l]["btn_balance"] for l in TEXTS},
    "buy": {TEXTS[l]["btn_buy"] for l in TEXTS},
    "language": {TEXTS[l]["btn_language"] for l in TEXTS},
    "back": {TEXTS[l]["btn_back"] for l in TEXTS},
    "cancel": {TEXTS[l]["btn_cancel"] for l in TEXTS},
}

# Har bir foydalanuvchi uchun necha daqiqalik video tanlanganini saqlaydi
user_duration = {}
# Bot interfeysi tili: uz | en | ru
user_ui_language = {}
# Video tili: uz | en | ru
user_video_language = {}
# Har bir foydalanuvchi uchun vizual uslubni saqlaydi: stock | cartoon
user_visual_style = {}
# Har bir foydalanuvchi hozir qaysi bosqichda turganini saqlaydi
user_state = {}         # idle | choosing_video_language | choosing_visual_style | choosing_duration | ready_for_topic
awaiting_payment_proof = {}  # {user_id: package_id}

job_semaphore = asyncio.Semaphore(MAX_CONCURRENT_JOBS)
_waiting_count = 0
_waiting_lock = asyncio.Lock()


def _ui(user_id: int) -> str:
    return user_ui_language.get(user_id, DEFAULT_UI_LANG)


def main_menu_kb(ui_lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t(ui_lang, "btn_create_video"))],
            [KeyboardButton(text=t(ui_lang, "btn_balance")), KeyboardButton(text=t(ui_lang, "btn_buy"))],
            [KeyboardButton(text=t(ui_lang, "btn_language"))],
        ],
        resize_keyboard=True,
    )


def video_language_menu_kb(ui_lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=VIDEO_LANG_BUTTONS["uz"])],
            [KeyboardButton(text=VIDEO_LANG_BUTTONS["en"])],
            [KeyboardButton(text=VIDEO_LANG_BUTTONS["ru"])],
            [KeyboardButton(text=t(ui_lang, "btn_back"))],
        ],
        resize_keyboard=True,
    )


def style_menu_kb(ui_lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=STYLE_BUTTONS["stock"]), KeyboardButton(text=STYLE_BUTTONS["cartoon"])],
            [KeyboardButton(text=t(ui_lang, "btn_back"))],
        ],
        resize_keyboard=True,
    )


def duration_menu_kb(ui_lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=k) for k in list(DURATION_BUTTONS.keys())[:2]],
            [KeyboardButton(text=list(DURATION_BUTTONS.keys())[2])],
            [KeyboardButton(text=t(ui_lang, "btn_back"))],
        ],
        resize_keyboard=True,
    )


def interface_language_menu_kb(ui_lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=UI_LANGUAGE_BUTTONS["uz"])],
            [KeyboardButton(text=UI_LANGUAGE_BUTTONS["en"])],
            [KeyboardButton(text=UI_LANGUAGE_BUTTONS["ru"])],
            [KeyboardButton(text=t(ui_lang, "btn_back"))],
        ],
        resize_keyboard=True,
    )


def cancel_menu_kb(ui_lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=t(ui_lang, "btn_cancel"))]], resize_keyboard=True)


def _fmt_price(price: int) -> str:
    return f"{price:,}".replace(",", " ")


# ============================== ASOSIY MENYU ==============================

@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    db.get_or_create_user(user_id, FREE_MINUTES)
    user_state[user_id] = "idle"
    ui_lang = _ui(user_id)
    await message.answer(
        t(ui_lang, "welcome", free=f"{FREE_MINUTES:.0f}"),
        reply_markup=main_menu_kb(ui_lang),
    )


@dp.message(F.text.in_(BTN_SETS["balance"]))
async def on_balance_button(message: Message):
    ui_lang = _ui(message.from_user.id)
    balance = db.get_or_create_user(message.from_user.id, FREE_MINUTES)
    await message.answer(
        t(ui_lang, "balance_msg", balance=f"{balance:.1f}", buy_btn=t(ui_lang, "btn_buy")),
        reply_markup=main_menu_kb(ui_lang),
    )


@dp.message(F.text.in_(BTN_SETS["language"]))
async def on_language_button(message: Message):
    ui_lang = _ui(message.from_user.id)
    await message.answer(
        t(ui_lang, "choose_interface_language", lang=UI_LANGUAGE_BUTTONS[ui_lang]),
        reply_markup=interface_language_menu_kb(ui_lang),
    )


@dp.message(F.text.in_(UI_LANG_BUTTON_TO_KEY.keys()))
async def on_interface_language_selected(message: Message):
    user_id = message.from_user.id
    new_lang = UI_LANG_BUTTON_TO_KEY[message.text]
    user_ui_language[user_id] = new_lang
    await message.answer(
        t(new_lang, "interface_language_selected", lang=UI_LANGUAGE_BUTTONS[new_lang]),
        reply_markup=main_menu_kb(new_lang),
    )


@dp.message(F.text.in_(BTN_SETS["create_video"]))
async def on_create_video_button(message: Message):
    user_id = message.from_user.id
    ui_lang = _ui(user_id)
    user_state[user_id] = "choosing_video_language"
    await message.answer(
        t(ui_lang, "choose_video_language"),
        reply_markup=video_language_menu_kb(ui_lang),
    )


@dp.message(F.text.in_(VIDEO_LANG_BUTTON_TO_KEY.keys()))
async def on_video_language_selected(message: Message):
    user_id = message.from_user.id
    ui_lang = _ui(user_id)
    video_lang_key = VIDEO_LANG_BUTTON_TO_KEY[message.text]
    user_video_language[user_id] = video_lang_key
    user_state[user_id] = "choosing_visual_style"
    await message.answer(
        t(ui_lang, "video_language_selected", lang=LANGUAGES[video_lang_key]["label"]),
        reply_markup=style_menu_kb(ui_lang),
    )


@dp.message(F.text.in_(STYLE_BUTTON_TO_KEY.keys()))
async def on_visual_style_selected(message: Message):
    user_id = message.from_user.id
    ui_lang = _ui(user_id)
    style_key = STYLE_BUTTON_TO_KEY[message.text]
    user_visual_style[user_id] = style_key
    user_state[user_id] = "choosing_duration"
    await message.answer(
        t(ui_lang, "visual_style_selected", style=STYLE_LABELS[style_key]),
        reply_markup=duration_menu_kb(ui_lang),
    )


@dp.message(F.text.in_(DURATION_BUTTONS.keys()))
async def on_duration_selected(message: Message):
    user_id = message.from_user.id
    ui_lang = _ui(user_id)
    minutes = DURATION_BUTTONS[message.text]
    user_duration[user_id] = minutes
    user_state[user_id] = "ready_for_topic"
    video_lang_key = user_video_language.get(user_id, "uz")
    await message.answer(
        t(ui_lang, "duration_selected", minutes=minutes, lang=LANGUAGES[video_lang_key]["label"]),
        reply_markup=cancel_menu_kb(ui_lang),
    )


@dp.message(F.text.in_(BTN_SETS["back"]))
async def on_back_button(message: Message):
    user_id = message.from_user.id
    ui_lang = _ui(user_id)
    user_state[user_id] = "idle"
    await message.answer(t(ui_lang, "back_to_menu"), reply_markup=main_menu_kb(ui_lang))


@dp.message(F.text.in_(BTN_SETS["cancel"]))
async def on_cancel_button(message: Message):
    user_id = message.from_user.id
    ui_lang = _ui(user_id)
    user_state[user_id] = "idle"
    await message.answer(t(ui_lang, "cancelled"), reply_markup=main_menu_kb(ui_lang))


# ============================== TO'LOV TIZIMI ==============================

@dp.message(F.text.in_(BTN_SETS["buy"]))
async def on_buy_button(message: Message):
    ui_lang = _ui(message.from_user.id)
    buttons = [
        [InlineKeyboardButton(text=t(ui_lang, "btn_custom_amount"), callback_data="topup_custom")],
        [InlineKeyboardButton(text=t(ui_lang, "btn_fixed_packages"), callback_data="topup_fixed")],
    ]
    await message.answer(t(ui_lang, "buy_choose_method"), reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))


@dp.callback_query(F.data == "topup_fixed")
async def on_topup_fixed(callback: CallbackQuery):
    ui_lang = _ui(callback.from_user.id)
    buttons = [
        [InlineKeyboardButton(
            text=t(ui_lang, "package_btn", minutes=f"{pkg['minutes']:.0f}", price=_fmt_price(pkg["price"])),
            callback_data=f"buy:{pkg['id']}",
        )]
        for pkg in PACKAGES
    ]
    await callback.message.answer(t(ui_lang, "buy_header"), reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))
    await callback.answer()


@dp.callback_query(F.data == "topup_custom")
async def on_topup_custom(callback: CallbackQuery):
    user_id = callback.from_user.id
    ui_lang = _ui(user_id)
    user_state[user_id] = "awaiting_topup_amount"
    await callback.message.answer(t(ui_lang, "ask_topup_amount", min_amount=_fmt_price(MIN_TOPUP_AMOUNT)))
    await callback.answer()


@dp.callback_query(F.data.startswith("buy:"))
async def on_package_selected(callback: CallbackQuery):
    ui_lang = _ui(callback.from_user.id)
    package_id = callback.data.split(":", 1)[1]
    package = next((p for p in PACKAGES if p["id"] == package_id), None)
    if not package:
        await callback.answer("...", show_alert=True)
        return

    buttons = []
    if CLICK_ENABLED:
        merchant_trans_id = db.create_click_order(callback.from_user.id, package_id, package["minutes"], package["price"])
        click_url = (
            f"https://my.click.uz/services/pay?service_id={CLICK_SERVICE_ID}"
            f"&merchant_id={CLICK_MERCHANT_ID}&amount={package['price']}"
            f"&transaction_param={merchant_trans_id}"
        )
        buttons.append([InlineKeyboardButton(text=t(ui_lang, "pay_click_btn"), url=click_url)])

    buttons.append([InlineKeyboardButton(text=t(ui_lang, "pay_manual_btn"), callback_data=f"manual:{package_id}")])

    await callback.message.answer(
        t(ui_lang, "package_details", minutes=f"{package['minutes']:.0f}", price=_fmt_price(package["price"])),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("manual:"))
async def on_manual_payment_selected(callback: CallbackQuery):
    ui_lang = _ui(callback.from_user.id)
    package_id = callback.data.split(":", 1)[1]
    package = next((p for p in PACKAGES if p["id"] == package_id), None)
    if not package:
        await callback.answer("...", show_alert=True)
        return

    awaiting_payment_proof[callback.from_user.id] = package_id
    await callback.message.answer(
        t(ui_lang, "manual_pay_instructions", price=_fmt_price(package["price"]), instructions=PAYMENT_INSTRUCTIONS)
    )
    await callback.answer()


@dp.message(F.photo)
async def on_payment_screenshot(message: Message):
    user_id = message.from_user.id
    ui_lang = _ui(user_id)
    package_id = awaiting_payment_proof.get(user_id)
    if not package_id:
        return

    package = next((p for p in PACKAGES if p["id"] == package_id), None)
    if not package:
        return

    del awaiting_payment_proof[user_id]
    photo_file_id = message.photo[-1].file_id
    payment_id = db.create_pending_payment(user_id, package_id, package["minutes"], package["price"], photo_file_id)

    await message.answer(t(ui_lang, "screenshot_received"))

    if ADMIN_TELEGRAM_ID:
        admin_buttons = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="✅ Approve", callback_data=f"approve:{payment_id}"),
            InlineKeyboardButton(text="❌ Reject", callback_data=f"reject:{payment_id}"),
        ]])
        await bot.send_photo(
            ADMIN_TELEGRAM_ID,
            photo_file_id,
            caption=(
                f"🆕 New payment request\n"
                f"User: {user_id} (@{message.from_user.username or '-'})\n"
                f"Package: {package['minutes']:.0f} min — {_fmt_price(package['price'])} so'm\n"
                f"Payment ID: {payment_id}"
            ),
            reply_markup=admin_buttons,
        )


@dp.callback_query(F.data.startswith("approve:"))
async def on_admin_approve(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_TELEGRAM_ID:
        await callback.answer("Admin only.", show_alert=True)
        return

    payment_id = int(callback.data.split(":", 1)[1])
    payment = db.get_pending_payment(payment_id)
    if not payment or payment["status"] != "pending":
        await callback.answer("Already processed.", show_alert=True)
        return

    db.add_balance(payment["user_id"], payment["minutes"])
    db.set_payment_status(payment_id, "approved")

    await callback.message.edit_caption(caption=callback.message.caption + "\n\n✅ APPROVED")
    user_ui = _ui(payment["user_id"])
    await bot.send_message(payment["user_id"], t(user_ui, "payment_approved", minutes=f"{payment['minutes']:.0f}"))
    await callback.answer("Approved.")


@dp.callback_query(F.data.startswith("reject:"))
async def on_admin_reject(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_TELEGRAM_ID:
        await callback.answer("Admin only.", show_alert=True)
        return

    payment_id = int(callback.data.split(":", 1)[1])
    payment = db.get_pending_payment(payment_id)
    if not payment or payment["status"] != "pending":
        await callback.answer("Already processed.", show_alert=True)
        return

    db.set_payment_status(payment_id, "rejected")
    await callback.message.edit_caption(caption=callback.message.caption + "\n\n❌ REJECTED")
    user_ui = _ui(payment["user_id"])
    await bot.send_message(payment["user_id"], t(user_ui, "payment_rejected"))
    await callback.answer("Rejected.")


# ============================== VIDEO YARATISH ==============================

@dp.message(F.text)
async def handle_topic(message: Message):
    global _waiting_count

    user_id = message.from_user.id
    ui_lang = _ui(user_id)
    topic = message.text.strip()

    # --- "O'zim summa kiritaman" oqimi: foydalanuvchi summani yozadi ---
    if user_state.get(user_id) == "awaiting_topup_amount":
        cleaned = topic.replace(" ", "").replace(",", "")
        if not cleaned.isdigit() or int(cleaned) < MIN_TOPUP_AMOUNT:
            await message.answer(t(ui_lang, "invalid_amount", min_amount=_fmt_price(MIN_TOPUP_AMOUNT)))
            return

        amount = int(cleaned)
        minutes = round(amount / RATE_PER_MINUTE, 1)
        db.create_sms_order(user_id, amount, minutes)
        user_state[user_id] = "idle"

        card_owner_line = f"👤 {PAYMENT_CARD_OWNER}\n" if PAYMENT_CARD_OWNER else ""
        await message.answer(
            t(ui_lang, "topup_instructions", card=PAYMENT_CARD_NUMBER, card_owner_line=card_owner_line,
              amount=_fmt_price(amount), minutes=f"{minutes:.0f}"),
            reply_markup=main_menu_kb(ui_lang),
        )
        return

    if user_state.get(user_id) != "ready_for_topic":
        await message.answer(t(ui_lang, "use_buttons_prompt"), reply_markup=main_menu_kb(ui_lang))
        return

    minutes = user_duration.get(user_id, 2)
    video_lang_key = user_video_language.get(user_id, "uz")
    lang_settings = LANGUAGES[video_lang_key]
    style_key = user_visual_style.get(user_id, "cartoon")
    use_ai_images = STYLE_USE_AI_IMAGES.get(style_key, True)

    balance = db.get_or_create_user(user_id, FREE_MINUTES)
    if balance < minutes:
        user_state[user_id] = "idle"
        await message.answer(
            t(ui_lang, "insufficient_balance", minutes=minutes, balance=f"{balance:.1f}", buy_btn=t(ui_lang, "btn_buy")),
            reply_markup=main_menu_kb(ui_lang),
        )
        return

    user_state[user_id] = "idle"
    db.deduct_balance(user_id, minutes)

    async with _waiting_lock:
        position = _waiting_count
        _waiting_count += 1

    if position > 0:
        status_msg = await message.answer(
            t(ui_lang, "queue_msg", position=position),
            reply_markup=main_menu_kb(ui_lang),
        )
    else:
        status_msg = await message.answer(
            t(ui_lang, "preparing_msg", topic=topic, minutes=minutes, lang=lang_settings["label"]),
            reply_markup=main_menu_kb(ui_lang),
        )

    async with job_semaphore:
        async with _waiting_lock:
            _waiting_count -= 1

        if position > 0:
            await status_msg.edit_text(
                t(ui_lang, "preparing_msg", topic=topic, minutes=minutes, lang=lang_settings["label"])
            )

        success = await _generate_and_send(message, status_msg, topic, minutes, lang_settings, ui_lang, use_ai_images)
        if not success:
            db.add_balance(user_id, minutes)


async def _generate_and_send(message: Message, status_msg: Message, topic: str, minutes: int,
                              lang_settings: dict, ui_lang: str, use_ai_images: bool = True) -> bool:
    main_loop = asyncio.get_event_loop()

    def progress(text: str):
        logger.info(text)
        async def _edit():
            try:
                await status_msg.edit_text(text)
            except Exception:
                pass
        asyncio.run_coroutine_threadsafe(_edit(), main_loop)

    try:
        from pipeline import create_video
        video_path = await main_loop.run_in_executor(
            None, create_video, topic, minutes, progress, lang_settings["voice"], lang_settings["script_lang"],
            use_ai_images,
        )

        await status_msg.edit_text(t(ui_lang, "sending_msg"))
        video_file = FSInputFile(video_path)

        last_error = None
        for attempt in range(1, 4):
            try:
                await message.answer_video(video_file, caption=t(ui_lang, "video_ready_caption", topic=topic))
                last_error = None
                break
            except Exception as send_err:
                last_error = send_err
                logger.warning(f"Video yuborish urinish {attempt}/3 muvaffaqiyatsiz: {send_err}")
                await status_msg.edit_text(t(ui_lang, "resend_retry_msg", attempt=attempt))

        if last_error:
            raise last_error

        os.remove(video_path)
        return True

    except Exception as e:
        logger.exception("Video yaratishda xatolik")
        error_text = t(ui_lang, "error_msg", error=str(e))
        try:
            await status_msg.edit_text(error_text)
        except Exception:
            # status_msg tahrirlab bo'lmasa (masalan juda eski yoki o'zgarmagan bo'lsa),
            # yangi xabar sifatida yuboramiz — foydalanuvchi baribir xabardor bo'lishi kerak.
            try:
                await message.answer(error_text)
            except Exception:
                logger.warning("Foydalanuvchiga xatolik haqida xabar yuborib bo'lmadi.")
        return False


async def main():
    logger.info("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

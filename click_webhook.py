"""
Click.uz to'lov tizimining "Shop API" talablariga mos webhook server.
Click, foydalanuvchi to'lov qilganda, shu serverga ikki so'rov yuboradi:
  1. Prepare (action=0) — to'lovni tayyorlashni so'raydi
  2. Complete (action=1) — to'lov muvaffaqiyatli tugaganini bildiradi

DIQQAT: Bu server ishlashi uchun:
  - Ochiq (public) domen nomi kerak (masalan: https://sizning-domen.uz)
  - SSL sertifikat kerak (Let's Encrypt / Certbot orqali bepul olinadi)
  - Bu manzillarni Click merchant kabinetida (Click bilan shartnoma tuzganda) ro'yxatdan o'tkazish kerak:
      Prepare URL:  https://sizning-domen.uz/click/prepare
      Complete URL: https://sizning-domen.uz/click/complete

Ishga tushirish (test uchun, portni ochib):
  uvicorn click_webhook:app --host 0.0.0.0 --port 8000

Productionda nginx orqali (443-portga, SSL bilan) yo'naltirish tavsiya etiladi — README.md'ga qarang.

MUHIM: Bu implementatsiya Click'ning umumiy hujjatlashtirilgan sxemasi (Shop API, MD5 imzo)
asosida yozilgan. Haqiqiy pul bilan ishga tushirishdan oldin, Click'ning rasmiy
hujjatlarini (docs.click.uz) va test (sandbox) muhitida albatta tekshirib chiqing.
"""
import hashlib
import logging

from fastapi import FastAPI, Form
from fastapi.responses import JSONResponse

import db
from config import CLICK_SECRET_KEY, CLICK_SERVICE_ID, TELEGRAM_BOT_TOKEN

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Click xatolik kodlari (hujjatlarga muvofiq)
ERROR_SUCCESS = 0
ERROR_SIGN_FAILED = -1
ERROR_TRANS_NOT_FOUND = -6
ERROR_ALREADY_PAID = -4
ERROR_USER_NOT_FOUND = -5


def _notify_user(user_id: int, text: str):
    """Botga bog'liq bo'lmagan holda, oddiy HTTP so'rov orqali foydalanuvchiga xabar yuboradi."""
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": user_id, "text": text},
            timeout=10,
        )
    except Exception as e:
        logger.warning(f"Foydalanuvchiga xabar yuborib bo'lmadi: {e}")


@app.post("/click/prepare")
async def click_prepare(
    click_trans_id: str = Form(...),
    service_id: str = Form(...),
    merchant_trans_id: str = Form(...),
    amount: str = Form(...),
    action: str = Form(...),
    sign_time: str = Form(...),
    sign_string: str = Form(...),
    error: str = Form("0"),
):
    # Imzoni tekshiramiz
    expected_sign = hashlib.md5(
        f"{click_trans_id}{service_id}{CLICK_SECRET_KEY}{merchant_trans_id}{amount}{action}{sign_time}".encode()
    ).hexdigest()
    if sign_string != expected_sign:
        return JSONResponse({"error": ERROR_SIGN_FAILED, "error_note": "Imzo noto'g'ri"})

    order = db.get_click_order(merchant_trans_id)
    if not order:
        return JSONResponse({"error": ERROR_TRANS_NOT_FOUND, "error_note": "Buyurtma topilmadi"})

    if int(float(amount)) != order["amount"]:
        return JSONResponse({"error": ERROR_TRANS_NOT_FOUND, "error_note": "Summa mos kelmadi"})

    db.mark_click_order_prepared(merchant_trans_id, click_trans_id)

    return JSONResponse({
        "click_trans_id": click_trans_id,
        "merchant_trans_id": merchant_trans_id,
        "merchant_prepare_id": order["id"],
        "error": ERROR_SUCCESS,
        "error_note": "Success",
    })


@app.post("/click/complete")
async def click_complete(
    click_trans_id: str = Form(...),
    service_id: str = Form(...),
    merchant_trans_id: str = Form(...),
    merchant_prepare_id: str = Form(...),
    amount: str = Form(...),
    action: str = Form(...),
    sign_time: str = Form(...),
    sign_string: str = Form(...),
    error: str = Form("0"),
):
    expected_sign = hashlib.md5(
        f"{click_trans_id}{service_id}{CLICK_SECRET_KEY}{merchant_trans_id}{merchant_prepare_id}{amount}{action}{sign_time}".encode()
    ).hexdigest()
    if sign_string != expected_sign:
        return JSONResponse({"error": ERROR_SIGN_FAILED, "error_note": "Imzo noto'g'ri"})

    order = db.get_click_order(merchant_trans_id)
    if not order:
        return JSONResponse({"error": ERROR_TRANS_NOT_FOUND, "error_note": "Buyurtma topilmadi"})

    if order["status"] == "paid":
        return JSONResponse({"error": ERROR_ALREADY_PAID, "error_note": "Allaqachon to'langan"})

    if int(error) < 0:
        # Click tomonidan to'lov bekor qilingan/xato
        return JSONResponse({
            "click_trans_id": click_trans_id,
            "merchant_trans_id": merchant_trans_id,
            "merchant_confirm_id": order["id"],
            "error": ERROR_SUCCESS,
            "error_note": "Success",
        })

    # To'lov muvaffaqiyatli — balansni to'ldiramiz
    db.add_balance(order["user_id"], order["minutes"])
    db.mark_click_order_paid(merchant_trans_id)
    _notify_user(
        order["user_id"],
        f"✅ To'lovingiz muvaffaqiyatli qabul qilindi! Balansingizga {order['minutes']:.0f} daqiqa qo'shildi.",
    )

    return JSONResponse({
        "click_trans_id": click_trans_id,
        "merchant_trans_id": merchant_trans_id,
        "merchant_confirm_id": order["id"],
        "error": ERROR_SUCCESS,
        "error_note": "Success",
    })


@app.get("/health")
async def health():
    return {"status": "ok"}

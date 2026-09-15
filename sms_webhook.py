"""
Telefoningizga o'rnatilgan SMS-forward qiluvchi ilova (masalan "SMS Forwarder", Android)
kelgan bank SMS'larini shu serverga yuboradi. Server SMS matnidan summani o'qib,
mos keladigan kutilayotgan to'lovni topadi va foydalanuvchi balansini avtomatik to'ldiradi.

Ishga tushirish:
  uvicorn sms_webhook:app --host 0.0.0.0 --port 8001

SMS forwarder ilovasida shu manzilni ko'rsating:
  http://SIZNING_SERVER_IP:8001/sms/incoming
  (yoki domen+SSL bo'lsa: https://sizning-domen.uz/sms/incoming)

Ilova POST so'rovida JSON yuborishi kerak:
  {"text": "SMS matni to'liq", "secret": "SMS_WEBHOOK_SECRET qiymati"}

Ko'pchilik SMS forwarder ilovalari so'rov formatini moslashtirish imkonini beradi —
shu formatga moslang (yoki "text" maydoni nomini ilova talab qilgan nomga o'zgartiring).
"""
import re
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

import db
from config import SMS_WEBHOOK_SECRET, SMS_MATCH_WINDOW_MINUTES, TELEGRAM_BOT_TOKEN

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# SMS matnidan summani ajratib olish uchun (masalan "...10 000 сум...", "...10000 so'm...")
AMOUNT_PATTERN = re.compile(r"(\d[\d\s.,]{2,})\s*(so'?m|сум|сумма|UZS)", re.IGNORECASE)


def _extract_amount(text: str) -> int | None:
    match = AMOUNT_PATTERN.search(text)
    if not match:
        return None
    raw = match.group(1)
    digits = re.sub(r"[^\d]", "", raw)
    return int(digits) if digits else None


def _notify_user(user_id: int, text: str):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": user_id, "text": text},
            timeout=10,
        )
    except Exception as e:
        logger.warning(f"Foydalanuvchiga xabar yuborib bo'lmadi: {e}")


@app.post("/sms/incoming")
async def sms_incoming(request: Request):
    data = await request.json()

    if SMS_WEBHOOK_SECRET and data.get("secret") != SMS_WEBHOOK_SECRET:
        return JSONResponse({"ok": False, "error": "invalid secret"}, status_code=403)

    text = data.get("text", "")
    logger.info(f"SMS qabul qilindi: {text[:100]}")

    amount = _extract_amount(text)
    if amount is None:
        logger.info("SMS ichidan summa topilmadi, e'tiborsiz qoldirildi.")
        return JSONResponse({"ok": True, "matched": False, "reason": "amount not found"})

    order = db.find_matching_sms_order(amount, SMS_MATCH_WINDOW_MINUTES)
    if not order:
        logger.info(f"{amount} so'mga mos kutilayotgan to'lov topilmadi.")
        return JSONResponse({"ok": True, "matched": False, "reason": "no pending order"})

    db.add_balance(order["user_id"], order["minutes"])
    db.mark_sms_order_paid(order["id"])
    _notify_user(
        order["user_id"],
        f"✅ To'lovingiz avtomatik aniqlandi! Balansingizga {order['minutes']:.0f} daqiqa qo'shildi.",
    )
    logger.info(f"To'lov muvaffaqiyatli: user={order['user_id']}, amount={amount}")

    return JSONResponse({"ok": True, "matched": True, "order_id": order["id"]})


@app.get("/health")
async def health():
    return {"status": "ok"}

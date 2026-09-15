"""
Premium (custom) emoji ID'larini aniqlash uchun bir martalik yordamchi skript.
Bu skript SIZNING botingiz orqali ishlaydi — hech qanday uchinchi tomon botiga
ma'lumot yuborilmaydi, hammasi shu yerda, sizning kompyuteringizda qoladi.

Ishlatish:
1. python get_emoji_id.py
2. Telegram'da OʻZ botingizga istalgan premium emoji(lar)ni o'z ichiga olgan xabar yuboring
   (agar sizda Premium bo'lsa, o'zingiz yozib yuborishingiz mumkin;
    yoki premium emoji bor xabarni forward qiling)
3. Terminalda shu emoji(lar)ning ID raqami chiqadi
4. Ctrl+C bilan to'xtating
"""
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

from config import TELEGRAM_BOT_TOKEN

bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


@dp.message(F.entities)
async def on_message(message: Message):
    found = False
    for entity in message.entities or []:
        if entity.type == "custom_emoji":
            found = True
            emoji_char = message.text[entity.offset: entity.offset + entity.length]
            print(f"\nEmoji: {emoji_char}")
            print(f"custom_emoji_id: {entity.custom_emoji_id}")
            print(f"HTML uchun: <tg-emoji emoji-id=\"{entity.custom_emoji_id}\">{emoji_char}</tg-emoji>")
    if not found:
        print("Bu xabarda premium emoji topilmadi (oddiy emoji ID'ga ega bo'lmaydi).")


async def main():
    print("Bot ishga tushdi. Botingizga premium emoji bor xabar yuboring...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

from telegram import Bot
from config import TELEGRAM_TOKEN, CHAT_ID


async def send_message(text: str):
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=text)
import asyncio
from telegram import Bot
from config import TOKEN

async def send_test_message():
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=1666355951, text="✅ Si tu vois ça, ton bot fonctionne !")

asyncio.run(send_test_message())

import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise SystemExit("BOT_TOKEN missing")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(m: types.Message):
    await m.answer("✅ Бот жив. Команды: /start /ping")

@dp.message_handler(commands=["ping"])
async def ping(m: types.Message):
    await m.answer("pong")

if name == "main":
    executor.start_polling(dp, skip_updates=True)

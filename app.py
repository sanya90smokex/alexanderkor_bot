
import os, asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise SystemExit("BOT_TOKEN missing. Put it in .env or Render env vars.")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start(m: Message):
    await m.answer("✅ Бот запущен. Команды: /start, /ping")

@dp.message(Command("ping"))
async def ping(m: Message):
    await m.answer("pong")

async def main():
    # Long polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

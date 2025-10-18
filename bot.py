import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не найден. Добавь его в Railway → Variables.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start", "help"])
async def cmd_start(message: types.Message):
    await message.answer("Бот запущен 🚀")

@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)

# запускаем сразу (без if name == "main")
executor.start_polling(dp, skip_updates=True)

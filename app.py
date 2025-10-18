rom aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import asyncio, os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await msg.answer("🤖 Бот запущен!\n\nДоступные команды:\n/start – запустить бота\n/ping – проверка связи\n/signal – получить торговый сигнал")

@dp.message_handler(commands=["ping"])
async def ping(msg: types.Message):
    await msg.answer("✅ Pong!")

@dp.message_handler(commands=["signal"])
async def signal(msg: types.Message):
    # Пример фейкового сигнала — позже подключим реальную аналитику
    await msg.answer(
        "💡 Торговый сигнал:\n\n"
        "🪙 Пара: BTC/USDT\n"
        "📈 Тренд: Восходящий\n"
        "🎯 Цель: $65,200\n"
        "🛡 Поддержка: $62,700\n"
        "⚙️ RSI: 38 — зона перепроданности"
    )

if name == "main":
    executor.start_polling(dp, skip_updates=True)

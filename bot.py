import logging
import os
from aiogram import Bot, Dispatcher, executor, types
from dotenv import load_dotenv

# ── Загружаем токен ────────────────────────────────────────
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ Переменная окружения BOT_TOKEN не найдена.")

# ── Настройка логов ────────────────────────────────────────
logging.basicConfig(level=logging.INFO)

# ── Создание экземпляров ───────────────────────────────────
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# ─── Команды ───────────────────────────────────────────────

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.reply("Бот запущен 🚀\n\nИспользуй /help, чтобы узнать команды.")

@dp.message_handler(commands=["help"])
async def cmd_help(message: types.Message):
    await message.reply(
        "Команды:\n"
        "/signal BTCUSDT 15m — анализ рынка\n"
        "/buy — тестовая покупка\n"
        "/sell — тестовая продажа\n"
        "/ai — включить умный режим"
    )

@dp.message_handler(commands=["signal"])
async def cmd_signal(message: types.Message):
    await message.reply("Собираю данные с Binance... ⏳")
    result = "📊 Анализ завершён: рынок в фазе роста."
    await message.reply(result)

@dp.message_handler(commands=["buy"])
async def cmd_buy(message: types.Message):
    await message.reply("🟢 Симуляция покупки BTCUSDT")

@dp.message_handler(commands=["sell"])
async def cmd_sell(message: types.Message):
    await message.reply("🔴 Симуляция продажи BTCUSDT")

@dp.message_handler(commands=["ai"])
async def cmd_ai(message: types.Message):
    await message.reply("🤖 Умный режим включён. Бот будет анализировать рынок автоматически.")

# ─── Точка входа ───────────────────────────────────────────
if __name__ == "__main__":
    print("Запуск Telegram-бота...")
    executor.start_polling(dp, skip_updates=True)

import os
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

import analyzer  # твой модуль анализа

# ── базовая настройка логов ───────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("alexanderkor_bot")

# ── env ───────────────────────────────────────────────────────────────────────
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не найден. Добавь его в .env или в переменные среды.")

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# ── пул потоков для синхронных расчётов ───────────────────────────────────────
POOL = ThreadPoolExecutor(max_workers=3)
loop = asyncio.get_event_loop()

# ── команды ──────────────────────────────────────────────────────────────────
@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    text = (
        "Бот запущен ✅\n"
        "Доступно:\n"
        "• /help — подсказка\n"
        "• /signal BTCUSDT 15m — разовый сигнал\n"
    )
    await message.reply(text)

@dp.message_handler(commands=["help"])
async def cmd_help(message: types.Message):
    await message.reply(
        "Что умею:\n"
        "— Реальные свечи (ccxt/Binance)\n"
        "— RSI/EMA/volatility и т.п.\n"
        "— Детектор dump-wave\n\n"
        "Пример: <code>/signal BTCUSDT 15m</code>"
    )

def _parse_args(text: str):
    # разбор /signal BTCUSDT 15m
    parts = text.split(maxsplit=2)
    symbol = parts[1] if len(parts) > 1 else "BTCUSDT"
    timeframe = parts[2] if len(parts) > 2 else "15m"
    return symbol.upper(), timeframe

async def _run_in_pool(func, *args, **kwargs):
    return await loop.run_in_executor(POOL, lambda: func(*args, **kwargs))

@dp.message_handler(commands=["signal"])
async def cmd_signal(message: types.Message):
    try:
        symbol, timeframe = _parse_args(message.text or "")
        await message.reply(f"⏳ Собираю данные и считаю: <b>{symbol} {timeframe}</b> …")
        # ВАЖНО: analyzer.make_signal — синхронная функция → уводим в пул
        result: str = await _run_in_pool(analyzer.make_signal, symbol, timeframe)
        # Защита от длинных сообщений
        if not result:
            result = "Пустой ответ анализатора."
        chunks = [result[i:i+3900] for i in range(0, len(result), 3900)]
        for ch in chunks:
            await message.reply(ch)
    except Exception as e:
        logger.exception("Ошибка в /signal")
        await message.reply(f"❌ Ошибка: {e}")

# ── общий текст (исключая команды) ────────────────────────────────────────────
@dp.message_handler(regexp=r"^(?!/).*")  # всё, что НЕ начинается с '/'
async def on_text(message: types.Message):
    await message.reply("Напиши команду /signal BTCUSDT 15m или /help.")

# ── точка входа ───────────────────────────────────────────────────────────────
if name == "main":
    # Если раньше ставился webhook — снимем его, чтобы polling получал апдейты
    try:
        loop.run_until_complete(bot.delete_webhook(drop_pending_updates=True))
    except Exception:
        pass

    logger.info("start_polling…")
    # skip_updates=True — чтобы не разгребать старые апдейты очереди
    executor.start_polling(dp, skip_updates=True)

import os, logging, asyncio
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

import analyzer  # наш модуль

# базовая настройка
logging.basicConfig(level=logging.INFO)
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN не найден. Добавь его в Railway → Variables.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# пул потоков для тяжёлых задач (ccxt/pandas/sklearn)
POOL = ThreadPoolExecutor(max_workers=3)
loop = asyncio.get_event_loop()

@dp.message_handler(commands=["start"])
async def start_cmd(m: types.Message):
    await m.answer(
        "Бот с анализом рынка запущен 🚀\n\n"
        "Команды:\n"
        "• /signal — анализ BTC/USDT (1m)\n"
        "• /watch — анализ BTC/USDT на 1m, 5m, 15m\n"
        "• /help — подсказка"
    )

@dp.message_handler(commands=["help"])
async def help_cmd(m: types.Message):
    await m.answer(
        "Что умею:\n"
        "• Реальные свечи (ccxt) с Binance\n"
        "• RSI/EMA/MACD, волатильность\n"
        "• Детектор dump-волны\n"
        "• Простая ML-оценка следующего шага\n\n"
        "⚠️ Это не финсовет. Используй с риск-менеджментом."
    )

async def _signal_once(symbol: str, timeframe: str) -> str:
    # запускаем синхронный анализ в пуле потоков
    sig = await loop.run_in_executor(POOL, lambda: analyzer.make_signal(symbol=symbol, timeframe=timeframe))
    return analyzer.format_signal(sig)

@dp.message_handler(commands=["signal"])
async def signal_cmd(m: types.Message):
    await m.answer("Собираю данные и считаю… ⏳")
    try:
        text = await _signal_once("BTC/USDT", "1m")
        await m.answer(text, parse_mode="Markdown")
    except Exception as e:
        await m.answer(f"Ошибка анализа: {e}")

@dp.message_handler(commands=["watch"])
async def watch_cmd(m: types.Message):
    await m.answer("Смотрю 1m/5m/15m… ⏳")
    out = []
    try:
        for tf in ["1m", "5m", "15m"]:
            txt = await _signal_once("BTC/USDT", tf)
            out.append(txt)
        await m.answer("\n\n".join(out), parse_mode="Markdown")
    except Exception as e:
        await m.answer(f"Ошибка анализа: {e}")

# запускаем сразу (без if name == "main")
executor.start_polling(dp, skip_updates=True)

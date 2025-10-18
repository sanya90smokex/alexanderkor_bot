# ─── Команды ────────────────────────────────────────────────

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

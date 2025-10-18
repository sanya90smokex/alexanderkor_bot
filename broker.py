import json
import os
from datetime import datetime

BALANCE_FILE = "paper_balance.json"

def load_balance():
    if os.path.exists(BALANCE_FILE):
        with open(BALANCE_FILE, "r") as f:
            return json.load(f)
    else:
        return {"USDT": 10000.0, "positions": []}

def save_balance(data):
    with open(BALANCE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def buy(symbol, price, amount):
    balance = load_balance()
    cost = price * amount
    if balance["USDT"] < cost:
        return f"❌ Недостаточно средств: нужно {cost:.2f}, есть {balance['USDT']:.2f}"
    balance["USDT"] -= cost
    balance["positions"].append({
        "symbol": symbol,
        "side": "BUY",
        "price": price,
        "amount": amount,
        "time": datetime.now().isoformat()
    })
    save_balance(balance)
    return f"✅ Paper LONG: {symbol} @ {price:.2f}, сумма {cost:.2f} USDT"

def sell(symbol, price, amount):
    balance = load_balance()
    pos = next((p for p in balance["positions"] if p["symbol"] == symbol and p["side"] == "BUY"), None)
    if not pos:
        return f"❌ Нет открытой позиции по {symbol}"
    profit = (price - pos["price"]) * amount
    balance["USDT"] += price * amount
    balance["positions"].remove(pos)
    save_balance(balance)
    return f"💰 Paper SELL: {symbol} @ {price:.2f} (прибыль: {profit:.2f} USDT)"

def get_balance():
    balance = load_balance()
    total = balance["USDT"]
    for p in balance["positions"]:
        total += p["price"] * p["amount"]
    return f"💼 Paper баланс: {balance['USDT']:.2f} USDT\n📈 Всего (включая позиции): {total:.2f} USDT"

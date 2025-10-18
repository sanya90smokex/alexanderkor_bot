import time
from typing import List, Dict, Tuple
import ccxt
import numpy as np
import pandas as pd

# ========= вспомогательные функции =========

def _rsi(series: pd.Series, period: int = 14) -> pd.Series:
    d = series.diff()
    up = d.clip(lower=0).rolling(period).mean()
    dn = (-d.clip(upper=0)).rolling(period).mean()
    rs = up / (dn + 1e-12)
    rsi = 100 - 100 / (1 + rs)
    return rsi

def _ema(s: pd.Series, n: int) -> pd.Series:
    return s.ewm(span=n, adjust=False).mean()

def _atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    h, l, c = df["high"], df["low"], df["close"]
    tr = pd.concat([(h - l), (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()

def _ohlcv_to_df(data) -> pd.DataFrame:
    df = pd.DataFrame(data, columns=["ts","open","high","low","close","volume"])
    df["ts"] = pd.to_datetime(df["ts"], unit="ms", utc=True)
    df.set_index("ts", inplace=True)
    df = df.astype(float)
    return df

# ========= функция анализа одной пары =========

def make_signal(symbol: str = "BTCUSDT", timeframe: str = "15m", use_futures=True,
                api_key: str = "", api_secret: str = "") -> str:
    ex = _make_binance(use_futures, api_key, api_secret)
    ex.load_markets()
    sym = _norm_symbol(symbol)
    if sym not in ex.markets:
        raise ValueError(f"Символ {sym} не найден на Binance.")

    df = _ohlcv_to_df(ex.fetch_ohlcv(sym, timeframe=timeframe, limit=300))
    if len(df) < 60:
        raise RuntimeError("Недостаточно данных OHLCV.")

    # индикаторы
    df["ema20"] = _ema(df["close"], 20)
    df["ema50"] = _ema(df["close"], 50)
    df["ema200"] = _ema(df["close"], 200)
    df["rsi14"] = _rsi(df["close"], 14)
    df["atr14"] = _atr(df, 14)

    last, prev = df.iloc[-1], df.iloc[-2]
    trend = "⬆️ бычий" if (last.ema20 > last.ema50 > last.ema200) else ("⬇️ медвежий" if (last.ema20 < last.ema50 < last.ema200) else "↔️ боковик")

    signal = "⚪ Нейтрально"
    reasons = []

    # пересечения EMA
    if prev.ema20 <= prev.ema50 and last.ema20 > last.ema50:
        signal = "🟢 BUY (EMA20↑EMA50)"
        reasons.append("EMA20 пересёк EMA50 вверх")
    elif prev.ema20 >= prev.ema50 and last.ema20 < last.ema50:
        signal = "🔴 SELL (EMA20↓EMA50)"
        reasons.append("EMA20 пересёк EMA50 вниз")

    # RSI
    if last.rsi14 < 30:
        reasons.append("RSI < 30 (перепроданность)")
    elif last.rsi14 > 70:
        reasons.append("RSI > 70 (перекупленность)")

    text = [
        f"📈 <b>{sym}</b>  •  <code>{timeframe}</code>  •  {df.index[-1].strftime('%Y-%m-%d %H:%M UTC')}",
        f"Цена: <b>{last.close:,.2f}</b>",
        f"EMA20/50/200: <code>{last.ema20:.2f}</code> / <code>{last.ema50:.2f}</code> / <code>{last.ema200:.2f}</code>",
        f"RSI14: <b>{last.rsi14:.1f}</b>   ATR14: <code>{last.atr14:.2f}</code>",
        f"Тренд: {trend}",
        "",
        f"Сигнал: <b>{signal}</b>"
    ]
    if reasons:
        text.append("Причины:")
        text += [f"• {r}" for r in reasons]
    text.append("\n<i>Не финсовет. Риск-менеджмент обязателен.</i>")
    return "\n".join(text)

# ========= функция сканирования аномалий =========

def scan_symbols(config: Dict) -> List[str]:
    ex = _make_binance(config.get("use_futures", True),
                       config.get("api_key",""), config.get("api_secret",""))
    ex.load_markets()
    tf = config.get("timeframe", "1m")
    alerts: List[str] = []

    for sym in config.get("symbols", ["BTCUSDT"]):
        s = _norm_symbol(sym)
        if s not in ex.markets:
            continue
        df = _ohlcv_to_df(ex.fetch_ohlcv(s, timeframe=tf, limit=200))
        if len(df) < 60:
            continue

        df["atr14"] = _atr(df, 14)
        df["ret"] = df["close"].pct_change()
        df["rsi14"] = _rsi(df["close"], 14)
        df["vol_mult"] = df["volume"] / (df["volume"].rolling(50).median() + 1e-12)

        last = df.iloc[-1]
        conds = []

        # всплески
        if abs(last["ret"]) >= float(config.get("ret_spike", 0.007)):
            conds.append(f"движение {last['ret']*100:+.2f}%")
        if (last["high"] - last["low"]) >= float(config.get("atr_mult",1.8)) * last["atr14"]:
            conds.append(f"свеча>{config.get('atr_mult',1.8)}×ATR")
        if last["vol_mult"] >= float(config.get("vol_mult",2.0)):
            conds.append(f"объём×{last['vol_mult']:.1f}")
        if last["rsi14"] < 25:
            conds.append("RSI<25")
        if last["rsi14"] > 75:
            conds.append("RSI>75")

        if conds:
            alerts.append(
                f"⚡️ Аномалия: <b>{s}</b>  •  <code>{tf}</code>\n"
                f"Цена: <b>{last['close']:.2f}</b>\n"
                f"Причины: {', '.join(conds)}\n"
                f"Время: {df.index[-1].strftime('%Y-%m-%d %H:%M UTC')}"
            )
    return alerts

# ========= внутренние функции =========

def _make_binance(use_futures: bool, api_key: str, api_secret: str):
    opts = {"enableRateLimit": True}
    if use_futures:
        opts["options"] = {"defaultType": "future"}  # USDT-M Futures
    if api_key and api_secret:
        opts["apiKey"] = api_key
        opts["secret"] = api_secret
    return ccxt.binance(opts)

def _norm_symbol(symbol: str) -> str:
    s = symbol.replace("/", "").upper()
    if s.endswith("USDT"):
        return f"{s[:-4]}/USDT"
    if "/" not in s:
        return f"{s[:-3]}/{s[-3:]}"
    return s

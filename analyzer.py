# ML-оценка следующего шага
    ml_pred = _ml_predict_next_return(close, rsi, macd_hist, vola)

    # базовая логика вердикта
    trend_up = last_ema_fast > last_ema_slow
    trend_down = last_ema_fast < last_ema_slow

    verdict = "⏸ Ждать подтверждения"
    note = "Нейтрально"

    if dump:
        if last_macd_hist > -0.05 and ml_pred >= 0:
            verdict = "🟢 Осторожный отскок (контртренд)"
            note = "Dump-волна замедляется; ML не против роста. Малый риск, частичный вход."
        else:
            verdict = "🔴 Не ловить нож — ждать"
            note = "Сильный скат без признаков замедления или ML против."
    else:
        if trend_up and last_rsi < 70 and ml_pred > 0:
            verdict = "🟢 По тренду (лонг-укрепление)"
            note = "EMA50>EMA200, RSI не перегрет, ML за рост."
        elif trend_down and ml_pred < 0 and last_rsi > 30:
            verdict = "🔴 По тренду вниз (шорт-сигн.)"
            note = "EMA50<EMA200 и ML за снижение."
        else:
            verdict = "⏸ Ждать сигналов"
            note = "Нет согласия индикаторов и ML."

    return Signal(
        symbol=symbol, timeframe=timeframe, price=price,
        change_3m_pct=round(change_3m_pct, 3),
        rsi=round(last_rsi, 2),
        macd_hist=round(last_macd_hist, 4),
        ema_fast=round(last_ema_fast, 2),
        ema_slow=round(last_ema_slow, 2),
        vola_20=round(last_vola, 4),
        dump_wave=dump,
        ml_pred_next_ret=round(ml_pred, 6),
        verdict=verdict,
        note=note
    )


def format_signal(sig: Signal) -> str:
    dump_txt = "Да" if sig.dump_wave else "Нет"
    return (
        f"📊 *{sig.symbol}* {sig.timeframe}\n"
        f"Цена: *{sig.price:.2f}*\n"
        f"Изм. за 3м: *{sig.change_3m_pct:.2f}%*\n"
        f"RSI(14): *{sig.rsi}*\n"
        f"MACD hist: *{sig.macd_hist}*\n"
        f"EMA50/EMA200: *{sig.ema_fast} / {sig.ema_slow}*\n"
        f"Волатильность(20): *{sig.vola_20}*\n"
        f"Dump-волна: *{dump_txt}*\n"
        f"ML прогноз следующего шага: *{sig.ml_pred_next_ret:+.6f}*\n"
        f"\nВердикт: {sig.verdict}\n"
        f"Заметка: _{sig.note}_"
    )

import asyncio
from typing import Dict, Any, List

from analysis import generate_signal
from bot.telegram_bot import send_message
from config import CRYPTO_SYMBOLS
from data.crypto_data import get_ohlcv
from signal_memory import load_last_signals, save_last_signals, is_new_signal


MIN_SCORE = 65
TOP_SIGNAL_LIMIT = 3


def format_signal_message(index: int, sig: Dict[str, Any]) -> str:
    return (
        f"📊 Top Signal #{index}\n\n"
        f"Symbol: {sig['symbol']}\n"
        f"Higher Trend (4H): {sig['higher_trend']}\n"
        f"Side: {sig['side']}\n"
        f"Entry: {sig['entry']}\n"
        f"Stop Loss: {sig['stop_loss']}\n"
        f"TP1: {sig['tp1']}\n"
        f"TP2: {sig['tp2']}\n"
        f"TP3: {sig['tp3']}\n"
        f"Leverage: {sig['leverage']}\n"
        f"EMA20 (1H): {sig['ema20']}\n"
        f"EMA50 (1H): {sig['ema50']}\n"
        f"RSI (1H): {sig['rsi']}\n"
        f"ATR (1H): {sig['atr']}\n"
        f"Bullish Engulfing: {sig['bullish_engulfing']}\n"
        f"Bearish Engulfing: {sig['bearish_engulfing']}\n"
        f"Score: {sig['score']}/100"
    )


def build_memory_item(sig: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "side": sig["side"],
        "entry": sig["entry"],
        "score": sig["score"]
    }


async def collect_signals() -> List[Dict[str, Any]]:
    signals = []

    for symbol in CRYPTO_SYMBOLS:
        try:
            print(f"Checking {symbol}...")

            df_1h = get_ohlcv(symbol, "1h", 100)
            df_4h = get_ohlcv(symbol, "4h", 100)

            signal = generate_signal(df_1h, df_4h)

            if signal is None:
                print(f"No signal for {symbol}")
                continue

            if signal["score"] < MIN_SCORE:
                print(f"Signal for {symbol} ignored. Score: {signal['score']}")
                continue

            signals.append({
                "symbol": symbol,
                **signal
            })

        except Exception as error:
            print(f"Error while checking {symbol}: {error}")

    signals.sort(key=lambda item: item["score"], reverse=True)
    return signals[:TOP_SIGNAL_LIMIT]


async def main():
    print("Starting crypto signal scan...")

    old_signals = load_last_signals()
    new_memory = {}

    top_signals = await collect_signals()

    if not top_signals:
        print("No valid signals found.")
        return

    sent_any = False

    for index, sig in enumerate(top_signals, start=1):
        symbol = sig["symbol"]
        new_memory[symbol] = build_memory_item(sig)

        if not is_new_signal(symbol, sig, old_signals):
            print(f"Skipping duplicate signal for {symbol}")
            continue

        message = format_signal_message(index, sig)
        await send_message(message)

        print(f"Signal sent for {symbol}")
        sent_any = True

    save_last_signals(new_memory)

    if not sent_any:
        print("No new signals to send.")

    print("Scan finished.")


if __name__ == "__main__":
    asyncio.run(main())
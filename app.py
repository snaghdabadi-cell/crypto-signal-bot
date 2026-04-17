import asyncio
from bot.telegram_bot import send_message
from data.crypto_data import get_ohlcv
from analysis import generate_signal
from config import CRYPTO_SYMBOLS


async def main():
    signals = []

    for symbol in CRYPTO_SYMBOLS:
        try:
            df_1h = get_ohlcv(symbol, "1h", 100)
            df_4h = get_ohlcv(symbol, "4h", 100)

            signal = generate_signal(df_1h, df_4h)

            if signal is not None and signal["score"] >= 65:
                signals.append({
                    "symbol": symbol,
                    **signal
                })

        except Exception as e:
            print(f"Error for {symbol}: {e}")

    if not signals:
        await send_message("📊 No valid multi-timeframe signal found right now.")
        return

    signals.sort(key=lambda x: x["score"], reverse=True)
    top_signals = signals[:3]

    for i, sig in enumerate(top_signals, start=1):
        text = (
            f"📊 Top Signal #{i}\n\n"
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

        await send_message(text)


if __name__ == "__main__":
    asyncio.run(main())
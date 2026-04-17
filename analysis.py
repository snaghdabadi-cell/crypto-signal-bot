import ta
import pandas as pd


def calculate_indicators(df):
    df = df.copy()

    df["ema20"] = ta.trend.ema_indicator(df["close"], window=20)
    df["ema50"] = ta.trend.ema_indicator(df["close"], window=50)
    df["rsi"] = ta.momentum.rsi(df["close"], window=14)
    df["atr"] = ta.volatility.average_true_range(
        df["high"], df["low"], df["close"], window=14
    )

    return df


def bullish_engulfing(df):
    if len(df) < 2:
        return False

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    return (
        prev["close"] < prev["open"] and
        curr["close"] > curr["open"] and
        curr["open"] <= prev["close"] and
        curr["close"] >= prev["open"]
    )


def bearish_engulfing(df):
    if len(df) < 2:
        return False

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    return (
        prev["close"] > prev["open"] and
        curr["close"] < curr["open"] and
        curr["open"] >= prev["close"] and
        curr["close"] <= prev["open"]
    )


def get_trend(df):
    if len(df) < 60:
        return None

    df = calculate_indicators(df)
    last = df.iloc[-1]

    if pd.isna(last["ema20"]) or pd.isna(last["ema50"]):
        return None

    ema20 = float(last["ema20"])
    ema50 = float(last["ema50"])
    close_price = float(last["close"])

    ema_distance_ratio = abs(ema20 - ema50) / close_price

    if ema20 > ema50 and ema_distance_ratio > 0.002:
        return "BUY"

    if ema20 < ema50 and ema_distance_ratio > 0.002:
        return "SELL"

    return None


def generate_signal(df_1h, df_4h):
    if len(df_1h) < 60 or len(df_4h) < 60:
        return None

    higher_trend = get_trend(df_4h)
    if higher_trend is None:
        return None

    df_1h = calculate_indicators(df_1h)
    last = df_1h.iloc[-1]

    if (
        pd.isna(last["ema20"]) or
        pd.isna(last["ema50"]) or
        pd.isna(last["rsi"]) or
        pd.isna(last["atr"])
    ):
        return None

    ema20 = float(last["ema20"])
    ema50 = float(last["ema50"])
    rsi = float(last["rsi"])
    atr = float(last["atr"])
    entry = round(float(last["close"]), 2)

    score = 0
    ema_distance_ratio = abs(ema20 - ema50) / entry

    bull_engulf = bullish_engulfing(df_1h)
    bear_engulf = bearish_engulfing(df_1h)

    if ema20 > ema50 and ema_distance_ratio > 0.002 and higher_trend == "BUY":
        side = "BUY"
        score += 50

        stop_loss = round(entry - (atr * 1.5), 2)
        risk = entry - stop_loss

        tp1 = round(entry + risk, 2)
        tp2 = round(entry + (risk * 2), 2)
        tp3 = round(entry + (risk * 3), 2)

        if bull_engulf:
            score += 10
        if bear_engulf:
            score -= 5

    elif ema20 < ema50 and ema_distance_ratio > 0.002 and higher_trend == "SELL":
        side = "SELL"
        score += 50

        stop_loss = round(entry + (atr * 1.5), 2)
        risk = stop_loss - entry

        tp1 = round(entry - risk, 2)
        tp2 = round(entry - (risk * 2), 2)
        tp3 = round(entry - (risk * 3), 2)

        if bear_engulf:
            score += 10
        if bull_engulf:
            score -= 5

    else:
        return None

    if side == "BUY":
        if rsi > 55:
            score += 25
        elif rsi > 50:
            score += 15
        else:
            score += 5
    else:
        if rsi < 45:
            score += 25
        elif rsi < 50:
            score += 15
        else:
            score += 5

    ema_distance_percent = ema_distance_ratio * 100
    if ema_distance_percent > 1:
        score += 10
    elif ema_distance_percent > 0.5:
        score += 5

    if score < 0:
        score = 0

    leverage = "1:3"

    return {
        "side": side,
        "entry": entry,
        "stop_loss": stop_loss,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,
        "leverage": leverage,
        "ema20": round(ema20, 2),
        "ema50": round(ema50, 2),
        "rsi": round(rsi, 2),
        "atr": round(atr, 4),
        "higher_trend": higher_trend,
        "bullish_engulfing": bull_engulf,
        "bearish_engulfing": bear_engulf,
        "score": score
    }
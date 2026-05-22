import pandas as pd
import ta


MIN_DATA_LENGTH = 60
EMA_DISTANCE_THRESHOLD = 0.002
ATR_MULTIPLIER = 1.5


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
        prev["close"] < prev["open"]
        and curr["close"] > curr["open"]
        and curr["open"] <= prev["close"]
        and curr["close"] >= prev["open"]
    )


def bearish_engulfing(df):
    if len(df) < 2:
        return False

    prev = df.iloc[-2]
    curr = df.iloc[-1]

    return (
        prev["close"] > prev["open"]
        and curr["close"] < curr["open"]
        and curr["open"] >= prev["close"]
        and curr["close"] <= prev["open"]
    )


def get_trend(df):
    if len(df) < MIN_DATA_LENGTH:
        return None

    df = calculate_indicators(df)
    last = df.iloc[-1]

    if pd.isna(last["ema20"]) or pd.isna(last["ema50"]) or pd.isna(last["close"]):
        return None

    ema20 = float(last["ema20"])
    ema50 = float(last["ema50"])
    close_price = float(last["close"])

    if close_price <= 0:
        return None

    ema_distance_ratio = abs(ema20 - ema50) / close_price

    if ema20 > ema50 and ema_distance_ratio > EMA_DISTANCE_THRESHOLD:
        return "BUY"

    if ema20 < ema50 and ema_distance_ratio > EMA_DISTANCE_THRESHOLD:
        return "SELL"

    return None


def calculate_targets(entry, atr, side):
    if entry <= 0 or atr <= 0:
        return None

    if side == "BUY":
        stop_loss = round(entry - (atr * ATR_MULTIPLIER), 2)
        risk = entry - stop_loss

        if risk <= 0:
            return None

        tp1 = round(entry + risk, 2)
        tp2 = round(entry + (risk * 2), 2)
        tp3 = round(entry + (risk * 3), 2)

    elif side == "SELL":
        stop_loss = round(entry + (atr * ATR_MULTIPLIER), 2)
        risk = stop_loss - entry

        if risk <= 0:
            return None

        tp1 = round(entry - risk, 2)
        tp2 = round(entry - (risk * 2), 2)
        tp3 = round(entry - (risk * 3), 2)

    else:
        return None

    return stop_loss, tp1, tp2, tp3


def generate_signal(df_1h, df_4h):
    if len(df_1h) < MIN_DATA_LENGTH or len(df_4h) < MIN_DATA_LENGTH:
        return None

    higher_trend = get_trend(df_4h)

    if higher_trend is None:
        return None

    df_1h = calculate_indicators(df_1h)
    last = df_1h.iloc[-1]

    required_columns = ["ema20", "ema50", "rsi", "atr", "close"]

    for column in required_columns:
        if pd.isna(last[column]):
            return None

    ema20 = float(last["ema20"])
    ema50 = float(last["ema50"])
    rsi = float(last["rsi"])
    atr = float(last["atr"])
    entry = round(float(last["close"]), 2)

    if entry <= 0 or atr <= 0:
        return None

    ema_distance_ratio = abs(ema20 - ema50) / entry

    bull_engulf = bullish_engulfing(df_1h)
    bear_engulf = bearish_engulfing(df_1h)

    score = 0
    side = None

    if ema20 > ema50 and ema_distance_ratio > EMA_DISTANCE_THRESHOLD and higher_trend == "BUY":
        side = "BUY"
        score += 50

        if bull_engulf:
            score += 10

        if bear_engulf:
            score -= 5

    elif ema20 < ema50 and ema_distance_ratio > EMA_DISTANCE_THRESHOLD and higher_trend == "SELL":
        side = "SELL"
        score += 50

        if bear_engulf:
            score += 10

        if bull_engulf:
            score -= 5

    else:
        return None

    targets = calculate_targets(entry, atr, side)

    if targets is None:
        return None

    stop_loss, tp1, tp2, tp3 = targets

    if side == "BUY":
        if rsi > 55:
            score += 25
        elif rsi > 50:
            score += 15
        else:
            score += 5

    elif side == "SELL":
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

    score = max(0, min(score, 100))

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
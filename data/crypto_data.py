import ccxt
import pandas as pd

exchange = ccxt.kucoin()


def get_ohlcv(symbol: str, timeframe: str = "1h", limit: int = 100):
    data = exchange.fetch_ohlcv(
        symbol,
        timeframe=timeframe,
        limit=limit
    )

    df = pd.DataFrame(
        data,
        columns=[
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]
    )

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        unit="ms"
    )

    return df
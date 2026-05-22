import ccxt
import pandas as pd


exchange = ccxt.binance({
    "enableRateLimit": True,
    "options": {
        "defaultType": "spot"
    }
})


def get_ohlcv(symbol: str, timeframe: str = "1h", limit: int = 100) -> pd.DataFrame:
    try:
        data = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

        if not data:
            raise ValueError(f"No OHLCV data received for {symbol}")

        df = pd.DataFrame(
            data,
            columns=["timestamp", "open", "high", "low", "close", "volume"]
        )

        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

        numeric_columns = ["open", "high", "low", "close", "volume"]
        df[numeric_columns] = df[numeric_columns].astype(float)

        return df

    except Exception as e:
        raise RuntimeError(f"Failed to fetch OHLCV for {symbol}: {e}")
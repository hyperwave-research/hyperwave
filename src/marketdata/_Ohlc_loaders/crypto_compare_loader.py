import pandas as pd
import pytz
import requests
import json


class CryptoCompareLoader:
    def __init__(self, symbol: str, time_frame="weekly"):
        self._symbol = symbol
        self._time_frame = time_frame

    @staticmethod
    def _aggregate_ticker_weekly(df):
        open = df.open.resample("W-MON").last()
        close = df.close.resample("W-SUN").last().resample("W-MON").last()
        high = df.high.resample("W-MON").max()
        low = df.low.resample("W-MON").min()
        vol = df.volume.resample("W-MON").sum()

        weekly_data = pd.concat([open, close, high, low, vol], axis=1)
        weekly_data["date"] = weekly_data.index
        return weekly_data

    def _fetch_daily_data(self):
        from_symbol, to_symbol = self._symbol.split("-")
        url = "https://min-api.cryptocompare.com/data/histoday?fsym={}&tsym={}&allData=true&aggregate=3&e=CCCAGG".format(
            from_symbol, to_symbol
        )

        r = requests.get(url)
        array = json.dumps(r.json())

        data = json.loads(array)
        daily_tickers = pd.DataFrame(data["Data"])
        daily_tickers["date"] = pd.to_datetime(daily_tickers["time"], unit="s")
        daily_tickers = daily_tickers.rename(columns={"volumeto": "volume"})
        daily_tickers = daily_tickers.set_index("date")
        daily_tickers["date"] = daily_tickers.index
        return daily_tickers

    def get_dataframe(self):
        daily_dataframe = self._fetch_daily_data()
        if self._time_frame == "daily":
            return daily_dataframe.dropna()

        return self._aggregate_ticker_weekly(daily_dataframe).dropna()

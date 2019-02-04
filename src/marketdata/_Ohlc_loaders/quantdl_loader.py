import pandas as pd
import pytz
import quandl

quandl.ApiConfig.api_key = "cEofBzyzyihN3fj62kp4"


class QuandlLoader:
    def __init__(self, symbol: str, time_frame: str = "weekly"):
        self._symbol = symbol
        self._time_frame = time_frame

    @staticmethod
    def _aggregate_ticker_weekly(df):
        open = df.open.resample("W-MON").last()
        close = df.close.resample("W-FRI").last().resample("W-MON").last()
        high = df.high.resample("W-MON").max()
        low = df.low.resample("W-MON").min()
        vol = df.volume.resample("W-MON").sum()

        weekly_data = pd.concat([open, close, high, low, vol], axis=1)
        weekly_data["date"] = weekly_data.index
        return weekly_data

    def _fetch_daily_data(self):
        daily_tickers = quandl.get_table(
            "WIKI/PRICES",
            ticker=[self._symbol],
            qopts={
                "columns": ["ticker", "date", "close", "open", "low", "high", "volume"]
            },
            date={"gte": "1900-01-01"},
            paginate=True,
        )
        daily_tickers = daily_tickers.set_index("date").tz_localize(tz=pytz.utc, level=0)
        daily_tickers["date"] = daily_tickers.index
        return daily_tickers

    def get_dataframe(self):
        daily_dataframe = self._fetch_daily_data()
        if self._time_frame == "daily":
            return daily_dataframe.dropna()

        return self._aggregate_ticker_weekly(daily_dataframe).dropna()

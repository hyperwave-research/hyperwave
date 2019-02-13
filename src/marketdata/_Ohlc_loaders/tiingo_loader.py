import os

import pandas as pd
import requests
from marketdata import TimeFrame


class TiingoLoader:
    def __init__(self, symbol, time_frame: TimeFrame = TimeFrame.Weekly):
        self._symbol = symbol
        self._time_frame = time_frame
        self._api_key = os.environ.get("TIINGO_API_KEY")

        if not self._api_key:
            raise RuntimeError(
                "Tiingo API Key not provided. Please provide"
                " via environment variable TIINGO_API_KEY."
            )

        self._headers = {
            "Authorization": "Token {}".format(self._api_key),
            "Content-Type": "application/json",
            "User-Agent": "hyperwave research",
        }

    def _fetch_data(self):

        params = {"format": "json", "startDate": "1800-1-1"}
        if self._time_frame == TimeFrame.Weekly:
            params["resampleFreq"] = "weekly"
        url = r"https://api.tiingo.com/tiingo/daily/{}/prices".format(self._symbol)

        json = requests.get(url, params=params, headers=self._headers)
        df_list = pd.DataFrame(json.json())
        if df_list.empty:
            raise NameError(
                "The query {} return no data for the symbol. Please check the synbol name in "
                "tiingo.com".format(url, self._symbol)
            )
        df_price = df_list.dropna()
        return df_price

    def get_dataframe(self):
        raw_data = self._fetch_data()
        df = raw_data[["date", "adjOpen", "adjHigh", "adjLow", "adjClose", "adjVolume"]]
        df = df.rename(
            columns={
                "adjOpen": "open",
                "adjHigh": "high",
                "adjLow": "low",
                "adjClose": "close",
                "adjVolume": "volume",
            }
        )

        df.loc[:, "date"] = pd.to_datetime(df.loc[:, "date"]).dt.tz_localize(None)
        df = df.set_index("date")
        df["date"] = df.index
        return df

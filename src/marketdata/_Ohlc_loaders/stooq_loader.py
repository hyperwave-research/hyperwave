import pandas as pd
from marketdata import TimeFrame


class StooqLoader:
    def __init__(self, symbol, time_frame: TimeFrame = TimeFrame.Weekly):
        self._symbol = symbol
        self._time_frame = time_frame

    def _fetch_data(self):
        time_frame = 'w' if self._time_frame == TimeFrame.Weekly else 'd'
        url_symbol = "https://stooq.com/q/d/l/?s={}&i={}".format(self._symbol, time_frame)
        df_list = pd.read_csv(url_symbol, header=0, parse_dates=True)
        if df_list.empty:
            raise NameError("The query {} return no data for the symbol. Please check the synbol name in "
                            "https://stooq.com/".format(url_symbol, self._symbol))
        df_price = df_list.dropna()
        return df_price

    def get_dataframe(self):
        raw_data = self._fetch_data()
        df = raw_data.rename(columns={column: column.lower()
                                      for column in raw_data.columns})
        df.loc[:, 'date'] = pd.to_datetime(df.loc[:, 'date'])
        df = df.set_index('date')
        df['date'] = df.index
        return df

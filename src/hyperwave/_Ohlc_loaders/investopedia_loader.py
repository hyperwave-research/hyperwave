import pandas as pd


class InvestopediaLoader:
    def __init__(self, symbol, time_frame='weekly'):
        self._symbol = symbol
        self._time_frame = time_frame

    @staticmethod
    def _clean_data(df):
        df.loc[:, 'date'] = pd.to_datetime(df.loc[:, 'Date'])
        df = df.rename(columns={'Adj. Close': 'close', 'Low': 'low',
                                'Open': 'open', 'High': 'high', 'Volume': 'volume'})
        df = df.reset_index(drop=True)
        df = df.drop("Date", axis=1)
        df = df.set_index('date')
        df['date'] = df.index
        return df

    def _fetch_data(self):
        url_symbol = "https://www.investopedia.com/markets/api/partial/historical/?Symbol={}&Type=Historical+Prices&Timeframe={}&StartDate=Jan+01%2C+1900".format(
            self._symbol, self._time_frame)
        df_list = pd.read_html(url_symbol, header=0, parse_dates=True)
        df_price = df_list[0].dropna()
        return df_price

    def get_dataframe(self):
        raw_data = self._fetch_data()
        return self._clean_data(raw_data)

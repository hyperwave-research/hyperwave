import numpy as np
import pandas as pd
import datetime as dt

from enum import Enum


from ._Ohlc_loaders.crypto_compare_loader import CryptoCompareLoader
from ._Ohlc_loaders.investopedia_loader import InvestopediaLoader
from ._Ohlc_loaders.local_data_loader import LocalDataLoader
from ._Ohlc_loaders.stooq_loader import StooqLoader

# from _Ohlc_loaders.Quantdl_Loader import Quandl_Loader

np.seterr(divide='ignore', invalid='ignore')


def _get_nb_weeks(row, base_date):
    return int((row["date"] - base_date).days / 7)


def _add_weekid_and_price_is_closing_up(df, base_date):
    df['is_price_closing_up'] = df.close > df.close.shift()
    df['weekId'] = df.apply(lambda row: _get_nb_weeks(row, base_date), axis=1)
    if "volume" in list(df.columns.values):
        df = df.drop("volume", axis=1)
    return df


class Source(Enum):
    CryptoCompare = 1
    Investopedia = 2
    LocalData = 3
    Stooq = 4


class TimeFrame(Enum):
    Daily = 1
    Weekly = 2


# SOURCE_CRYPTOCOMPARE = "cryptocompare"
# SOURCE_INVESTOPEDIA = "investopedia"
# SOURCE_LOCALDATA = "localdata"
# SOURCE_QUANDL = "quandl"


_sources_map = {
    Source.Investopedia: InvestopediaLoader,
    # SOURCE_QUANDL: Quandl_Loader,
    Source.CryptoCompare: CryptoCompareLoader,
    Source.LocalData: LocalDataLoader,
    Source.Stooq: StooqLoader
}


def get_monday_date(df: pd.DataFrame, column_date: str = 'date') -> pd.Series:
    return df.apply(lambda x: x[column_date] - dt.timedelta(days=x[column_date].weekday()), axis=1)


class OhlcLoader:

    @staticmethod
    def get_historical_data(symbol: str, source: Source, base_date: dt.datetime = dt.datetime(1789, 1, 5),
                            time_frame: TimeFrame = TimeFrame.Weekly):
        str_time_frame = 'WEEKLY' if time_frame == TimeFrame.Weekly else 'DAILY'
        source_class = _sources_map[source](symbol, str_time_frame)
        df_raw = source_class.get_dataframe()
        df_with_week_id = _add_weekid_and_price_is_closing_up(df_raw, base_date)
        df_with_week_id = df_with_week_id.reset_index(drop=True)
        if time_frame == TimeFrame.Weekly:
            df_with_week_id['date'] = get_monday_date(df_with_week_id)

        df_with_week_id = df_with_week_id.set_index('weekId')
        df_with_week_id['weekId'] = df_with_week_id.index

        return df_with_week_id

    @staticmethod
    def get_available_sources():
        return _sources_map.keys()

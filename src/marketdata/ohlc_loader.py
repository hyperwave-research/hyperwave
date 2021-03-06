import datetime as dt

import numpy as np
import pandas as pd
import pytz
from marketdata import Source, TimeFrame

from ._Ohlc_loaders.crypto_compare_loader import CryptoCompareLoader
from ._Ohlc_loaders.investopedia_loader import InvestopediaLoader
from ._Ohlc_loaders.local_data_loader import LocalDataLoader
from ._Ohlc_loaders.stooq_loader import StooqLoader
from ._Ohlc_loaders.tiingo_loader import TiingoLoader

np.seterr(divide="ignore", invalid="ignore")


def _get_nb_weeks(row, base_date):
    return int((row["date"] - base_date).days / 7)


def _add_weekid_and_price_is_closing_up(df, base_date):
    df["is_price_closing_up"] = df.close > df.close.shift()
    df["weekId"] = (
        ((df["date"] - base_date).dt.days / 7).round(0).astype(int)
    )  # df.apply(lambda row: _get_nb_weeks(row, base_date), axis=1)
    if not "volume" in list(df.columns.values):
        df["volume"] = 0.0
    return df


_sources_map = {
    Source.Investopedia: InvestopediaLoader,
    Source.CryptoCompare: CryptoCompareLoader,
    Source.LocalData: LocalDataLoader,
    Source.Stooq: StooqLoader,
    Source.Tiingo: TiingoLoader,
}


def get_monday_date(df: pd.DataFrame, column_date: str = "date") -> pd.Series:
    return df.apply(
        lambda x: x[column_date] - dt.timedelta(days=x[column_date].weekday()), axis=1
    )


class Loader:
    @staticmethod
    def get_historical_data(
        symbol: str,
        source: Source,
        base_date: dt.datetime = dt.datetime(1789, 1, 5),
        time_frame: TimeFrame = TimeFrame.Weekly,
    ):
        source_class = _sources_map[source](symbol, time_frame)
        df_raw = source_class.get_dataframe()
        df_with_week_id = _add_weekid_and_price_is_closing_up(df_raw, base_date)
        df_with_week_id = df_with_week_id.reset_index(drop=True)
        if time_frame == TimeFrame.Weekly:
            df_with_week_id["date"] = get_monday_date(df_with_week_id)

        df_with_week_id = df_with_week_id.set_index("weekId")
        df_with_week_id["weekId"] = df_with_week_id.index

        return df_with_week_id

    @staticmethod
    def get_available_sources():
        return _sources_map.keys()

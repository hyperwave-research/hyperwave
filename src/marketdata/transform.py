from typing import List

import pandas as pd
from dataclasses import dataclass


@dataclass
class ResultSet:
    name: str
    df: pd.DataFrame


def get_ohlc_for_column(
    df: pd.DataFrame, col_name: str, date_col_name: str
) -> pd.DataFrame:
    if df.dropna().empty:
        return pd.DataFrame(columns=["date", "open", "high", "low", "close"])

    assert col_name in df.columns
    assert date_col_name in df.columns or date_col_name == df.index.name

    date_as_index = date_col_name == df.index.name
    col_to_extract = [col_name] if date_as_index else [col_name, date_col_name]
    result_df = (
        df[col_to_extract]
        .reset_index()
        .rename(columns={col_name: "open", date_col_name: "date"})
    )
    result_df["high"] = result_df[["open"]]
    result_df["low"] = result_df[["open"]]
    result_df["close"] = result_df[["open"]]
    result_df["volume"] = 0

    return result_df.dropna()


def split_column_to_ohlc(
    df: pd.DataFrame, data_col_name: str = "date"
) -> List[ResultSet]:
    results = [
        ResultSet(column, get_ohlc_for_column(df, column, data_col_name))
        for column in df.columns
        if column != data_col_name
    ]
    return results


def resample_data(df: pd.DataFrame, resample_time_frame: str = "W") -> pd.DataFrame:
    if df.empty:
        return df

    assert "date" == df.index.name
    assert "open" in df.columns
    assert "high" in df.columns
    assert "low" in df.columns
    assert "close" in df.columns

    logic = {"open": "first", "high": "max", "low": "min", "close": "last"}
    if "volume" in df.columns:
        logic["volume"] = "sum"

    offset = pd.offsets.timedelta(days=-6)

    result_df = df.resample(resample_time_frame, loffset=offset, ).apply(logic).dropna()
    return result_df

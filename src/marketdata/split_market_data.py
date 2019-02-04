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

    return result_df


def split_column_to_ohlc(
    df: pd.DataFrame, data_col_name: str = "date"
) -> List[ResultSet]:
    results = [
        ResultSet(column, get_ohlc_for_column(df, column, data_col_name))
        for column in df.columns
        if column != data_col_name
    ]
    return results

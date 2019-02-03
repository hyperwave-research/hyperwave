from typing import List

import pandas as pd
import datetime as dt

import pytest
from marketdata import get_ohlc_for_column, split_column_to_ohlc


def test_raise_error_when_col_name_in_dataframe():
    with pytest.raises(AssertionError):
        data = [{
            "date": dt.date.today(),
            "col1": 1,
            "col2": 2
        }]
        df = pd.DataFrame(data)
        result_df = get_ohlc_for_column(df, "fund1", "date")


def test_split_column_when_date_is_in_index():
    data = [
        {
            "date": dt.date.today(),
            "col1": 1,
            "col2": 2
        },
        {
            "date": dt.date.today() + dt.timedelta(days=1),
            "col1": 2,
            "col2": 4
        }
    ]
    df = pd.DataFrame(data).set_index("date")
    return_df = get_ohlc_for_column(df, "col1", "date")
    expected_number_of_columns = 6
    expected_number_of_rows = 2
    assert return_df.shape[0] == expected_number_of_rows
    assert return_df.shape[1] == expected_number_of_columns


def test_raise_error_when_date_col_name_in_dataframe():
    with pytest.raises(AssertionError):
        data = [{
            "date": dt.date.today(),
            "col1": 1,
            "col2": 2
        }]
        df = pd.DataFrame(data)
        result_df = get_ohlc_for_column(df, "col1", "timestamp")


def test_get_ohlc_for_column_when_dataframe_empty():
    df = pd.DataFrame(data=[], columns=["date", "col1", "col2"])
    result_df = get_ohlc_for_column(df, "col1", "date")

    assert "open" in result_df.columns
    assert "high" in result_df.columns
    assert "low" in result_df.columns
    assert "close" in result_df.columns
    assert "date" in result_df.columns


def test_get_ohlc_for_column_when_dataframe_empty():
    datas = [
        {
            "date": dt.date.today(),
            "col1": 1,
            "col2": 2
        }
    ]

    df = pd.DataFrame(data=datas)
    result_df = get_ohlc_for_column(df, "col1", "date")

    assert "open" in result_df.columns
    assert "high" in result_df.columns
    assert "low" in result_df.columns
    assert "close" in result_df.columns
    assert "date" in result_df.columns


def test_when_empty_dataframe_return_empty_array():
    df = pd.DataFrame()
    split_df = split_column_to_ohlc(df)
    assert [] == split_df


def test_when_dataframe_has_zero_row_but_column_return_array_with_empty_result():
    df = pd.DataFrame(index=["date"], columns=["col1", "col2"])
    split_df = split_column_to_ohlc(df)
    assert 2 == len(split_df)
    assert "col1" == split_df[0].name
    assert split_df[0].df.empty
    assert "col2" == split_df[1].name
    assert split_df[1].df.empty


def test_when_dataframe_has_one_row_and_column_return_one_split_array():
    values = [{
        "date": dt.date.today(),
        "col1": 1}]
    df = pd.DataFrame(values, index=["date"])
    split_df = split_column_to_ohlc(df)
    assert 1 == len(split_df)
    assert "col1" == split_df[0].name
    assert not split_df[0].df.empty
    assert not split_df[0].df.empty

def test_split_dataframe_with_more_than_one_row_and_column():
    data = [
        {
            "date": dt.date.today(),
            "col1": 1,
            "col2": 2
        },
        {
            "date": dt.date.today() + dt.timedelta(days=1),
            "col1": 2,
            "col2": 4
        }
    ]
    df = pd.DataFrame(data).set_index("date")
    split_df = split_column_to_ohlc(df)
    assert len(split_df) == 2
    assert split_df[0].name == "col1"
    assert split_df[1].name == "col2"
    assert split_df[0].df.shape[0] == 2
    assert split_df[0].df.shape[1] == 6


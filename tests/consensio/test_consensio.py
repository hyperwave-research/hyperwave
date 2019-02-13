import inspect
import os

import pandas as pd
import pytest
import pytz
from consensio import (
    get_rolling_mean,
    get_move_value,
    get_value_between_two_col,
    get_consonsio,
)
from marketdata import Loader, Source, TimeFrame


def test_return_mean_serie():
    input_data = [
        {"date": "2018-1-1", "close": 1},
        {"date": "2018-1-2", "close": 1},
        {"date": "2018-1-3", "close": 1},
        {"date": "2018-1-4", "close": 1},
        {"date": "2018-1-5", "close": 1},
        {"date": "2018-1-6", "close": 1},
        {"date": "2018-1-7", "close": 1},
        {"date": "2018-1-8", "close": 1},
        {"date": "2018-1-9", "close": 1},
    ]
    result_data = [
        {"date": "2018-1-1", "close": 1, "roll_mean": None},
        {"date": "2018-1-2", "close": 1, "roll_mean": 1.0},
        {"date": "2018-1-3", "close": 1, "roll_mean": 1.0},
        {"date": "2018-1-4", "close": 1, "roll_mean": 1.0},
        {"date": "2018-1-5", "close": 1, "roll_mean": 1.0},
        {"date": "2018-1-6", "close": 1, "roll_mean": 1.0},
        {"date": "2018-1-7", "close": 1, "roll_mean": 1.0},
        {"date": "2018-1-8", "close": 1, "roll_mean": 1.0},
        {"date": "2018-1-9", "close": 1, "roll_mean": 1.0},
    ]

    df = pd.DataFrame(input_data)
    df["roll_mean"] = get_rolling_mean(df, "close", 2)
    df_result = pd.DataFrame(result_data)

    pd.testing.assert_frame_equal(
        df_result, df, check_less_precise=True, check_like=True
    )


def test_calculate_price_increase_for_column():
    input_data = [
        {"date": "2018-1-1", "close": 1},
        {"date": "2018-1-2", "close": 2},
        {"date": "2018-1-3", "close": 3},
        {"date": "2018-1-4", "close": 4},
        {"date": "2018-1-5", "close": 3},
        {"date": "2018-1-6", "close": 2},
        {"date": "2018-1-7", "close": 1},
        {"date": "2018-1-8", "close": 1},
        {"date": "2018-1-9", "close": 0},
    ]
    result_data = [
        {"date": "2018-1-1", "close": 1, "close_up": None},
        {"date": "2018-1-2", "close": 1, "close_up": 2},
        {"date": "2018-1-3", "close": 1, "close_up": 2},
        {"date": "2018-1-4", "close": 1, "close_up": 2},
        {"date": "2018-1-5", "close": 1, "close_up": 0},
        {"date": "2018-1-6", "close": 1, "close_up": 0},
        {"date": "2018-1-7", "close": 1, "close_up": 0},
        {"date": "2018-1-8", "close": 1, "close_up": 1},
        {"date": "2018-1-9", "close": 1, "close_up": 0},
    ]

    df = pd.DataFrame(input_data)
    df["close_up"] = get_move_value(df, "close", 0, 2, 1)
    df_result = pd.DataFrame(result_data)

    pd.testing.assert_frame_equal(
        df_result[["date", "close_up"]],
        df[["date", "close_up"]],
        check_less_precise=True,
        check_like=True,
    )


def test_return_weight_if_col1_greater_than_col2():
    input_data = [
        {"date": "2018-1-1", "close": 1, "short_MA": None},
        {"date": "2018-1-2", "close": 2, "short_MA": 1.5},
        {"date": "2018-1-3", "close": 3, "short_MA": 2.5},
        {"date": "2018-1-4", "close": 4, "short_MA": 3.5},
        {"date": "2018-1-5", "close": 3, "short_MA": 3.5},
        {"date": "2018-1-6", "close": 2, "short_MA": 2.5},
        {"date": "2018-1-7", "close": 1, "short_MA": 1.5},
        {"date": "2018-1-8", "close": 1, "short_MA": 1},
        {"date": "2018-1-9", "close": 0, "short_MA": 0.5},
    ]
    result_data = [
        {"date": "2018-1-1", "close": 1, "short_MA": None, "close<short_MA": None},
        {"date": "2018-1-2", "close": 2, "short_MA": 1.5, "close<short_MA": 2.0},
        {"date": "2018-1-3", "close": 3, "short_MA": 2.5, "close<short_MA": 2.0},
        {"date": "2018-1-4", "close": 4, "short_MA": 3.5, "close<short_MA": 2.0},
        {"date": "2018-1-5", "close": 3, "short_MA": 3.5, "close<short_MA": 0},
        {"date": "2018-1-6", "close": 2, "short_MA": 2.5, "close<short_MA": 0},
        {"date": "2018-1-7", "close": 1, "short_MA": 1.5, "close<short_MA": 0},
        {"date": "2018-1-8", "close": 1, "short_MA": 1, "close<short_MA": 2.0},
        {"date": "2018-1-9", "close": 0, "short_MA": 0.5, "close<short_MA": 0},
    ]

    df = pd.DataFrame(input_data)
    df["close<short_MA"] = get_value_between_two_col(df, "close", "short_MA", 2.0, 0)
    df_result = pd.DataFrame(result_data)
    pd.testing.assert_frame_equal(
        df_result[["date", "close<short_MA"]],
        df[["date", "close<short_MA"]],
        check_less_precise=True,
        check_like=True,
    )


@pytest.mark.usefixtures("set_env_variable_consensio")
def get_sample_data():
    base_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    sample_data_folder = os.path.join(base_dir, "sample_data")
    print("get_sample_data {}".format(sample_data_folder))
    for file in os.listdir(sample_data_folder):
        file_name = os.path.basename(file)
        file_name_raw_data, file_extension = os.path.splitext(file_name)
        file_name_json_result = "{}.consensio.csv".format(file_name_raw_data)

        file_full_path = os.path.join(sample_data_folder, file)
        result_full_path = os.path.join(sample_data_folder, file_name_json_result)
        if file_extension != ".csv":
            continue

        if ".consensio" in file_name:
            continue
        yield (file_full_path, result_full_path, "test file {}".format(file_name))


@pytest.mark.parametrize("source_path, result_file_path, comment", get_sample_data())
def test_consensio(source_path: str, result_file_path: str, comment: str):
    root_test, result_file_name = os.path.split(result_file_path)
    df_source = Loader.get_historical_data(
        source_path, Source.LocalData, time_frame=TimeFrame.Weekly
    )
    df_consensio = get_consonsio(df_source, "close", low_ma=3, mid_ma=7, high_ma=30)

    if not os.path.exists(os.path.join(root_test, "results")):
        os.mkdir(os.path.join(root_test, "results"))

    result_output_path = os.path.join(root_test, "results", result_file_name)
    df_consensio.sort_values("date", ascending=True).to_csv(
        result_output_path, header=True, index=False
    )

    if not os.path.exists(result_file_path):
        print("Result file doesnt exist")
        return

    df_result = pd.read_csv(
        result_file_path, header=0, parse_dates=["date"], infer_datetime_format=True
    ).set_index("date")
    df_result["date"] = df_result.index

    df_result = (
        df_result.reset_index(drop=True)
        .sort_values("date", ascending=True)
        .reset_index()
    )
    df_consensio = (
        df_consensio.reset_index(drop=True)
        .sort_values("date", ascending=True)
        .reset_index()
    )
    pd.testing.assert_frame_equal(
        df_result.sort_values("date", ascending=True)[["date", "consensio"]],
        df_consensio.sort_values("date", ascending=True)[["date", "consensio"]],
        check_less_precise=True,
        check_like=True,
    )

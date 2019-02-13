import inspect
import logging
import os

import pandas as pd
import pytest
import pytz
from marketdata import Source, TimeFrame, Loader
from hyperwave import Hyperwave

logging.basicConfig(level=logging.ERROR)


@pytest.mark.usefixtures("set_env_variable_hyperwave")
def get_test_sample_data():
    base_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    sample_data_folder = os.path.join(base_dir, "sample_data")

    for file_name in os.listdir(sample_data_folder):
        # base_dir, file_name = os.path.split(file)
        file_name_raw_data, file_extension = os.path.splitext(file_name)

        file_name_json_result = "{}.hw.csv".format(file_name_raw_data)
        if file_extension != ".csv":
            continue
        if ".hw" in file_name or ".hull" in file_name:
            continue
        yield (
            os.path.join(sample_data_folder, file_name),
            os.path.join(sample_data_folder, file_name_json_result),
            "test file {}".format(file_name),
        )


# @pytest.mark.usefixtures("set_env_variable_hyperwave")
@pytest.mark.parametrize(
    "source_name, result_file_path, comment", get_test_sample_data()
)
def test_hyperwaves(source_name: str, result_file_path: str, comment: str):
    df_source = Loader.get_historical_data(
        source_name, Source.LocalData, time_frame=TimeFrame.Weekly
    )

    hw = Hyperwave.get_standard_hyperwave()
    (df_hull_hyperwave, hw_phases_temp, hyperwave) = hw.get_hyperwave(df_source)
    sample_data_folder, result_file_name = os.path.split(result_file_path)
    # result_file_path = os.path.join(sample_data_folder, result_file_name)

    df_result = pd.read_csv(
        result_file_path,
        header=0,
        parse_dates=["x1_date", "x2_date"],
        infer_datetime_format=True,
    )

    if not df_result.empty:
        df_result["x1_date"] = pd.to_datetime(df_result["x1_date"])
        df_result["x2_date"] = pd.to_datetime(df_result["x2_date"])

    if not os.path.exists(os.path.join(sample_data_folder, "results")):
        os.mkdir(os.path.join(sample_data_folder, "results"))
    result_output_path = os.path.join(sample_data_folder, "results", result_file_name)

    hyperwave.sort_values("phase_id", ascending=True).to_csv(
        result_output_path, header=True, index=False
    )
    df_result = df_result.sort_values("phase_id", ascending=True).reset_index()
    hyperwave = hyperwave.sort_values("phase_id", ascending=True).reset_index()
    pd.testing.assert_frame_equal(
        df_result, hyperwave, check_less_precise=True, check_like=True
    )


# # @pytest.mark.usefixtures("set_env_variable")
# def test_single_hyperwave():
#     source_name = "~/git/hyperwave/tests/hyperwave/sample_data/Stooq_BHF.US_20181122.csv"
#     result_file_path = "~/git/hyperwave/tests/hyperwave/sample_data/Stooq_BHF.US_20181122.hw.csv"
#     df_source = Loader.get_historical_data(
#         source_name, Source.LocalData, time_frame=TimeFrame.Weekly)
#
#     hw = Hyperwave.get_standard_hyperwave()
#     (df_hull_hyperwave, hw_phases_temp, hyperwave) = hw.get_hyperwave(df_source)
#     with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 150):
#         print(df_hull_hyperwave)
#         print(hw_phases_temp)
#         print(hyperwave)
#
#     df_result = pd.read_csv(
#         result_file_path,
#         header=0,
#         parse_dates=["x1_date", "x2_date"],
#         infer_datetime_format=True,
#     )
#
#     # df_result['x1_date'] = pd.to_datetime(df_result ['x1_date']).dt.tz_localize(pytz.UTC)
#     # df_result['x2_date'] = pd.to_datetime(df_result['x2_date']).dt.tz_localize(pytz.UTC)
#
#     df_result = df_result.sort_values("phase_id", ascending=True).reset_index()
#     hyperwave = hyperwave.sort_values("phase_id", ascending=True).reset_index()
#     pd.testing.assert_frame_equal(
#         df_result, hyperwave, check_less_precise=True, check_like=True
#     )
#
# def test_resave_result_to_csv():
#     root_path = r'/home/dzucker/git/hyperwave/tests/sample_data'
#     for json_file_path in get_files(root_path):
#         print("Load file {} :".format(json_file_path))
#         file_name, extension = os.path.splitext(json_file_path)
#         if not extension == '.json':
#             continue
#
#         df = pd.read_json(json_file_path , orient='table')
#
#         csv_file_path= '{}.csv'.format(file_name)
#         df.to_csv(csv_file_path, header=True, index=False)
#
# def get_files(root_path):
#     for path in os.listdir(root_path):
#         full_path = os.path.join(root_path, path)
#         if os.path.isdir(full_path):
#             yield from get_files(full_path)
#         yield full_path


# # @pytest.mark.usefixtures("set_env_variable")
# def test_Nasdac_Until_2005_hyperwave():
#     df_source = OhlcLoader.get_historical_data(
#         "Nasdac_Before_2005", Source.LocalData, base_date, TimeFrame.Weekly)
#
#     hw = Hyperwave.get_standard_hyperwave()
#     (df_hull_hyperwave, hw_phases_temp, hyperwave) = hw.get_hyperwave(df_source)
#     with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#         print(df_hull_hyperwave)
#         print(hw_phases_temp)
#         print(hyperwave)
#     assert len(hyperwave) == 4
#     # assert df.shape[0] == 0
#
#
# # @pytest.mark.usefixtures("set_env_variable")
# def test_Bitcoin_hyperwave():
#     df_source = OhlcLoader.get_historical_data(
#         "btcusd_w", Source.LocalData, base_date, TimeFrame.Weekly)
#
#     hw = Hyperwave.get_standard_hyperwave()
#     (df_hull_hyperwave, hw_phases_temp, hyperwave) = hw.get_hyperwave(df_source)
#     with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#         print(df_hull_hyperwave)
#         print(hw_phases_temp)
#         print(hyperwave)
#     assert len(hyperwave) == 4
#     # assert df.shape[0] == 0

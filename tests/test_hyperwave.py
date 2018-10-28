import logging
import os

import pandas as pd
import pytest
from hyperwave import OhlcLoader, Source, Hyperwave, TimeFrame

logging.basicConfig(level=logging.ERROR)


def get_test_sample_data():
    sample_data_folder = os.environ.get("HW_DATA_ROOT_FOLDER", "./sample_data")
    for file in os.listdir(sample_data_folder):
        file_name = os.path.basename(file)
        file_name_raw_data, file_extension = os.path.splitext(file_name)
        file_name_json_result = "{}.hw.json".format(file_name_raw_data)
        if file_extension != '.csv':
            continue
        yield (file_name_raw_data, file_name_json_result ,"test file {}".format(file_name))

@pytest.mark.parametrize("source_name, result_file_name, comment", get_test_sample_data())
def test_hyperwaves(source_name: str, result_file_name: str,  comment: str):
    df_source = OhlcLoader.get_historical_data(source_name, Source.LocalData, time_frame=TimeFrame.Weekly)

    hw = Hyperwave.get_standard_hyperwave()
    (df_hull_hyperwave, hw_phases_temp,hyperwave) = hw.get_hyperwave(df_source)
    sample_data_folder = os.environ.get("HW_DATA_ROOT_FOLDER", "./sample_data")
    result_file_path = os.path.join(sample_data_folder, result_file_name)

    df_result = pd.read_json(result_file_path, orient='table')

    if not os.path.exists(os.path.join(sample_data_folder, "results")) :
        os.mkdir(os.path.join(sample_data_folder, "results"))
    result_output_path = os.path.join(sample_data_folder, "results", result_file_name)

    hyperwave.to_json(result_output_path, orient='table')
    pd.testing.assert_frame_equal(df_result, hyperwave, check_less_precise=True )


# @pytest.mark.usefixtures("set_env_variable")
def test_single_hyperwave():
    source_name = "Stooq_AAPL.US_20181026"
    df_source = OhlcLoader.get_historical_data(
        source_name, Source.LocalData, time_frame=TimeFrame.Weekly)

    hw = Hyperwave.get_standard_hyperwave()
    (df_hull_hyperwave, hw_phases_temp, hyperwave) = hw.get_hyperwave(df_source)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 150):
        print(df_hull_hyperwave)
        print(hw_phases_temp)
        print(hyperwave)
    assert 4 == hyperwave.shape[0]


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

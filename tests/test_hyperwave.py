import inspect
import pandas as pd
import os
import logging
from datetime import datetime
# from os import os

import pytest
from hyperwave import OhlcLoader, Source, Hyperwave, TimeFrame

# from hyperwave import Hyperwave

logging.basicConfig(level=logging.DEBUG)
base_date = datetime(1800, 1, 6)




# @pytest.fixture
def get_test_sample_data():
    sample_data_folder = os.environ.get("HW_DATA_ROOT_FOLDER", "./sample_data")
    tests = []
    for file in os.listdir(sample_data_folder):
        file_name = os.path.basename(file)
        file_name, file_extension = os.path.splitext(file_name)
        if file_extension != '.csv':
            continue
        yield (file_name, "test file {}".format(file_name))

    # return pytest.mark.parametrize("source_name, comment", tests)


# @pytest.mark.usefixtures("set_env_variable")
@pytest.mark.parametrize("source_name, comment", get_test_sample_data())
def test_hyperwaves(source_name: str, comment: str):
    df_source = OhlcLoader.get_historical_data(
        source_name, Source.LocalData, base_date, TimeFrame.Weekly)

    hw = Hyperwave.get_standard_hyperwave()
    (df_hull_hyperwave, hw_phases_temp,hyperwave) = hw.get_hyperwave(df_source)
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(df_hull_hyperwave)
    #     print(hw_phases_temp)
    #     print(hyperwave)
    assert 4 == hyperwave.shape[0], comment
    # assert df.shape[0] == 0


# @pytest.mark.usefixtures("set_env_variable")
def test_single_hyperwave():
    source_name = "DowJones_1920_1933"
    df_source = OhlcLoader.get_historical_data(
        source_name, Source.LocalData, base_date, TimeFrame.Weekly)

    hw = Hyperwave.get_standard_hyperwave()
    (df_hull_hyperwave, hw_phases_temp, hyperwave) = hw.get_hyperwave(df_source)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 150):
        print(df_hull_hyperwave)
        print(hw_phases_temp)
        print(hyperwave)
    assert 4 == hyperwave.shape[0]


# @pytest.mark.usefixtures("set_env_variable")
# def test_10y_usd_treasury_note_hyperwave():
#     df_source = OhlcLoader.get_historical_data(
#         "10y_usd_treasury_note", Source.LocalData, base_date, TimeFrame.Weekly)
#
#     hw = Hyperwave.get_standard_hyperwave()
#     (df_hull_hyperwave, hw_phases_temp, hyperwave) = hw.get_hyperwave(df_source)
#     with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#         print(df_hull_hyperwave)
#         print(hw_phases_temp)
#         print(hyperwave)
#     assert len(hyperwave) == 4
#     # assert df.shape[0] == 0

# @pytest.mark.usefixtures("set_env_variable")
def test_Nasdac_Until_2005_hyperwave():
    df_source = OhlcLoader.get_historical_data(
        "Nasdac_Before_2005", Source.LocalData, base_date, TimeFrame.Weekly)

    hw = Hyperwave.get_standard_hyperwave()
    (df_hull_hyperwave, hw_phases_temp, hyperwave) = hw.get_hyperwave(df_source)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df_hull_hyperwave)
        print(hw_phases_temp)
        print(hyperwave)
    assert len(hyperwave) == 4
    # assert df.shape[0] == 0


# @pytest.mark.usefixtures("set_env_variable")
def test_Bitcoin_hyperwave():
    df_source = OhlcLoader.get_historical_data(
        "btcusd_w", Source.LocalData, base_date, TimeFrame.Weekly)

    hw = Hyperwave.get_standard_hyperwave()
    (df_hull_hyperwave, hw_phases_temp, hyperwave) = hw.get_hyperwave(df_source)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df_hull_hyperwave)
        print(hw_phases_temp)
        print(hyperwave)
    assert len(hyperwave) == 4
    # assert df.shape[0] == 0

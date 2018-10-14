import inspect
import pandas as pd
import os
from datetime import datetime
# from os import os

import pytest
from hyperwave import OhlcLoader, Source, Hyperwave

# from hyperwave import Hyperwave

base_date = datetime(1800, 1, 6)

@pytest.fixture
def set_env_variable():
    base_dir = os.path.dirname(os.path.abspath(
        inspect.getfile(inspect.currentframe())))
    sample_data_path = os.path.join(base_dir, "sample_data")

    os.environ["HW_DATA_ROOT_FOLDER"] = sample_data_path
    return


# @pytest.mark.usefixtures("set_env_variable")
# def test_10y_usd_treasury_is_hyperwave():
#     df_source = OhlcLoader.get_historical_data(
#         "10y_usd_treasury_note", Source.LocalData, base_date, 'weekly')
#
#     hw = Hyperwave()
#     (df_hull_hyperwave, hw_phases_temp, hyperwave) = hw.get_hyperwave(df_source)
#     with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#         print(df_hull_hyperwave)
#         print(hw_phases_temp)
#         print(hyperwave)
#     assert len(hyperwave) == 4
#     # assert df.shape[0] == 0

@pytest.mark.usefixtures("set_env_variable")
def test_Nasdax_hyperwave():
    df_source = OhlcLoader.get_historical_data(
        "Nasdac", Source.LocalData, base_date, 'weekly')

    hw = Hyperwave(phase_grow_factor=2.4)
    (df_hull_hyperwave, hw_phases_temp, hyperwave) = hw.get_hyperwave(df_source)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df_hull_hyperwave)
        print(hw_phases_temp)
        print(hyperwave)
    assert len(hyperwave) == 4
    # assert df.shape[0] == 0

@pytest.mark.usefixtures("set_env_variable")
def test_Nasdax_hyperwave():
    df_source = OhlcLoader.get_historical_data(
        "Nasdac_Before_2005", Source.LocalData, base_date, 'weekly')

    hw = Hyperwave(phase_grow_factor=2.4)
    (df_hull_hyperwave, hw_phases_temp, hyperwave) = hw.get_hyperwave(df_source)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df_hull_hyperwave)
        print(hw_phases_temp)
        print(hyperwave)
    assert len(hyperwave) == 4
    # assert df.shape[0] == 0

@pytest.mark.usefixtures("set_env_variable")
def test_Nasdax_hyperwave():
    df_source = OhlcLoader.get_historical_data(
        "Nasdac_Before_2005", Source.LocalData, base_date, 'weekly')

    hw = Hyperwave(phase_grow_factor=2.4)
    (df_hull_hyperwave, hw_phases_temp, hyperwave) = hw.get_hyperwave(df_source)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df_hull_hyperwave)
        print(hw_phases_temp)
        print(hyperwave)
    assert len(hyperwave) == 4
    # assert df.shape[0] == 0
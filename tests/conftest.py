import inspect
import os

import pytest


# @pytest.fixture(scope="module")
# def set_env_variable():
base_dir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
sample_data_path = os.path.join(base_dir, "consensio")

os.environ["HW_DATA_ROOT_FOLDER"] = sample_data_path
    # return

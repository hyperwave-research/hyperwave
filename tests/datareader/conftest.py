import inspect
import os

import pytest


@pytest.fixture()
def set_env_variable():
    base_dir = os.path.dirname(os.path.abspath(
    inspect.getfile(inspect.currentframe())))
    os.environ["HW_DATA_ROOT_FOLDER"] = base_dir
    return

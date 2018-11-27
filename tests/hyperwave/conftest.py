import inspect
import os

import pytest


@pytest.mark.run(order=1)
@pytest.fixture()
def set_env_variable_consensio(monkeypatch):
    base_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    sample_data_path = os.path.join(base_dir, "sample_data")
    print("===================== SET CONFTEST FROM HYPERWAVE ===========================")
    monkeypatch.setenv("HW_DATA_ROOT_FOLDER", sample_data_path)
    # reload(conf)
    return
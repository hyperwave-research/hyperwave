import inspect
import sys
import os

from consensio import Main


def test_run_consensio(monkeypatch, tmpdir):
    base_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    data_dir = os.path.join(base_dir, "folder_test")

    result_path = os.path.join(tmpdir, "HSBC_Consensio.csv")
    arg_sample = [
        "main.py",
        "calculate",
        "--inputPath",
        data_dir,
        "--outputPath",
        result_path,
    ]

    monkeypatch.setattr(sys, "argv", arg_sample)
    Main()

    assert os.path.exists(result_path)

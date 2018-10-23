import sys
import tempfile
import os

from hyperwave import Main


def test_hw_Download_file(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdirname:
        output_path = os.path.join(tmpdirname, "AAPL.csv")
        arg_sample = ['main.py', 'download', '--source', 'LocalData', '--symbol', 'aapl_us_w', '--output',
                      output_path, '--timeframe', 'Weekly']

        monkeypatch.setattr(sys, 'argv', arg_sample)
        Main()

        assert os.path.exists(output_path)

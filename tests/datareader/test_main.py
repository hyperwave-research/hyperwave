import os
import sys

from datareader import Main


def test_datareader_Download_file(monkeypatch, tmpdir):
    ticker = 'AAPL.US'
    output_path = os.path.join(tmpdir.dirname, "{}.csv".format(ticker))
    arg_sample = ['main.py', 'download', '--source', "Stooq", '--symbol', ticker, '--outputPath',
                  tmpdir.dirname, '--timeframe', "Weekly", '--nbThread', "1"]

    monkeypatch.setattr(sys, 'argv', arg_sample)
    Main()

    assert os.path.exists(output_path)

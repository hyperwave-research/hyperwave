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


def test_datareader_Download_file_multithread(monkeypatch, tmpdir):
    tickers = 'AAPL.US,MS.US,MSFT.US,GOOGL.US'
    arg_sample = ['main.py', 'download', '--source', "Stooq", '--symbol', tickers, '--outputPath',
                  tmpdir.dirname, '--timeframe', "Weekly", '--nbThread', "2"]

    monkeypatch.setattr(sys, 'argv', arg_sample)
    Main()

    for ticker in tickers.split(','):
        ticker_path = os.path.join(tmpdir.dirname, "{}.csv".format(ticker))
        assert os.path.exists(ticker_path)

import datetime as dt
import os
import sys

from marketdata import Main


def test_marketdata_Download_file(monkeypatch, tmpdir):
    ticker = "AAPL.US"
    output_path = os.path.join(tmpdir.dirname, "{}.csv".format(ticker))
    arg_sample = [
        "main.py",
        "download",
        "--source",
        "Stooq",
        "--symbols",
        ticker,
        "--outputPath",
        tmpdir.dirname,
        "--timeframe",
        "Weekly",
        "--nbThread",
        "1",
    ]

    monkeypatch.setattr(sys, "argv", arg_sample)
    Main()

    assert os.path.exists(output_path)


def test_marketdata_Download_file_multithread(monkeypatch, tmpdir):
    tickers = "AAPL.US,MS.US,MSFT.US,GOOGL.US"
    arg_sample = [
        "main.py",
        "download",
        "--source",
        "Stooq",
        "--symbols",
        tickers,
        "--outputPath",
        tmpdir.dirname,
        "--timeframe",
        "Weekly",
        "--nbThread",
        "2",
    ]

    monkeypatch.setattr(sys, "argv", arg_sample)
    Main()

    for ticker in tickers.split(","):
        ticker_path = os.path.join(tmpdir.dirname, "{}.csv".format(ticker))
        assert os.path.exists(ticker_path)


def test_marketdata_Download_file(monkeypatch, tmpdir):
    ticker = "^FTM"
    output_path = os.path.join(tmpdir.dirname, "{}.csv".format(ticker))
    arg_sample = [
        "main.py",
        "download",
        "--source",
        "Stooq",
        "--symbols",
        ticker,
        "--outputPath",
        tmpdir.dirname,
        "--timeframe",
        "Weekly",
        "--nbThread",
        "1",
    ]

    monkeypatch.setattr(sys, "argv", arg_sample)
    Main()

    assert os.path.exists(output_path)


def test_marketdata_split_assets(monkeypatch, tmpdir):
    # prepare the sample input file
    input_path = os.path.join(tmpdir.dirname, "sample.csv")
    with open(input_path, mode="w") as f:
        f.write("date,col1,col2,col3\n")
        for i in range(0, 4):
            f.write(
                "{},{},{},{}\n".format(dt.date.today() + dt.timedelta(days=i), 1, 2, 3)
            )
        f.flush()

    arg_sample = [
        "main.py",
        "split-assets",
        "--inputPath",
        input_path,
        "--outputPath",
        tmpdir.dirname,
    ]

    monkeypatch.setattr(sys, "argv", arg_sample)
    Main()

    expected_output_paths = [
        os.path.join(tmpdir.dirname, "{}.csv".format(col_name))
        for col_name in ["col1", "col2", "col3"]
    ]

    for output_path in expected_output_paths:
        assert os.path.exists(output_path)

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


def test_resample_market_data_from_daily_to_weekly(monkeypatch, tmpdir):
    # prepare the sample input file
    input_path = os.path.join(tmpdir.dirname, "input")
    os.mkdir(input_path)

    output_path = os.path.join(tmpdir.dirname, "output")
    os.mkdir(output_path)

    file_names = []
    for file_id in range(1, 4):
        file_name = "market_{}.csv".format(file_id)
        file_names.append(file_name)
        file_path = os.path.join(input_path, file_name)
        with open(file_path, mode="w") as f:
            f.write("date,open,high,low,close\n")
            for row_id in range(0, 4):
                f.write(
                    "{},{},{},{},{}\n".format(
                        dt.date.today() + dt.timedelta(days=row_id),
                        1 * row_id,
                        2 * row_id,
                        0.5 * row_id,
                        2 * row_id,
                    )
                )
            f.flush()

    arg_sample = [
        "main.py",
        "resample",
        "--inputPath",
        input_path,
        "--outputPath",
        output_path,
    ]

    monkeypatch.setattr(sys, "argv", arg_sample)
    Main()

    expected_output_paths = [
        os.path.join(output_path, file_name) for file_name in file_names
    ]

    for output_path in expected_output_paths:
        assert os.path.exists(output_path)

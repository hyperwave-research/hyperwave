import inspect
import os
from datetime import datetime

import pandas as pd
import pytest
import pytz
from marketdata import Loader, Source, TimeFrame

base_date = datetime(1900, 1, 1)

INVESTOPIA_SAMPLE_DATA = """
    <html>
        <head>
            <meta http-equiv="content-type" content="text/html; charset=UTF-8">
        </head>
        <body>
            <div class="page">
                <table class="data">
                    <tbody data-rows="7309" data-start-date="Jan 01, 1900">
                    <tr class="header-row">
                        <th class="date">Date</th>
                        <th class="num">Open</th>
                        <th class="num">High</th>
                        <th class="num">Low</th>
                        <th class="num">Adj. Close</th>
                        <th class="num">Volume</th>
                    </tr>
                    <tr class="in-the-money">
                        <td class="date">Oct 01, 2018</td>
                        <td class="num">227.95</td>
                        <td class="num">229.42</td>
                        <td class="num">226.35</td>
                        <td class="num">227.26</td>
                        <td class="num">23,600,802</td>
                    </tr>
                        <tr class="in-the-money">
                        <td class="date">Sep 28, 2018</td>
                        <td class="num">224.79</td>
                        <td class="num">225.84</td>
                        <td class="num">224.02</td>
                        <td class="num">225.74</td>
                        <td class="num">22,929,364</td>
                    </tr>
                    <tr class="in-the-money">
                        <td class="date">Sep 27, 2018</td>
                        <td class="num">223.82</td>
                        <td class="num">226.44</td>
                        <td class="num">223.54</td>
                        <td class="num">224.95</td>
                        <td class="num">30,181,227</td>
                    </tr>
                    <tr class="in-the-money">
                        <td class="date">Sep 26, 2018</td>
                        <td class="num">221.00</td>
                        <td class="num">223.75</td>
                        <td class="num">219.76</td>
                        <td class="num">220.42</td>
                        <td class="num">23,984,706</td>
                    </tr>
                    </tbody>
                </table>
             </div>
        </body>
    </html>"""

data_source_required_columns = [
    "close",
    "date",
    "high",
    "is_price_closing_up",
    "low",
    "open",
    "volume",
    "weekId",
]


def test_that_source_available_is_equal_to_5():
    sources = Loader.get_available_sources()
    assert len(sources) == 5


def test_that_cryptocompare_source_return_right_schema_dataframeHyperwave_Path_Finder():
    df = Loader.get_historical_data(
        "BTC-USD", Source.CryptoCompare, base_date, TimeFrame.Weekly
    )
    assert (df.columns.sort_values() == data_source_required_columns).all()


def test_that_investopedia_source_return_right_schema_dataframe(monkeypatch):
    def mock_pandas_read_html(url_symbol, header, parse_dates):
        data = [
            {
                "Date": "Oct 01, 2018",
                "Open": 227.95,
                "High": 229.42,
                "Low": 226.35,
                "Adj. Close": 227.26,
                "Volume": 23600802,
            }
        ]
        return [pd.DataFrame(data)]

    monkeypatch.setattr(pd, "read_html", mock_pandas_read_html)
    df = Loader.get_historical_data("AAPL", Source.Investopedia, base_date)

    assert (df.columns.sort_values() == data_source_required_columns).all()


def test_that_local_data_source_return_right_schema_dataframe():
    base_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    test_file_path = os.path.join(base_dir, "sample_data.csv")
    df = Loader.get_historical_data(
        test_file_path, Source.LocalData, base_date, TimeFrame.Weekly
    )

    assert (df.columns.sort_values() == data_source_required_columns).all()


def test_that_local_data_source_raise_filenotfound_error():
    with pytest.raises(FileNotFoundError):
        df = Loader.get_historical_data(
            "unknow_file", Source.LocalData, base_date, TimeFrame.Weekly
        )


def test_that_we_can_load_from_stooq():
    df = Loader.get_historical_data("BTCUSD", Source.Stooq, base_date)
    assert (df.columns.sort_values() == data_source_required_columns).all()


def test_stooq_fail_load_apple():
    with pytest.raises(NameError):
        df = Loader.get_historical_data("AAPL", Source.Stooq, base_date)


def test_tiingo_can_load_data():
    df = Loader.get_historical_data("AAPL", Source.Tiingo, base_date)
    assert (df.columns.sort_values() == data_source_required_columns).all()

import datetime as dt
from typing import List, Dict

import pandas as pd
import pytest
from marketdata.transform import resample_data


def test_resample_empty_dataframe_return_empty_data_frame():
    df = pd.DataFrame()
    df_result = resample_data(df)
    assert df_result.empty


@pytest.mark.parametrize(
    "tested_column", [("date"), ("open"), ("high"), ("low"), ("close")]
)
def test_throw_error_when_input_doesnt_contain_open(tested_column):
    with pytest.raises(AssertionError):
        data = [
            {
                column_name: 1
                for column_name in ["date", "open", "high", "low", "close"]
                if column_name != tested_column
            }
        ]
        df = pd.DataFrame(data)
        df_result = resample_data(df)


@pytest.mark.parametrize(
    "input, output, test_comment",
    [
        (
            [
                {
                    "date": dt.datetime(2019, 1, 7),
                    "open": 10.0,
                    "high": 15.0,
                    "low": 5.0,
                    "close": 12.0,
                },
                # {"date": dt.datetime(2018, 1, 8), "open": 12, "high": 16, "low": 10, "close": 16}],
            ],
            [
                {
                    "date": dt.datetime(2019, 1, 7),
                    "open": 10.0,
                    "high": 15.0,
                    "low": 5.0,
                    "close": 12.0,
                }
            ],
            "One date on monday return the same date",
        ),
        (
            [
                {
                    "date": dt.datetime(2019, 1, 7),
                    "open": 10.0,
                    "high": 15.0,
                    "low": 5.0,
                    "close": 12.0,
                },
                {
                    "date": dt.datetime(2019, 1, 8),
                    "open": 12.0,
                    "high": 16.0,
                    "low": 10.0,
                    "close": 16.0,
                },
                # {"date": dt.datetime(2018, 1, 9), "open": 16, "high": 16, "low": 9, "close": 12},
            ],
            [
                {
                    "date": dt.datetime(2019, 1, 7),
                    "open": 10.0,
                    "high": 16.0,
                    "low": 5.0,
                    "close": 16.0,
                }
            ],
            "two date in the same week return one candle",
        ),
        (
            [
                {
                    "date": dt.datetime(2019, 1, 8),
                    "open": 10.0,
                    "high": 15.0,
                    "low": 5.0,
                    "close": 12.0,
                },
                {
                    "date": dt.datetime(2019, 1, 9),
                    "open": 12.0,
                    "high": 16.0,
                    "low": 10.0,
                    "close": 16.0,
                },
                # {"date": dt.datetime(2018, 1, 9), "open": 16, "high": 16, "low": 9, "close": 12},
            ],
            [
                {
                    "date": dt.datetime(2019, 1, 7),
                    "open": 10.0,
                    "high": 16.0,
                    "low": 5.0,
                    "close": 16.0,
                }
            ],
            "two date in the same week not starting on Monday return one candle",
        ),
        (
            [
                {
                    "date": dt.datetime(2019, 1, 8),
                    "open": 10.0,
                    "high": 15.0,
                    "low": 5.0,
                    "close": 12.0,
                },
                {
                    "date": dt.datetime(2019, 1, 9),
                    "open": 12.0,
                    "high": 16.0,
                    "low": 10.0,
                    "close": 16.0,
                },
                {
                    "date": dt.datetime(2019, 1, 21),
                    "open": 18.0,
                    "high": 21.0,
                    "low": 17.0,
                    "close": 20.0,
                },
                # {"date": dt.datetime(2018, 1, 9), "open": 16, "high": 16, "low": 9, "close": 12},
            ],
            [
                {
                    "date": dt.datetime(2019, 1, 7),
                    "open": 10.0,
                    "high": 16.0,
                    "low": 5.0,
                    "close": 16.0,
                },
                {
                    "date": dt.datetime(2019, 1, 21),
                    "open": 18.0,
                    "high": 21.0,
                    "low": 17.0,
                    "close": 20.0,
                },
            ],
            "two date in the same week not starting on Monday return one candle",
        ),
        (
            [
                {
                    "date": dt.datetime(2019, 1, 7),
                    "open": 10.0,
                    "high": 15.0,
                    "low": 5.0,
                    "close": 12.0,
                    "volume": 100.0,
                },
                {
                    "date": dt.datetime(2019, 1, 8),
                    "open": 10.0,
                    "high": 15.0,
                    "low": 5.0,
                    "close": 12.0,
                    "volume": 150.0,
                },
                {
                    "date": dt.datetime(2019, 1, 9),
                    "open": 10.0,
                    "high": 15.0,
                    "low": 5.0,
                    "close": 12.0,
                    "volume": 50.0,
                },
            ],
            [
                {
                    "date": dt.datetime(2019, 1, 7),
                    "open": 10.0,
                    "high": 15.0,
                    "low": 5.0,
                    "close": 12.0,
                    "volume": 300.0,
                }
            ],
            "When column volume exist return the sum for the column volume",
        ),
    ],
)
def test_input_output_result(
    input: List[Dict[str, object]], output: List[Dict[str, object]], test_comment: str
):
    df_input = pd.DataFrame(input).set_index("date")
    df_output = pd.DataFrame(output).set_index("date")

    df_result = resample_data(df_input)
    pd.testing.assert_frame_equal(
        df_result, df_output, check_less_precise=True, check_like=True, check_names=True
    )


# logic = {'Open'  : 'first',
#          'High'  : 'max',
#          'Low'   : 'min',
#          'Close' : 'last',
#          'Volume': 'sum'}
#
# offset = pd.offsets.timedelta(days=-6)
#
# f = pd.read_clipboard(parse_dates=['Date'], index_col=['Date'])
# f.resample('W', loffset=offset).apply(logic)

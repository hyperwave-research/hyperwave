import pandas as pd
import os

from os import path

import pytz
from marketdata import TimeFrame

ENV_HW_DATA_ROOT_FOLDER = "HW_DATA_ROOT_FOLDER"


class LocalDataLoader:
    def __init__(self, symbol: str, time_frame: TimeFrame = TimeFrame.Weekly):
        self._file_name = symbol  # "{}.csv".format(symbol)
        self._time_frame = time_frame

    def get_dataframe(self):
        root_path = os.getenv(ENV_HW_DATA_ROOT_FOLDER, None)

        file_path = path.abspath (path.expanduser(
            path.join(root_path, self._file_name) if root_path else self._file_name
        ))
        if not path.exists(file_path):
            raise FileNotFoundError(
                "Cannot find the data in the path {}. The root folder is {}. You can set the env variable {} for the root path".format(
                    file_path, root_path, ENV_HW_DATA_ROOT_FOLDER
                )
            )

        df = pd.read_csv(file_path, header=0, parse_dates=True)
        df = df.rename(columns={column: column.lower() for column in df.columns})
        df.loc[:, "date"] = pd.to_datetime(df.loc[:, "date"])
        df = df.set_index("date").tz_localize(tz=pytz.utc, level=0)
        df["date"] = df.index
        return df

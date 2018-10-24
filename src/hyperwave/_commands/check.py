import os

import pandas as pd
from hyperwave import Source, TimeFrame, OhlcLoader, Hyperwave


def func_check(args):
    df_raw_data = OhlcLoader.get_historical_data(args.symbol, args.source, time_frame=TimeFrame.Weekly)
    hw = Hyperwave.get_standard_hyperwave()
    (df_hull_hyperwave, hw_phases_temp, hyperwave) =  hw.get_hyperwave(df_raw_data)

    print(df_hull_hyperwave)
    print(hw_phases_temp)
    print(hyperwave)


def set_command(subparsers, parents):
    download_parse = subparsers.add_parser("check", parents=parents,
                                           description="check the given symbol is on Hyperwave")
    download_parse.add_argument('--source', type=Source.from_string, choices=list(Source))
    download_parse.add_argument('--symbol', type=str, help="The synbol for which you want to download the data")
    download_parse.add_argument('--outputType', type=str,choices=["display", "file"], default="display", help="Set the output source. Default display")

    download_parse.set_defaults(func=func_check)

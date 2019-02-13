import os
import pandas as pd
from marketdata.transform import split_column_to_ohlc, resample_data
from marketdata import TimeFrame
from marketdata import Loader
from marketdata import Source
from tqdm import tqdm


def func_resample(args):
    output_path = args.outputPath
    input_path = args.inputPath
    resample_time = "W"

    print("Resample input data to:")
    print("Input path : {}".format(input_path))
    print("Output path : {}".format(output_path))
    print("Resample to : {}".format(resample_time))

    files = [input_path] if os.path.isfile(input_path) else os.listdir(input_path)

    with tqdm(total=len(files)) as pbar:
        for file in files:
            full_path = os.path.join(input_path, file)
            df = Loader.get_historical_data(
                full_path, Source.LocalData, time_frame=TimeFrame.Daily
            )
            df = df.set_index("date")
            result_df = resample_data(df, resample_time)
            full_path = os.path.join(output_path, file)
            result_df.to_csv(full_path, index=True, header=True)
            pbar.set_description("done %s" % file)
            pbar.update(1)
        # for result in split_column_to_ohlc(df):


def set_command(subparsers, parents):
    resample_parser = subparsers.add_parser(
        "resample",
        parents=parents,
        description="Resample daily candle to weekly or monthly",
    )

    resample_parser.add_argument(
        "--inputPath", type=str, help="Path to the input csv file you want split data"
    )

    resample_parser.add_argument(
        "--outputPath",
        type=str,
        help="Path to the directory you want to want to save the OHLC",
    )

    resample_parser.set_defaults(func=func_resample)

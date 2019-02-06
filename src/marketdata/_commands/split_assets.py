import os
import pandas as pd
from marketdata.transform import split_column_to_ohlc


def func_split_asset(args):
    output_path = args.outputPath
    input_path = args.inputPath

    print("Split Asset :")
    print("Input path : {}".format(input_path))
    print("Output path : {}".format(output_path))

    df = pd.read_csv(input_path)
    for result in split_column_to_ohlc(df):
        full_path = os.path.join(output_path, "{}.csv".format(result.name))
        result.df.to_csv(full_path, index=False, header=True)


def set_command(subparsers, parents):
    split_asset_parser = subparsers.add_parser(
        "split-assets",
        parents=parents,
        description="Split an input csv file to OHLC candle using the price for the day",
    )

    split_asset_parser.add_argument(
        "--inputPath", type=str, help="Path to the input csv file you want split data"
    )

    split_asset_parser.add_argument(
        "--outputPath",
        type=str,
        help="Path to the directory you want to want to save the OHLC",
    )

    split_asset_parser.set_defaults(func=func_split_asset)

import argparse

from hyperwave import Source, TimeFrame


def func_download(args):
    print("============ Call download ==============")
    print(args)


def set_command(subparsers):
    download_parse = subparsers.add_parser("download",
                                           description="Download the given symbol and save the data to the output path")
    download_parse.add_argument('--source', type=Source.from_string, choices=list(Source))
    download_parse.add_argument('--symbol', type=str, help="The synbol for which you want to download the data")
    download_parse.add_argument('--output', type=str,
                                help="Path to the file you want to save the Open, High, Low, Close data")
    download_parse.add_argument('--timeframe', type=TimeFrame.from_string, choices=list(TimeFrame),
                                default=TimeFrame.Weekly, required=False,
                                help="Timeframe of the data. Default value Weekly")

    download_parse.set_defaults(func=func_download)

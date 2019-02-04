import multiprocessing

from marketdata import TimeFrame, Groups, GroupComposition, Source
from marketdata._commands.helper import fetch_symbols


def func_download_index(args):
    source = Source.Stooq
    index = args.index
    ticker_infos = GroupComposition[index]
    output_path = args.outputPath
    time_frame = args.timeframe
    nb_thread = args.nbThread

    print("Download data :")
    print("Source : {}".format(source))
    print("Index: {}".format(index))
    print("Symbols : {}".format([ticker_info.ticker for ticker_info in ticker_infos]))
    print("Time frame : {}".format(time_frame))
    print("Nb Thread : {}".format(nb_thread))

    fetch_symbols(ticker_infos, output_path, time_frame, nb_thread)


def set_command(subparsers, parents):
    download_parse = subparsers.add_parser(
        "download-index",
        parents=parents,
        description="Download the given symbol and save the data to the output path",
    )

    download_parse.add_argument(
        "--index", type=Groups.from_string, choices=list(Groups)
    )

    download_parse.add_argument(
        "--outputPath",
        type=str,
        help="Path to the file you want to save the Open, High, Low, Close data",
    )
    download_parse.add_argument(
        "--timeframe",
        type=TimeFrame.from_string,
        choices=list(TimeFrame),
        default=TimeFrame.Weekly,
        required=False,
        help="Timeframe of the data. Default value Weekly",
    )
    download_parse.add_argument(
        "--nbThread",
        type=int,
        default=multiprocessing.cpu_count() * 2,
        required=False,
        help="Number of parallel load. Default(1)",
    )
    download_parse.set_defaults(func=func_download_index)

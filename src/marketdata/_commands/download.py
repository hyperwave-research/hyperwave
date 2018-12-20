import multiprocessing

from marketdata import Source, TimeFrame, TickerInfo
from marketdata._commands.helper import fetch_symbols


def func_download(args):
    source = args.source
    symbols = args.symbols.split(',')
    output_path = args.outputPath
    time_frame = args.timeframe
    nb_thread = args.nbThread

    print("Download data :")
    print("Source : {}".format(source))
    print("Symbols : {}".format(symbols))
    print("Time frame : {}".format(time_frame))
    print("Nb Thread : {}".format(nb_thread))

    fetch_symbols([TickerInfo(s, source, s) for s in symbols], output_path, time_frame, nb_thread)


def set_command(subparsers, parents):
    download_parse = subparsers.add_parser("download",
                                           parents=parents,
                                           description="Download the given symbol and save the data to the output path")
    download_parse.add_argument('--source',
                                type=Source.from_string,
                                choices=list(Source))
    download_parse.add_argument('--symbols',
                                type=str,
                                help="The synbols for which you want to download the data. separated by ','")
    download_parse.add_argument('--outputPath',
                                type=str,
                                help="Path to the file you want to save the Open, High, Low, Close data")
    download_parse.add_argument('--timeframe',
                                type=TimeFrame.from_string, choices=list(TimeFrame),
                                default=TimeFrame.Weekly, required=False,
                                help="Timeframe of the data. Default value Weekly")
    download_parse.add_argument('--nbThread', type=int, default=multiprocessing.cpu_count() * 2, required=False,
                                help="Number of parallel load. Default(1)")
    download_parse.set_defaults(func=func_download)

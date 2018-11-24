from os import path

from hyperwave import TimeFrame, OhlcLoader, Index, IndexComposition
from tqdm import tqdm


def func_download(args):
    index_composition = IndexComposition.get(args.index)
    output_path = args.outputPath

    with tqdm(total=len(index_composition)) as pbar:
        def download_data(source, symbol, ticker):
            file_name = '{}.csv'.format(symbol)
            output_file_path = path.join(output_path, file_name )
            pbar.set_description("Processing %s" % symbol)

            if not args.override and path.exists(output_file_path):
                return

            df_raw_data = OhlcLoader.get_historical_data(symbol, source, time_frame=TimeFrame.Weekly)
            df_raw_data.to_csv(output_file_path , columns=['date', 'close', 'high', 'low', 'open'], index=False, header=True)
            pbar.update(1)

        for info in index_composition:
            download_data(info['source'], info['ticker'], info['ticker'])




def set_command(subparsers, parents):
    download_index_parser = subparsers.add_parser("download-index",parents=parents,
                                           description="Download the given symbol and save the data to the output path")
    download_index_parser.add_argument('--index', type=Index.from_string, choices=list(Index))
    download_index_parser.add_argument('--outputPath', type=str,
                                help="Path to the file you want to save the Open, High, Low, Close data")
    download_index_parser.add_argument('--override', type=bool, default=True,
                                help="force override the data is the file exist")
    download_index_parser.add_argument('--timeframe', type=TimeFrame.from_string, choices=list(TimeFrame),
                                default=TimeFrame.Weekly, required=False,
                                help="Timeframe of the data. Default value Weekly")

    download_index_parser.set_defaults(func=func_download)

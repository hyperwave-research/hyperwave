import os

from datareader import Groups, Loader, TimeFrame, GroupComposition, Source
from hyperwave import Hyperwave
from tqdm import tqdm
import pandas as pd

def func_check(args):
    hw = Hyperwave.get_standard_hyperwave()

    base_dir = os.path.abspath(args.inputPath)
    # os.environ["HW_DATA_ROOT_FOLDER"] = base_dir

    tickers = [(os.path.splitext(os.path.basename(file))[0],
                os.path.join(base_dir, file))for file in os.listdir(base_dir)]

    with tqdm(total=len(tickers)) as pbar:
        def get_hyperwave_from_source(source, symbol, ticker):
            pbar.set_description("Processing %s" % symbol)
            df_raw_data = Loader.get_historical_data(symbol, source, time_frame=TimeFrame.Weekly)

            (df_hull_hyperwave, hw_phases_temp, hyperwave) = hw.get_hyperwave(df_raw_data)
            hyperwave['ticker'] = ticker
            pbar.update(1)
            return hyperwave

        result = [get_hyperwave_from_source(Source.LocalData, ticker[1], ticker[0]) for ticker in
                  tickers]

    hyperwaves = pd.concat(result)

    print(hyperwaves)
    hyperwaves.to_csv(args.outputPath)

def set_command(subparsers, parents):
    check_parser = subparsers.add_parser("check-index-folder", parents=parents,
                                         description="check the given index for hyperwave")
    check_parser.add_argument('--inputPath', type=str, default='.')
    check_parser.add_argument('--outputPath', type=str, default='hyperwaves.csv', help="Path to the folder where we persist the result")

    check_parser.set_defaults(func=func_check)

import os

from consensio import consensio
from hyperwave import OhlcLoader, TimeFrame, Source
from tqdm import tqdm
import pandas as pd

def func_check(args):
    base_dir = os.path.abspath(args.inputPath)
    os.environ["HW_DATA_ROOT_FOLDER"] = base_dir

    tickers = [os.path.splitext(os.path.basename(file))[0] for file in os.listdir(base_dir)]

    with tqdm(total=len(tickers)) as pbar:
        def get_hyperwave_from_source(source, symbol, ticker):
            pbar.set_description("Processing %s" % symbol)
            df_raw_data = OhlcLoader.get_historical_data(symbol, source, time_frame=TimeFrame.Weekly)

            result = consensio.get_consonsio( df_raw_data)[['date', 'consensio']].rename(columns={'consensio': symbol}).reset_index(drop=True).set_index('date')
            pbar.update(1)
            return result

        result = [get_hyperwave_from_source(Source.LocalData, ticker, ticker) for ticker in
                  tickers]

    consensios = pd.concat(result, axis=1)

    print(consensios)
    consensios.to_csv(args.outputPath)

def set_command(subparsers, parents):
    check_parser = subparsers.add_parser("calculate", parents=parents,
                                         description="check the given index for hyperwave")
    check_parser.add_argument('--inputPath', type=str, default='.')
    check_parser.add_argument('--outputPath', type=str, default='hyperwaves.csv', help="Path to the folder where we persist the result")

    check_parser.set_defaults(func=func_check)

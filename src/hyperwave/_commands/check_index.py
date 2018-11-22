from hyperwave import Index, OhlcLoader, Hyperwave, TimeFrame, IndexComposition
from tqdm import tqdm
import pandas as pd

def func_check(args):
    hw = Hyperwave.get_standard_hyperwave()
    index_composition = IndexComposition.get(args.name)

    with tqdm(total=len(index_composition)) as pbar:
        def get_hyperwave_from_source(source, symbol, ticker):
            pbar.set_description("Processing %s" % symbol)
            df_raw_data = OhlcLoader.get_historical_data(symbol, source, time_frame=TimeFrame.Weekly)

            (df_hull_hyperwave, hw_phases_temp, hyperwave) = hw.get_hyperwave(df_raw_data)
            hyperwave['ticker'] = ticker
            pbar.update(1)
            return hyperwave

        result = [get_hyperwave_from_source(info['source'], info['symbol'], info['ticker']) for info in
                  index_composition]

    hyperwaves = pd.concat(result)

    print(hyperwaves)
    hyperwaves.to_csv(args.outputPath)

def set_command(subparsers, parents):
    check_parser = subparsers.add_parser("check-index", parents=parents,
                                         description="check the given index for hyperwave")
    check_parser.add_argument('--name', type=Index.from_string, choices=list(Index))

    # check_parser.add_argument('--symbol', type=str, help="The synbol for which you want to download the data")
    # check_parser.add_argument('--outputType', type=str,choices=["display", "file"], default="display", help="Set the output source. Default display")
    check_parser.add_argument('--outputPath', type=str, default='hyperwaves.csv', help="Path to the folder where we persist the result")

    check_parser.set_defaults(func=func_check)

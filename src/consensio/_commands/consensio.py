import os

from consensio import consensio
from marketdata import Loader, TimeFrame, Source
from tqdm import tqdm
import pandas as pd


def func_check(args):
    base_dir = os.path.abspath(args.inputPath)

    tickers = [
        (os.path.splitext(os.path.basename(file))[0], os.path.join(base_dir, file))
        for file in os.listdir(base_dir)
    ]

    with tqdm(total=len(tickers)) as pbar:

        def get_hyperwave_from_source(source, symbol, ticker):
            pbar.set_description("Processing %s" % symbol)
            df_raw_data = Loader.get_historical_data(
                symbol, source, time_frame=TimeFrame.Weekly
            )

            result = (
                consensio.get_consonsio(df_raw_data)[["date", "consensio"]]
                .rename(columns={"consensio": ticker})
                .reset_index(drop=True)
                .set_index("date")
            )
            pbar.update(1)
            return result

        result = [
            get_hyperwave_from_source(Source.LocalData, ticker[1], ticker[0])
            for ticker in tickers
        ]

    consensios = pd.concat(result, axis=1)

    consensios.to_csv(args.outputPath)
    # loop = asyncio.get_event_loop()
    #
    # loop.run_in_executor()


def set_command(subparsers, parents):
    check_parser = subparsers.add_parser(
        "calculate", parents=parents, description="check the given index for hyperwave"
    )
    check_parser.add_argument("--inputPath", type=str, default=".")
    check_parser.add_argument(
        "--outputPath",
        type=str,
        default="hyperwaves.csv",
        help="Path to the folder where we persist the result",
    )

    check_parser.set_defaults(func=func_check)

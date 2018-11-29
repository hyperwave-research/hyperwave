import concurrent.futures
from os import path
from typing import List

from datareader import TimeFrame, Source, Loader
from tqdm import tqdm


def task_fetch_symbol(source: Source, symbol: str, outputPath: str, timeframe: TimeFrame):
    data = Loader.get_historical_data(symbol, source, time_frame=timeframe)
    data.to_csv(outputPath, columns=['date', 'close', 'high', 'low', 'open'], index=False, header=True)


def fetch_symbols(source: Source, symbols: List[str], output_path: str, time_frame: TimeFrame, nb_thread: int):
    if nb_thread > 1:
        with concurrent.futures.ThreadPoolExecutor(max_workers=nb_thread) as executor:
            # Start the load operations and mark each future with its URL
            future_to_url = {
                executor.submit(task_fetch_symbol, source, symbol, path.join(output_path, "{}.csv".format(symbol)),
                                time_frame): symbol for symbol in symbols}
            with tqdm(total=len(symbols)) as pbar:
                for future in concurrent.futures.as_completed(future_to_url):
                    symbol = future_to_url[future]
                    try:
                        data = future.result()
                    except Exception as exc:
                        pbar.set_description('%r generated an exception: %s' % (symbol, exc))
                    else:
                        pbar.set_description("Processing %s" % symbol)
                    pbar.update(1)
    else:
        with tqdm(total=len(symbols)) as pbar:
            for symbol in symbols:
                task_fetch_symbol(source, symbol, path.join(output_path, "{}.csv".format(symbol)), time_frame)
                pbar.set_description("Processing %s" % symbol)
                pbar.update(1)
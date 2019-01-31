import asyncio
from concurrent.futures.thread import ThreadPoolExecutor
from os import path
from typing import List

from marketdata import TimeFrame, Source, Loader
from marketdata import TickerInfo
from tqdm import tqdm



def task_fetch_symbol(source: Source, symbol: str, output_path: str, timeframe: TimeFrame):
    try:
        data = Loader.get_historical_data(symbol, source, time_frame=timeframe)
        data.to_csv(output_path, columns=['date', 'close', 'high', 'low', 'open'], index=False, header=True)
    except:
        return (False, symbol)

    return (True, symbol)

def fetch_symbols(ticker_infos: List[TickerInfo], output_path: str, time_frame: TimeFrame, nb_thread: int):
    event_loop = asyncio.new_event_loop()
    # asyncio.set_event_loop( event_loop )
    p = ThreadPoolExecutor( nb_thread )

    async def load_data():
        with tqdm(total=len(ticker_infos)) as pbar:
            futures = [event_loop.run_in_executor(p, task_fetch_symbol, ticker_info.source, ticker_info.symbol,
                                            path.join(output_path, "{}.csv".format(ticker_info.ticker)), time_frame) for
                       ticker_info in ticker_infos]
            while futures:
                done, futures = await asyncio.wait(futures, return_when=asyncio.FIRST_COMPLETED)
                for f in done:
                    no_error, symbol = await f
                    if no_error:
                        pbar.set_description("done %s" % symbol)
                    else:
                        pbar.set_description("Error %s" % symbol)
                    pbar.update(1)


    try:
        event_loop.run_until_complete(load_data())
    finally:
        event_loop.close()

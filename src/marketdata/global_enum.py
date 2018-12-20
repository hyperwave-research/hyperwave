from helpers import AdvanceEnum


class Source(AdvanceEnum):
    CryptoCompare = 1
    Investopedia = 2
    LocalData = 3
    Stooq = 4
    Tiingo = 5


class TimeFrame(AdvanceEnum):
    Daily = 1
    Weekly = 2

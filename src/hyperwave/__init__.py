"""Minimal Project Task Management."""

from .hyperwave import (  # noqa: F401
    Hyperwave
)
from hyperwave.hyperwave_grouping import HyperwaveGrouping, HyperwaveWeekLenghtGrouping, HyperwavePhaseGrouper, \
    HyperwaveGroupingPhasePercent, HyperwaveGroupingPhaseAggregator

from .ohlc_loader import  (  # noqa: F401
    OhlcLoader,
    Source
)

__version__ = '0.1.0'
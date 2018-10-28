"""Minimal Project Task Management."""


from .hyperwave_grouping import (
    HyperwaveGrouping,
    HyperwaveWeekLenghtGrouping,
    HyperwavePhaseGrouper,
    HyperwaveGroupingPhasePercent,
    HyperwaveGroupingPhaseAggregator,
    HyperwaveGroupingToPhase4,
    HyperwaveGrouperSmallWeek,
    HyperwaveGrouperByMedianSlopeIncrease
)


from .hyperwave import (  # noqa: F401
    Hyperwave
)

from .ohlc_loader import  (  # noqa: F401
    OhlcLoader,
    Source,
    TimeFrame
)

from .main import Main

__version__ = '0.1.0'
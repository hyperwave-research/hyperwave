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



from .ohlc_loader import (
    OhlcLoader,
    Source,
    TimeFrame
)

from .index import (
    Index,
    IndexComposition
)

from .hyperwave import (
    Hyperwave,
)



from .main import Main

__version__ = '0.1.0'


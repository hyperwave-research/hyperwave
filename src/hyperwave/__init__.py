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


from .global_enum import (
    Source,
    TimeFrame
)

from .ohlc_loader import (
    OhlcLoader,
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


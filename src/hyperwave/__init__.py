"""Minimal Project Task Management."""

from .hyperwave_grouping import (
    HyperwaveGrouping,
    HyperwaveWeekLenghtGrouping,
    HyperwavePhaseGrouper,
    HyperwaveGroupingPhasePercent,
    HyperwaveGroupingPhaseAggregator,
    HyperwaveGroupingToPhase4,
    HyperwaveGrouperSmallWeek,
    HyperwaveGrouperByMedianSlopeIncrease,
)

from .hyperwave import Hyperwave


from .main import Main

__version__ = "0.1.0"

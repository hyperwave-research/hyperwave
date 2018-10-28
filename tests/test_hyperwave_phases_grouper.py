from datetime import datetime
from typing import List

import pandas as pd
import pytest
from hyperwave import HyperwaveWeekLenghtGrouping, HyperwavePhaseGrouper, HyperwaveGroupingPhasePercent, \
    HyperwaveGroupingPhaseAggregator, HyperwaveGroupingToPhase4, HyperwaveGrouperByMedianSlopeIncrease, \
    HyperwaveGrouping, HyperwaveGrouperSmallWeek


def get_path_row(
        x1: int = 0, x1_date: datetime = datetime(2000, 1, 1), x1_normalize: float = 0.0,
        x2: int = 0, x2_date: datetime = datetime(2000, 1, 1), x2_normalize: float = 0.0,
        y1: float = 0.0, y1_normalize: float = 0.0,
        y2: float = 0.0, y2_normalize: float = 0.0,
        m: float = 0.0, b: float = 0.0, m_normalize: float = 0.0, b_normalize: float = 0.0,
        angle: float = 0.0, angle_normalize: float = 0.0,
        weeks: int = 0, mean_error: float = 0.0, nb_is_lower: int = 0,
        ratio_error_cut: float = 0.0, ratio_slope_y1_normalize: float = 0.0, ratio_slope_y2_normalize: float = 0.0):
    return {
        'x1': x1, 'x1_date': x1_date, 'x1_normalize': x1_normalize,
        'x2': x2, 'x2_date': x2_date, 'x2_normalize': x2_normalize,
        'y1': y1, 'y1_normalize': y1_normalize,
        'y2': y2, 'y2_normalize': y2_normalize,
        'm': m, 'b': b, 'm_normalize': m_normalize, 'b_normalize': b_normalize,
        'angle': angle, 'angle_normalize': angle_normalize,
        'weeks': weeks, 'mean_error': mean_error, 'nb_is_lower': nb_is_lower,
        'ratio_error_cut': ratio_error_cut, 'ratio_slope_y1_normalize': ratio_slope_y1_normalize,
        'ratio_slope_y2_normalize': ratio_slope_y2_normalize
    }


@pytest.mark.parametrize("raw_path, expected_phases, increase_factor, test_conment", [
    ([get_path_row()], [[0]], 2.0, "one row return the row if greater than zero"),
    ([
         get_path_row(),
         get_path_row()
     ], [[0, 1]], 2.0, "Two path with m_normalize equal zero should return an array with both element"),
    ([
         get_path_row(m_normalize=-0.5),
         get_path_row(m_normalize=-1.0)
     ], [], 2.0, "Path with only negative elements should return empty array"),
    ([
         get_path_row(m_normalize=-0.5),
         get_path_row(m_normalize=1.0)
     ], [[1]], 2.0, "Path with only one positive m_normalize should retunr an array with one element"),
    ([
         get_path_row(m_normalize=0.5),
         get_path_row(m_normalize=0.7)
     ], [[0, 1]], 2.0,
     "Path with two positive m_normalize without increase factor should return an array with both elements id"),
    ([
         get_path_row(m_normalize=0.5),
         get_path_row(m_normalize=1.1)
     ], [[0], [1]], 2.0,
     "Path with two positive m_normalize with increase factor greated should return an array with two array"),
    ([
         get_path_row(m_normalize=0.5),
         get_path_row(m_normalize=1.1),
         get_path_row(m_normalize=1.5)
     ], [[0], [1, 2]], 2.0, "Path m_normalize [0.5, 1.1, 1.5] should return [[0],[1, 2]]"),
    ([
         get_path_row(m_normalize=0.5),
         get_path_row(m_normalize=1.1),
         get_path_row(m_normalize=1.5)
     ], [[0], [1, 2]], 2.0, "Path m_normalize [0.5, 1.1, 1.5] should return [[0],[1, 2]]"),
    ([
         get_path_row(m_normalize=0.5),
         get_path_row(m_normalize=1.1),
         get_path_row(m_normalize=1.5),
         get_path_row(m_normalize=2.2),
     ], [[0], [1, 2, 3]], 2.0, "Path m_normalize [0.5, 1.1, 1.5, 2.2] should return [[0],[1, 2, 3]]"),
    ([
         get_path_row(m_normalize=0.5),
         get_path_row(m_normalize=1.1),
         get_path_row(m_normalize=1.5),
         get_path_row(m_normalize=2.4),
     ], [[0], [1, 2], [3]], 2.0, "Path m_normalize [0.5, 1.1, 1.5, 2.4] should return [[0],[1, 2], [3]]"),
    ([
         get_path_row(m_normalize=0.5),
         get_path_row(m_normalize=1.1),
         get_path_row(m_normalize=1.5),
         get_path_row(m_normalize=2.4),
         get_path_row(m_normalize=10),
     ], [[0], [1, 2], [3], [4]], 2.0, "Path m_normalize [0.5, 1.1, 1.5, 2.4, 10] should return [[0],[1, 2], [3], [4]"),
])
def test_that_grouping_return_expected_value(raw_path, expected_phases, increase_factor, test_conment):
    df_path = pd.DataFrame(raw_path)

    hw_phase_grouper = HyperwavePhaseGrouper(increase_factor)
    phases = hw_phase_grouper.group(df_path)
    assert expected_phases == phases, test_conment


@pytest.mark.parametrize("raw_path, input_group, expected_result, group_min_week, only_group_last_phase, test_comment",
                         [
                             ([
                                  get_path_row(weeks=4)
                              ], [[0]], [[0]], 10, True, "one path with weeks lower than should return same input"),
                             ([
                                  get_path_row(weeks=4),
                                  get_path_row(weeks=4)
                              ], [[1]], [[1]], 10, True,
                              "path with two input path but one group should return one group"),
                             ([
                                  get_path_row(weeks=10),
                                  get_path_row(weeks=4)
                              ], [[0], [1]], [[0, 1]], 10, True,
                              "path with two input path and two groups should return one group"),
                             ([
                                  get_path_row(weeks=10),
                                  get_path_row(weeks=4),
                                  get_path_row(weeks=3),
                              ], [[0], [1], [2]], [[0, 1, 2]], 10, True,
                              "initial group [[0], [1], [2]] with weeks [10, 4, 3] shoud return group [[0, 1, 2]]"),
                             ([
                                  get_path_row(weeks=10),
                                  get_path_row(weeks=4),
                                  get_path_row(weeks=3),
                                  get_path_row(weeks=4),
                              ], [[0], [1], [2, 3]], [[0], [1, 2, 3]], 10, True,
                              "initial group [[0], [1], [2, 3]] with weeks [10, 4, 3, 4] shoud return group [[0], [1, 2, 3]]"),
                             ([
                                  get_path_row(weeks=10),
                                  get_path_row(weeks=4),
                                  get_path_row(weeks=7),
                                  get_path_row(weeks=4),
                              ], [[0], [1], [2], [3]], [[0, 1], [2, 3]], 10, False,
                              "initial group [[0], [1], [2, 3]] with weeks [10, 4, 3, 4] shoud return group [[0], [1, 2, 3]]"),
                             ([
                                  get_path_row(weeks=10),
                                  get_path_row(weeks=4),
                                  get_path_row(weeks=7),
                                  get_path_row(weeks=4),
                              ], [[0], [1], [2], [3]], [[0], [1], [2, 3]], 10, True,
                              "initial group [[0], [1], [2, 3]] with weeks [10, 4, 3, 4] shoud return group [[0], [1, 2, 3]]"),
                         ])
def test_grouping_second_step_week_base_when_all_weeks_are_enough_long(raw_path, input_group, expected_result,
                                                                       group_min_week, only_group_last_phase,
                                                                       test_comment):
    df_path = pd.DataFrame(raw_path)
    hw_week_lenght_grouping = HyperwaveWeekLenghtGrouping(group_min_week, only_group_last_phase)
    result_group = hw_week_lenght_grouping.group(df_path, input_group)

    assert expected_result == result_group


@pytest.mark.parametrize("raw_data, expected_result, percent_increase, test_comment", [
    ([], [], 0.7, "Test empty array"),
    ([
         get_path_row(m_normalize=2.4),
     ], [[0]], 0.7, "Test array with only one element"),
    ([
         get_path_row(m_normalize=1),
         get_path_row(m_normalize=1.5)
     ], [[0, 1]], 1.7, "Two elements in the same range"),
    ([
         get_path_row(m_normalize=1),
         get_path_row(m_normalize=2.5)
     ], [[0], [1]], 1.7, "Test array with two elements in different phase"),
    ([
         get_path_row(m_normalize=1),
         get_path_row(m_normalize=1.5),
         get_path_row(m_normalize=1.6),
         get_path_row(m_normalize=3.9),
     ], [[0, 1, 2], [3]], 1.7, "Test array with 4 elements that increase into different phase"),
    ([
         get_path_row(m_normalize=0.353723),
         get_path_row(m_normalize=0.476578),
         get_path_row(m_normalize=1.276563),
         get_path_row(m_normalize=1.601295),
         get_path_row(m_normalize=7.864277),
         get_path_row(m_normalize=11.429688),
         get_path_row(m_normalize=11.589543),
         get_path_row(m_normalize=80.007812),
     ], [[0, 1], [2, 3], [4, 5, 6], [7]], 1.7, "Test array with two elements in different phase"),
])
def test_grouping_phase_percent_increase_no_increase(raw_data, expected_result, percent_increase, test_comment):
    dF_path = pd.DataFrame(raw_data)
    hw_grouping_phase_percent = HyperwaveGroupingPhasePercent(percent_increase=percent_increase)
    result_group = hw_grouping_phase_percent.group(df_path=dF_path)
    assert expected_result == result_group, test_comment


@pytest.mark.parametrize("raw_data, expected_result, group_aggregators, test_comment ", [
    ([], [], [], "Test with everything empty"),
    ([
         get_path_row(m_normalize=1)
     ], [[0]], [HyperwaveGroupingPhasePercent()], "Test one grouping with one row"),
    ([
         get_path_row(m_normalize=1, weeks=15)
     ], [[0]], [HyperwaveGroupingPhasePercent(), HyperwaveWeekLenghtGrouping(10)], "Test grouping with two grouping"),

])
def test_grouping_phase_aggregator(raw_data, expected_result, group_aggregators, test_comment):
    df_path = pd.DataFrame(raw_data)
    hw_grouping_phase_aggregator = HyperwaveGroupingPhaseAggregator(group_aggregators)
    result_group = hw_grouping_phase_aggregator.group(df_path, [])

    assert expected_result == result_group, test_comment


@pytest.mark.parametrize("raw_data, input_group, expected_result, test_comment ", [
    ([], [], [], "Test with everything empty"),
    ([], [[0]], [[0]], "When group is one return the same group"),
    ([], [[0], [1]], [[0], [1]], "When group is two return the same group"),
    ([], [[0], [1], [2]], [[0], [1], [2]], "When group is tree return the same group"),
    ([], [[0], [1], [2]], [[0], [1], [2]], "When group is tree return the same group"),
    ([], [[0], [1], [2], [3]], [[0], [1], [2, 3]], "When group is four return aggregated result"),
    ([], [[0], [1], [2], [3, 4], [5]], [[0], [1], [2, 3, 4, 5]], "When group is four return aggregated result"),
])
def test_grouping_phase_up_to_phase4(raw_data, input_group, expected_result, test_comment):
    df_path = pd.DataFrame(raw_data)
    hw_grouper = HyperwaveGroupingToPhase4()
    result_group = hw_grouper.group(df_path, input_group)
    assert expected_result == result_group, test_comment


@pytest.mark.parametrize("raw_data, input_group, expected_result, test_comment ", [
    ([], [], [], "Test with everything empty"),
    ([get_path_row(m_normalize=0.5), ], [], [[0]], "One item should return a one group with this item"),
    ([
         get_path_row(m_normalize=1),
         get_path_row(m_normalize=2),
     ], [], [[0], [1]], "Two elements should every time be grouped separately"),
    ([
         get_path_row(m_normalize=4),
         get_path_row(m_normalize=6),
     ], [], [[0], [1]], "Two elements should every time be grouped together"),
    ([
         get_path_row(m_normalize=0.5),
         get_path_row(m_normalize=1),
         get_path_row(m_normalize=1.5),
         get_path_row(m_normalize=2),
         get_path_row(m_normalize=6),
         get_path_row(m_normalize=6.5),
         get_path_row(m_normalize=9),
     ], [], [[0], [1], [2, 3], [4, 5, 6]], ""),
    ([
         get_path_row(m_normalize=0.011087),
         get_path_row(m_normalize=0.043478),
         get_path_row(m_normalize=0.054480),
         get_path_row(m_normalize=0.432808),
         get_path_row(m_normalize=2.111662),
         get_path_row(m_normalize=2.719618),
         get_path_row(m_normalize=2.899851),
         get_path_row(m_normalize=2.967290),
         get_path_row(m_normalize=3.433861),
         get_path_row(m_normalize=3.948482),
         get_path_row(m_normalize=9.667921),
         get_path_row(m_normalize=12.907091),
         get_path_row(m_normalize=15.286372),
         get_path_row(m_normalize=58.963515),
     ], [], [[0], [1, 2], [3], [4], [5, 6, 7, 8, 9], [10], [11, 12], [13]], "Amazon data"),
])
def test_grouping_phase_by_median(raw_data, input_group, expected_result, test_comment):
    df_path = pd.DataFrame(raw_data)
    hw_grouper = HyperwaveGrouperByMedianSlopeIncrease()
    result_group = hw_grouper.group(df_path, input_group)
    assert expected_result == result_group, test_comment


@pytest.mark.parametrize("raw_data, input_group, expected_result, test_comment ", [
    ([], [], [], "Test with everything empty"),
    ([get_path_row(weeks=10), ], [[0]], [[0]], "if input group smaller than 3 return input group"),
    ([
         get_path_row(weeks=10),
         get_path_row(weeks=10),
     ], [[0], [1]], [[0], [1]], "if input group smaller than 3 return input group"),
    ([
         get_path_row(weeks=10),
         get_path_row(weeks=10),
         get_path_row(weeks=20),
     ], [[0], [1], [2]], [[0], [1], [2]], "if input group smaller than 3 return input group"),
    ([
         get_path_row(weeks=10),
         get_path_row(weeks=20),
         get_path_row(weeks=19),
         get_path_row(weeks=31),
        get_path_row(weeks=10),
     ], [[0, 1], [2], [3], [4]], [[0, 1, 2], [3], [4]], "Should group 2 with group 1"),
    ([
         get_path_row(weeks=10),
         get_path_row(weeks=23),
         get_path_row(weeks=19),
         get_path_row(weeks=30),
         get_path_row(weeks=10),
     ], [[0, 1], [2], [3], [4]], [[0, 1], [3, 2], [4]], "Should group 2 with group 1"),

])
def test_grouping_low_week_middle(raw_data, input_group, expected_result, test_comment):
    df_path = pd.DataFrame(raw_data)
    hw_grouper = HyperwaveGrouperSmallWeek(0.5)
    result_group = hw_grouper.group(df_path, input_group)
    assert expected_result == result_group, test_comment

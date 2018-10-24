import itertools
from typing import List

import logging
import numpy as np
import pandas as pd


class HyperwaveGrouping(object):
    def group(self, df_path: pd.DataFrame, input_group: List[List[int]] = []) -> List[List[int]]:
        pass


class HyperwaveWeekLenghtGrouping(HyperwaveGrouping):
    def __init__(self, group_min_weeks: int, only_group_last_phase: bool = True):
        self.group_min_weeks = group_min_weeks
        self.only_group_last_phase = only_group_last_phase

    def group(self, df_path: pd.DataFrame, input_group: List[List[int]]) -> List[List[int]]:
        hw_phase = input_group.copy()

        for i in np.arange(len(hw_phase), 1, -1):
            phase = hw_phase[i - 1]
            if self._sum_group_weeks(df_path, phase) < self.group_min_weeks:
                hw_phase.remove(phase)
                hw_phase[i - 2].extend(phase)
            else:
                if self.only_group_last_phase:
                    break

        return hw_phase

    @staticmethod
    def _sum_group_weeks(df, group):
        return df.loc[group].sum()['weeks']


class HyperwaveWeekLengthPhase1Grouping(HyperwaveGrouping):

    def group(self, df_path: pd.DataFrame, input_group: List[List[int]]) -> List[List[int]]:
        hyperwave_total_weeks = df_path["weeks"].sum()
        phase1_min_nb_weeks = hyperwave_total_weeks * 0.25

        week_grouping = HyperwaveWeekLenghtGrouping(phase1_min_nb_weeks, True)
        reversed_list = list(reversed(input_group))
        result_grouping = week_grouping.group(df_path, reversed_list)
        result_grouping = list(reversed(result_grouping))
        return result_grouping


class HyperwaveWeekLengthPhase4Grouping(HyperwaveGrouping):

    def group(self, df_path: pd.DataFrame, input_group: List[List[int]]) -> List[List[int]]:
        hyperwave_total_weeks = df_path["weeks"].sum()
        phase4_min_nb_weeks = hyperwave_total_weeks * 0.06

        week_grouping = HyperwaveWeekLenghtGrouping(phase4_min_nb_weeks, True)
        return week_grouping.group(df_path, input_group)


class HyperwavePhaseGrouper(HyperwaveGrouping):
    def __init__(self, phase_increase_factor: float = 2.0):
        self.phase_increase_factor = phase_increase_factor

    def group(self, df_path: pd.DataFrame, input_group: List[List[int]] = []) -> List[List[int]]:
        df_positive_m = df_path[df_path['m_normalize'] >= 0]
        if df_positive_m.shape[0] == 0:
            return []

        current_phase_m = df_positive_m.iloc[0].m_normalize
        hw_phases_temp = []
        hw_current_phase = [df_positive_m.index[0]]

        for index, row in df_positive_m.drop(df_positive_m.index[0]).iterrows():
            if row.m_normalize <= current_phase_m * self.phase_increase_factor:
                hw_current_phase.append(index)
            else:
                hw_phases_temp.append(hw_current_phase)
                hw_current_phase = [index]
                current_phase_m = row.m_normalize

        hw_phases_temp.append(hw_current_phase)

        return hw_phases_temp


class HyperwaveGroupingPhasePercent(HyperwaveGrouping):
    def __init__(self, percent_increase=0.7):
        self.percent_increase = percent_increase

    def group(self, df_path: pd.DataFrame, input_group: List[List[int]] = []):

        if df_path.empty:
            return []
        df_positive_m = df_path[df_path['m_normalize'] >= 0]
        if df_positive_m.shape[0] == 0:
            return []

        hw_phases_temp = []
        previous_m_normalize = df_positive_m.iloc[0].m_normalize
        hw_current_phase = [df_positive_m.index[0]]

        for index, row in df_positive_m.drop(df_positive_m.index[0]).iterrows():
            current_phase_grow = (row.m_normalize - previous_m_normalize) / previous_m_normalize

            if current_phase_grow <= self.percent_increase:
                hw_current_phase.append(index)
            else:
                hw_phases_temp.append(hw_current_phase)
                hw_current_phase = [index]
                previous_m_normalize = row.m_normalize

        hw_phases_temp.append(hw_current_phase)

        return hw_phases_temp


class HyperwaveGrouperByMedianSlopeIncrease(HyperwaveGrouping):

    def group(self, df_path: pd.DataFrame, input_group: List[List[int]] = []) -> List[List[int]]:
        if df_path.empty:
            return []

        df_positive_m = df_path[df_path['m_normalize'] >= 0]
        if df_positive_m.shape[0] == 0:
            return []

        median = df_positive_m["m_normalize"].pct_change().dropna().median()
        logging.debug("median value {}".format(median))
        return HyperwaveGroupingPhasePercent(median).group(df_path, input_group)


class HyperwaveGrouperByMeanSlopeIncrease(HyperwaveGrouping):

    def group(self, df_path: pd.DataFrame, input_group: List[List[int]] = []) -> List[List[int]]:
        if df_path.empty:
            return []

        df_positive_m = df_path[df_path['m_normalize'] >= 0]
        if df_positive_m.shape[0] == 0:
            return []

        df_changes = df_positive_m["m_normalize"].pct_change().dropna()
        mean_raw_data = df_changes.mean()
        sd_raw_data = df_changes.std()
        up_value = mean_raw_data + sd_raw_data * 2
        low_value = mean_raw_data - sd_raw_data * 2

        df_changes = df_changes[(df_changes >= low_value)]
        df_changes = df_changes[(df_changes <= up_value)]
        mean = df_changes.mean()
        logging.debug("mean value {}".format(mean))
        return HyperwaveGroupingPhasePercent(mean).group(df_path, input_group)


class HyperwaveGroupingPhaseAggregator(HyperwaveGrouping):

    def __init__(self, hw_grouping: List[HyperwaveGrouping]):
        self.hw_grouping = hw_grouping

    def group(self, df_path: pd.DataFrame, input_group: List[List[int]] = []) -> List[List[int]]:
        group_result = input_group.copy()

        for hw_group in self.hw_grouping:
            group_result = hw_group.group(df_path, group_result)

        return group_result


class HyperwaveGroupingToPhase4(HyperwaveGrouping):

    def group(self, df_path: pd.DataFrame, input_group: List[List[int]]) -> List[List[int]]:
        if len(input_group) < 4:
            return input_group

        output_group = input_group[:2]
        phase_3 = list(itertools.chain.from_iterable(input_group[2:]))
        output_group.append(phase_3)

        return output_group

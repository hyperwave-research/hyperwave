import itertools
from typing import List

import logging
import numpy as np
import pandas as pd
from scipy import constants


class HyperwaveGrouping(object):
    def group(
        self, df_path: pd.DataFrame, input_group: List[List[int]] = []
    ) -> List[List[int]]:
        pass


class HyperwaveWeekLenghtGrouping(HyperwaveGrouping):
    def __init__(self, group_min_weeks: int, only_group_last_phase: bool = True):
        self.group_min_weeks = group_min_weeks
        self.only_group_last_phase = only_group_last_phase

    def group(
        self, df_path: pd.DataFrame, input_group: List[List[int]]
    ) -> List[List[int]]:
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
        return df.loc[group].sum()["weeks"]


class HyperwaveGrouperSmallWeek(HyperwaveGrouping):
    def __init__(self, percent_bigger: int = 0.5):
        self._percent_bigger = percent_bigger

    def group(
        self, df_path: pd.DataFrame, input_group: List[List[int]] = []
    ) -> List[List[int]]:
        if len(input_group) < 4:
            return input_group

        hw_phase = input_group.copy()

        for i in np.arange(len(hw_phase), 1, -1):
            phase_previous = hw_phase[i - 3]
            phase_current = hw_phase[i - 2]
            phase_next = hw_phase[i - 1]

            week_previous = self._sum_group_weeks(df_path, phase_previous)
            week_current = self._sum_group_weeks(df_path, phase_current)
            week_next = self._sum_group_weeks(df_path, phase_next)

            week_current_grow = week_current * (1 + self._percent_bigger)

            if week_current_grow < week_previous and week_current_grow < week_next:
                if week_previous < week_next:
                    hw_phase.remove(phase_current)
                    hw_phase[i - 3].extend(phase_current)
                elif week_previous > week_next:
                    hw_phase.remove(phase_current)
                    hw_phase[i - 2].extend(phase_current)
                elif week_previous == week_next:
                    hw_phase.remove(phase_current)
                    hw_phase[i - 3].extend(phase_current)

        return hw_phase

    @staticmethod
    def _sum_group_weeks(df, group):
        return df.loc[group].sum()["weeks"]


class HyperwaveWeekLengthPhase1Grouping(HyperwaveGrouping):
    def __init__(self, phase_1_percent_length=0.236):
        self._phase_1_percent_length = phase_1_percent_length

    def group(
        self, df_path: pd.DataFrame, input_group: List[List[int]]
    ) -> List[List[int]]:
        hyperwave_total_weeks = df_path["weeks"].sum()
        phase1_min_nb_weeks = hyperwave_total_weeks * self._phase_1_percent_length

        logging.debug("Phase 1 min weeks : {}".format(int(phase1_min_nb_weeks)))

        week_grouping = HyperwaveWeekLenghtGrouping(phase1_min_nb_weeks, True)
        reversed_list = list(reversed(input_group))
        result_grouping = week_grouping.group(df_path, reversed_list)
        result_grouping = list(reversed(result_grouping))
        return result_grouping


class HyperwaveWeekLengthPhase4Grouping(HyperwaveGrouping):
    def __init__(self, phase_4_percent_lenght=0.0769):
        self._phase4_percent_lenght = phase_4_percent_lenght

    def group(
        self, df_path: pd.DataFrame, input_group: List[List[int]]
    ) -> List[List[int]]:
        phase4_min_nb_weeks = df_path["weeks"].sum() * self._phase4_percent_lenght
        logging.debug("Phase 4 min weeks : {}".format(int(phase4_min_nb_weeks)))
        week_grouping = HyperwaveWeekLenghtGrouping(phase4_min_nb_weeks, True)
        return week_grouping.group(df_path, input_group)


class HyperwavePhaseGrouper(HyperwaveGrouping):
    def __init__(self, phase_increase_factor: float = 2.0):
        self.phase_increase_factor = phase_increase_factor

    def group(
        self, df_path: pd.DataFrame, input_group: List[List[int]] = []
    ) -> List[List[int]]:
        df_positive_m = df_path[df_path["m_normalize"] >= 0]
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
        df_positive_m = df_path[df_path["m_normalize"] >= 0]
        if df_positive_m.shape[0] == 0:
            return []

        hw_phases_temp = []
        previous_m_normalize = df_positive_m.iloc[0].m_normalize
        hw_current_phase = [df_positive_m.index[0]]

        for index, row in df_positive_m.drop(df_positive_m.index[0]).iterrows():
            if row.m_normalize >= self.percent_increase * previous_m_normalize:
                hw_phases_temp.append(hw_current_phase)
                hw_current_phase = [index]
            else:
                hw_current_phase.append(index)
            previous_m_normalize = row.m_normalize

        hw_phases_temp.append(hw_current_phase)

        return hw_phases_temp


class HyperwaveGrouperByMedianSlopeIncrease(HyperwaveGrouping):
    def group(
        self, df_path: pd.DataFrame, input_group: List[List[int]] = []
    ) -> List[List[int]]:
        if df_path.empty:
            return []

        df_positive_m = df_path[df_path["m_normalize"] >= 0]
        if df_positive_m.shape[0] == 0:
            return []

        median = df_positive_m["m_normalize"].pct_change().dropna().median() + 1
        logging.debug("median value {}".format(median))
        return HyperwaveGroupingPhasePercent(median).group(df_path, input_group)


class HyperwaveGrouperByMeanSlopeIncrease(HyperwaveGrouping):
    def group(
        self, df_path: pd.DataFrame, input_group: List[List[int]] = []
    ) -> List[List[int]]:
        if df_path.empty:
            return []

        df_positive_m = df_path[df_path["m_normalize"] >= 0]
        if df_positive_m.shape[0] == 0:
            return []

        df_changes = df_positive_m["m_normalize"].pct_change().dropna()
        mean_raw_data = df_changes.mean()
        sd_raw_data = df_changes.std()
        up_value = mean_raw_data + sd_raw_data * 2
        low_value = mean_raw_data - sd_raw_data * 2

        df_changes = df_changes[(df_changes >= low_value)]
        df_changes = df_changes[(df_changes <= up_value)]

        std = df_changes.std()
        mean = df_changes.mean() + std

        mean += 0 if mean > 1.2 else 1
        mean = min(mean, 2)

        logging.debug("mean value {}".format(mean))
        return HyperwaveGroupingPhasePercent(mean).group(df_path, input_group)


class HyperwaveGrouperGoldenIncrease(HyperwaveGrouping):
    def group(
        self, df_path: pd.DataFrame, input_group: List[List[int]] = []
    ) -> List[List[int]]:
        if df_path.empty:
            return []

        increase = constants.golden
        return HyperwaveGroupingPhasePercent(increase).group(df_path, input_group)


class HyperwaveGroupingPhaseAggregator(HyperwaveGrouping):
    def __init__(self, hw_grouping: List[HyperwaveGrouping]):
        self.hw_grouping = hw_grouping

    def group(
        self, df_path: pd.DataFrame, input_group: List[List[int]] = []
    ) -> List[List[int]]:
        group_result = input_group.copy()

        for hw_group in self.hw_grouping:
            group_result = hw_group.group(df_path, group_result)

        return group_result


class HyperwaveGroupingToPhase4(HyperwaveGrouping):
    def group(
        self, df_path: pd.DataFrame, input_group: List[List[int]]
    ) -> List[List[int]]:
        if len(input_group) < 4:
            return input_group

        output_group = []
        output_group.append(input_group[0])
        phase_3_group = [y for x in input_group[1:-1] for y in x]

        output_group.append(phase_3_group)
        output_group.append(input_group[-1])

        return output_group

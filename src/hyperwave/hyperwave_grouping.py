from typing import List

import numpy as np
import pandas as pd


class HyperwaveGrouping( object ):
    def group( self, df_path:pd.DataFrame, input_group:List[List[int]] = [] ) -> List[List[int]]:
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

        if df_path.shape[0] == 0:
            return []
        df_positive_m = df_path[df_path['m_normalize'] >= 0]
        if df_positive_m.shape[0] == 0:
            return []

        # current_phase_m = df_positive_m.iloc[0].m_normalize
        hw_phases_temp = []
        sum_phase_increase = 0
        previous_m_normalize = df_positive_m.iloc[0].m_normalize
        hw_current_phase = [df_positive_m.index[0]]

        for index, row in df_positive_m.drop(df_positive_m.index[0]).iterrows():
            current_phase_grow = (row.m_normalize - previous_m_normalize) / previous_m_normalize
            sum_phase_increase += current_phase_grow
            previous_m_normalize = row.m_normalize

            if sum_phase_increase < self.percent_increase:
                hw_current_phase.append(index)
            else:
                hw_phases_temp.append(hw_current_phase)
                hw_current_phase = [index]
                sum_phase_increase = 0

        hw_phases_temp.append(hw_current_phase)

        return hw_phases_temp


class HyperwaveGroupingPhaseAggregator(HyperwaveGrouping):

    def __init__(self, hw_grouping: List[HyperwaveGrouping]):
        self.hw_grouping = hw_grouping

    def group(self, df_path: pd.DataFrame, input_group: List[List[int]] = []) -> List[List[int]]:
        group_result = input_group.copy()

        for hw_group in self.hw_grouping:
            group_result = hw_group.group(df_path, group_result)

        return group_result
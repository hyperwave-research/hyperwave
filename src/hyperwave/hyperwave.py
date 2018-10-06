import pandas as pd
import numpy as np
import logging
from typing import List
from .hyperwavepathfinder import HyperwavePathFinder


class HyperwaveWeekLenghtGrouping:
    def __init__(self, group_min_weeks: int, only_group_last_phase:bool = True):
        self.group_min_weeks = group_min_weeks
        self.only_group_last_phase = only_group_last_phase

    def Group(self, df_path: pd.DataFrame, input_group:List[List[int]]) -> List[List[int]]:
        hw_phase = input_group.copy()

        for i in np.arange(len(hw_phase ), 1, -1):
            phase = hw_phase [i-1]
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

class HyperwavePhaseGrouper():
    def __init__(self, phase_increase_factor: float = 2.0):
        self.phase_increase_factor = phase_increase_factor

    def get_hw_phases(self, df_path: pd.DataFrame) -> List[List[int]]:
        df_positive_m = df_path[df_path['m_normalize'] >= 0]
        if df_positive_m.shape[0] == 0:
            return []

        current_phase_m = df_positive_m.iloc[0].m_normalize
        hw_phases_temp = []
        hw_current_phase = [df_positive_m.index[0]]

        for index, row in df_positive_m.drop(df_positive_m.index[0]).iterrows():  # df_positive_m.loc[2:].iterrows():
            if row.m_normalize <= current_phase_m * self.phase_increase_factor:
                hw_current_phase.append(index)
            else:
                hw_phases_temp.append(hw_current_phase)
                hw_current_phase = [index]
                current_phase_m = row.m_normalize

        hw_phases_temp.append(hw_current_phase)

        return hw_phases_temp

class Hyperwave:
    def __init__(self,
                 min_m=0.5,
                 phase2_weeks_find_max=156,
                 phase_grow_factor=2,
                 phase4_min_weeks=15,
                 phase4_validation_previous_high=1.3,
                 hw_path_finder=HyperwavePathFinder()):
        self.phase2_weeks_find_max = phase2_weeks_find_max
        self.phase_grow_factor = phase_grow_factor
        self.min_m = min_m
        self.phase4_min_weeks = phase4_min_weeks
        self.phase4_validation_previous_high = phase4_validation_previous_high
        self.hw_path_finder = hw_path_finder

    def get_hyperwave(self, df):
        # Step 1 - Get the raw Hull from max and min raw data
        df_min_to_max = self._borne_raw_data_between_max_to_min(df)
        max_week_id = df_min_to_max.loc[df_min_to_max.loc[:, 'weekId'].idxmax(
        ), 'weekId']
        df_post_max = df.loc[max_week_id:]
        df_hull = self._order_and_reset_index(
            self._delete_above_path(self.hw_path_finder.get_hyperwave_path(df_min_to_max)))

        hw_phases_first_round = self._group_hyperwave_phase_1_to_4(df_hull, df)

        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            logging.debug("HW Phase search :")
            logging.debug(df_hull)
            logging.debug(hw_phases_first_round)

        # Step 2 - Find max Price prior of start hyperwave
        first_phase_id = min(len(hw_phases_first_round), 3) * -1
        phase_2 = hw_phases_first_round[first_phase_id]
        min_week = self._get_phase_start_week(df_hull, phase_2)
        max_price_weeks_before_start_week = self._get_max_price_week_before(
            df, min_week)

        hw_start_week_id = self._get_weekId_first_price_greater_than(df_min_to_max,
                                                                    min_week,
                                                                    max_price_weeks_before_start_week)

        # Step 3 - Get new Hull for the borned hyperwave raw data
        df_hyperwave_raw_data = df_min_to_max[(
                df_min_to_max.weekId >= hw_start_week_id)]

        df_hull_hyperwave = self._order_and_reset_index(
            self._delete_above_path(self.hw_path_finder.get_hyperwave_path(df_hyperwave_raw_data)))

        hw_phases_temp = self._group_hyperwave_phase_1_to_4(
            df_hull_hyperwave, df)

        max_nb_phases = min(len(hw_phases_temp), 3) * -1
        hw_phases_temp = hw_phases_temp[:max_nb_phases]
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            logging.debug(hw_phases_temp)
        # print(hw_phases_temp)
        hyperwave = {}
        phase_id = 1
        for phase in hw_phases_temp:
            phase_id = phase_id + 1
            df_phase = df_hull_hyperwave.loc[df_hull_hyperwave.loc[phase].loc[:, (
                                                                                     'ratio_error_cut')].idxmin()]
            hyperwave[phase_id] = df_phase[self._get_columns_not_normalize(
                df_phase)].to_dict()
        if len(hyperwave) >= 1:
            hyperwave[1] = self._get_phase1(
                hyperwave[2], max_price_weeks_before_start_week)

        for (phase_id, phase) in hyperwave.items():
            phase["is-broken"] = self._is_price_below_line(
                df_post_max, phase['m'], phase['b'])

        return df_hull_hyperwave, hw_phases_temp, hyperwave

    #     def df_result_row_to_dictionary(df_result):

    @staticmethod
    def _is_price_below_line(df, m, b):
        df['phase_line_week_price'] = df["weekId"] * m + b
        return df[df["close"] < df["phase_line_week_price"]].any()

    #     return df.any(axis='is_price_below')

    @staticmethod
    def _get_phase1(dic_phase2, price_break):
        dic_phase1 = dic_phase2.copy()
        dic_phase1['angle'] = 0
        dic_phase1['b'] = price_break
        dic_phase1['index'] = 0
        dic_phase1['m'] = 0
        dic_phase1['mean_error'] = 0
        dic_phase1['nb_is_lower'] = 0
        dic_phase1['ratio_error_cut'] = 0
        dic_phase1['weeks'] = 0
        return dic_phase1

    @staticmethod
    def _get_columns_not_normalize(df):
        return [c for c in df.axes[0] if "normalize" not in c]

    def _group_hyperwave_phase_1_to_4(self, df_result, df_raw):
        filtered_hw = df_result[(df_result.m_normalize > 0)]

        current_phase_m = filtered_hw.iloc[0].m_normalize
        hw_phases_temp = []
        hw_current_phase = [filtered_hw.index[0]]

        for index, row in filtered_hw.loc[2:].iterrows():
            if row.m_normalize < current_phase_m * self.phase_grow_factor:
                hw_current_phase.append(index)
            else:
                hw_phases_temp.append(hw_current_phase)
                hw_current_phase = [index]
                current_phase_m = row.m_normalize

        hw_phases_temp.append(hw_current_phase)

        #         if len(hw_phases_temp) == 3:
        #             return hw_phases_temp

        for i in np.arange(len(hw_phases_temp) - 1, 1, -1):
            phase = hw_phases_temp[i]
            current_phase_max = self._get_max_value_phase(
                phase, df_result, df_raw)
            previous_phase_max = self._get_max_value_phase(
                hw_phases_temp[i - 1], df_result, df_raw)

            if self._sum_group_weeks(filtered_hw, phase) < self.phase4_min_weeks:
                hw_phases_temp.remove(phase)
                hw_phases_temp[i - 1].extend(phase)
            # if self._sum_group_weeks(filtered_hw, phase) < self.phase4_min_weeks \
            #         or current_phase_max > previous_phase_max * self.phase4_validation_previous_high:
            #     hw_phases_temp.remove(phase)
            #     hw_phases_temp[i - 1].extend(phase)

        return hw_phases_temp

    @staticmethod
    def _get_max_phase_max(phase, df_result, df):
        df_phase = df_result.loc[phase]
        weekId_min = df_phase.loc[df_phase.loc[:, ('x1')].idxmin(), 'x1']
        weekId_max = df_phase.loc[df_phase.loc[:, ('x2')].idxmax(), 'x2']
        return Hyperwave._get_max_value_between(df, weekId_min, weekId_max)

    @staticmethod
    def _get_max_value_phase(phase, df_result, df):
        df_phase = df_result.loc[phase]
        weekId_min = df_phase.loc[df_phase.loc[:, ('x1')].idxmin(), 'x1']
        weekId_max = df_phase.loc[df_phase.loc[:, ('x2')].idxmax(), 'x2']
        return Hyperwave._get_max_value_between(df, weekId_min, weekId_max)

    @staticmethod
    def _get_max_value_between(df, weekId_min, weekId_max):
        df_phase = df.loc[weekId_min:weekId_max]
        return df_phase.loc[df_phase.loc[:, ('close')].idxmax(), 'close']

    @staticmethod
    def _order_and_reset_index(df):
        return df.sort_values(['x1', 'x2'], ascending=[True, False]) \
            .reset_index()



    @staticmethod
    def _get_weekId_first_price_greater_than(df, min_week_id, max_price):
        df_week_greater_than = df[(df.weekId >= min_week_id)]

        df_val_price_greater_than_max = df_week_greater_than[(
                df_week_greater_than.close > max_price)]
        return df_val_price_greater_than_max.loc[df_val_price_greater_than_max.loc[:, ('weekId')].idxmin()]['weekId']

    @staticmethod
    def _get_phase_start_week(df_result, phase_lines):
        return min(df_result.iloc[phase_lines]['x1'])

    @staticmethod
    def _delete_above_path(df):
        # As we are using Hull to find the external phase of the graph. The positive mean_error as the way up
        # whereas the negative are the way down
        return df[(df.mean_error >= 0)]

    @staticmethod
    def _delete_below_path(df):
        # As we are using Hull to find the external phase of the graph. The positive mean_error as the way up
        # whereas the negative are the way down
        return df[(df.mean_error < 0)]

    @staticmethod
    def _borne_raw_data_between_max_to_min( df):
        #     Born the dataframe from with all the value before weekId of Max and from them find the min to born the other side
        max_price_weekId = Hyperwave._get_week_id_max_price(df)
        df_until_max = df.loc[:max_price_weekId]
        min_price_weekId = Hyperwave._get_week_id_max_price(df_until_max)
        df_min_to_max = df_until_max.loc[min_price_weekId:]
        return df_min_to_max

    @staticmethod
    def _get_week_id_max_price(df):
        return df.loc[df.loc[:, ('close')].idxmax(), 'weekId']

    @staticmethod
    def _get_week_id_min_price(df):
        return df.loc[df.loc[:, ('close')].idxmin(), 'weekId']

    @staticmethod
    def _get_max_price( df, column_name='close'):
        return df.loc[df.loc[:, (column_name)].idxmax()][column_name]

    @staticmethod
    def _get_max_price_week_before(self, df, weekId):
        last_n_weeks_Items = df[(df.weekId <= weekId)].tail(
            self.phase2_weeks_find_max)
        max_price = self._get_max_price(last_n_weeks_Items)
        return max_price

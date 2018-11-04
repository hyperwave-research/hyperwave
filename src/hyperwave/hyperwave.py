import pandas as pd
import logging
from typing import List

from hyperwave import HyperwaveWeekLenghtGrouping, HyperwavePhaseGrouper
from .hyperwave_grouping import *
from .hyperwavepathfinder import HyperwavePathFinder


class Hyperwave:

    @classmethod
    def get_standard_hyperwave(cls, phase2_weeks_max: int = 156):
        hw_grouping_lookup_phase1 = [
            # HyperwaveGrouperGoldenIncrease(),
            HyperwaveGrouperByMeanSlopeIncrease(),
            HyperwaveGrouperSmallWeek(0.07),
            # HyperwaveWeekLenghtGrouping(group_min_weeks=15),
            HyperwaveWeekLengthPhase4Grouping(0.07),
        ]
        hw_grouping_lookup_phase2 = [
            HyperwaveGrouperGoldenIncrease(),
            HyperwaveGrouperSmallWeek(0.07),
            HyperwaveWeekLengthPhase1Grouping(),
            HyperwaveWeekLengthPhase4Grouping(),
            HyperwaveGroupingToPhase4()
        ]

        return cls(hw_grouping_lookup_phase1, hw_grouping_lookup_phase2, phase2_weeks_find_max=phase2_weeks_max)

    def __init__(self,
                 # min_m=0.5,
                 hw_grouping_lookup_phase1: List[HyperwaveGrouping],
                 hw_grouping_lookup_phase2: List[HyperwaveGrouping],
                 phase2_weeks_find_max=156,
                 # phase_grow_factor=2,
                 # phase4_min_weeks=15,
                 hw_path_finder=HyperwavePathFinder(),

                 # hw_phase_grouper: HyperwavePhaseGrouper = None,
                 # hw_week_lenght_grouping: HyperwaveWeekLenghtGrouping = None
                 # # phase4_validation_previous_high=1.3
                 ):
        # self.hw_phase_grouper = HyperwavePhaseGrouper(phase_grow_factor) \
        #     if hw_phase_grouper is None \
        #     else hw_phase_grouper
        # self.hw_week_lenght_grouping = HyperwaveWeekLenghtGrouping(phase4_min_weeks, True) \
        #     if hw_week_lenght_grouping is None \
        #     else hw_week_lenght_grouping
        self.hw_path_finder = hw_path_finder
        self.phase2_weeks_find_max = phase2_weeks_find_max
        self.hw_grouping_lookup_phase1 = hw_grouping_lookup_phase1
        self.hw_grouping_lookup_phase2 = hw_grouping_lookup_phase2

        self._min_m_normalize = 0.03818
        # self.phase_grow_factor = phase_grow_factor
        # self.min_m = min_m
        # self.phase4_min_weeks = phase4_min_weeks
        # self.phase4_validation_previous_high = phase4_validation_previous_high
        # self.hw_path_finder = hw_path_finder

    def get_hyperwave(self, df_source):
        # Step 1 - Get the raw Hull from max and min raw data
        df_min_to_max = self._borne_raw_data_between_max_to_min(df_source)
        max_week_id = df_min_to_max.loc[df_min_to_max.loc[:, 'weekId'].idxmax(
        ), 'weekId']
        df_post_max = df_source.loc[max_week_id:]
        # df_hull = self._order_and_reset_index(
        #     self._delete_above_path(self.hw_path_finder.get_hyperwave_path(df_min_to_max)))
        #
        # hw_phases_first_round = Hyperwave._group_hyperwave_phase(df_hull, self.hw_grouping_lookup_phase1)
        #
        # logging.debug("HW Phase search :")
        # logging.debug(df_hull)
        # logging.debug(hw_phases_first_round)
        #
        # # Step 2 - Find max Price prior of start hyperwave
        # first_phase_id = min(len(hw_phases_first_round), 3) * -1
        # phase_2 = hw_phases_first_round[first_phase_id]
        # min_week = self._get_phase_start_week(df_hull, phase_2)
        min_week = df_min_to_max.loc[df_min_to_max.loc[:, 'weekId'].idxmin(
        ), 'weekId']
        # Step 3 - Get new Hull for the borned hyperwave raw data
        while True:
            max_price_weeks_before_start_week = self._get_max_price_week_before(df_source, min_week,
                                                                                self.phase2_weeks_find_max)

            hw_start_week_id = self._get_weekId_first_price_greater_than(df_min_to_max,
                                                                         min_week,
                                                                         max_price_weeks_before_start_week)

            df_hyperwave_raw_data = df_min_to_max.loc[hw_start_week_id:]

            df_hull_hyperwave = self._order_and_reset_index(
                self._delete_above_path(self.hw_path_finder.get_hyperwave_path(df_hyperwave_raw_data)))

            min_week = df_hull_hyperwave[(df_hull_hyperwave.m_normalize > 0)].iloc[0]["x1"]
            logging.debug(
                '******************* m_normalize too smaller that {} ****************** '.format(self._min_m_normalize))
            logging.debug('\n{}'.format(df_hull_hyperwave))
            logging.debug('Min WeekId : {}'.format(min_week))

            if df_hull_hyperwave.loc[0]["m_normalize"] <= 0.0:
                continue

            min_week = df_hull_hyperwave[(df_hull_hyperwave.nb_is_lower > 0)].iloc[0]["x1"]
            if df_hull_hyperwave.loc[0]["nb_is_lower"] == 0:
                continue

            min_week = df_hull_hyperwave[(df_hull_hyperwave.m_normalize > 0)].iloc[0]["x2"]
            if df_hull_hyperwave.loc[0]["m_normalize"] >= self._min_m_normalize :
                break

            logging.debug(
                '******************* m_normalize too smaller that {} ****************** '.format(self._min_m_normalize))
            logging.debug('\n{}'.format(df_hull_hyperwave))
            logging.debug('Min WeekId : {}'.format(min_week))

        hw_phases_temp = Hyperwave._group_hyperwave_phase(df_hull_hyperwave, self.hw_grouping_lookup_phase2)
        max_nb_phases = min(len(hw_phases_temp), 3) * -1
        hw_phases_temp = hw_phases_temp[max_nb_phases:]

        logging.debug(hw_phases_temp)

        hyperwave = []
        phase_id = 1
        for phase in hw_phases_temp:
            phase_id = phase_id + 1
            df_phase = df_hull_hyperwave.loc[df_hull_hyperwave.loc[phase].loc[:, (
                                                                                     'ratio_error_cut')].idxmin()]
            hyperwave_phase = df_phase[self._get_columns_not_normalize(
                df_phase)].to_dict()
            hyperwave_phase['phase_id'] = phase_id
            hyperwave.append(hyperwave_phase)

        if len(hyperwave) >= 1:
            phase_2_start = self.get_phase_2_start(df_hull_hyperwave, hw_phases_temp[0]).to_dict()
            hyperwave_phase1 = self._get_phase1(phase_2_start, max_price_weeks_before_start_week)
            hyperwave.append(hyperwave_phase1)

        for phase in hyperwave:
            phase["is-broken"] = self._is_price_below_line(
                df_post_max, phase['m'], phase['b'])

        df_hyperwave_phases = pd.DataFrame(hyperwave)
        df_hyperwave_phases = df_hyperwave_phases.drop(['index'], axis=1)
        df_hyperwave_phases = self._order_and_reset_index(df_hyperwave_phases)
        df_hyperwave_phases = df_hyperwave_phases.drop(['index'], axis=1)
        return df_hull_hyperwave, hw_phases_temp, df_hyperwave_phases

    @staticmethod
    def get_phase(phases, phase_id):
        for phase in phases:
            if phase['phase_id'] == phase_id:
                return phase
        return {}

    @staticmethod
    def get_phase_2_start(df_hull: pd.DataFrame, phase_index: List[int]):
        df_phase = df_hull.iloc[phase_index]
        return df_phase.loc[df_phase.loc[:, ('x1')].idxmin()]

    @staticmethod
    def _is_price_below_line(df, m, b):
        df['phase_line_week_price'] = df["weekId"] * m + b
        df['is_price_below'] = df.loc[:, 'close'] <= df.loc[:, "phase_line_week_price"]
        return df.any()['is_price_below']

    #     return df.any(axis='is_price_below')

    @staticmethod
    def _get_phase_start_week_id(df_hull: pd.DataFrame, phase_index: List[int]):
        df_phase = df_hull.iloc[phase_index]
        return df_phase.loc[df_phase.loc[:, ('x1')].idxmin(), 'x1']

    @staticmethod
    def _get_phase1(dic_phase2, price_break):
        dic_phase1 = dic_phase2.copy()
        dic_phase1['y2'] = dic_phase1['y1']
        dic_phase1['angle'] = 0
        dic_phase1['b'] = price_break
        # dic_phase1['index'] = 0
        dic_phase1['m'] = 0
        dic_phase1['mean_error'] = 0
        dic_phase1['nb_is_lower'] = 0
        dic_phase1['ratio_error_cut'] = 0
        dic_phase1['weeks'] = 0
        dic_phase1['phase_id'] = 1
        return dic_phase1

    @staticmethod
    def _get_columns_not_normalize(df):
        return [c for c in df.axes[0] if "index" != c]

    @staticmethod
    def _group_hyperwave_phase(df_phase_result, grouping: List[HyperwaveGrouping]):
        phase_grouping = []
        for grp in grouping:
            logging.debug("========== Use grouper {} =================".format(grp))
            logging.debug("Before Grouping : {}".format(phase_grouping))
            phase_grouping = grp.group(df_phase_result, phase_grouping)
            logging.debug("After Grouping : {}".format(phase_grouping))

        return phase_grouping

    # def _group_hyperwave_phase_1_to_4(self, df_result, df_raw):
    #     filtered_hw = df_result[(df_result.m_normalize > 0)]
    #
    #     current_phase_m = filtered_hw.iloc[0].m_normalize
    #     hw_phases_temp = []
    #     hw_current_phase = [filtered_hw.index[0]]
    #
    #     for index, row in filtered_hw.loc[2:].iterrows():
    #         if row.m_normalize < current_phase_m * self.phase_grow_factor:
    #             hw_current_phase.append(index)
    #         else:
    #             hw_phases_temp.append(hw_current_phase)
    #             hw_current_phase = [index]
    #             current_phase_m = row.m_normalize
    #
    #     hw_phases_temp.append(hw_current_phase)
    #
    #     #         if len(hw_phases_temp) == 3:
    #     #             return hw_phases_temp
    #
    #     for i in np.arange(len(hw_phases_temp) - 1, 1, -1):
    #         phase = hw_phases_temp[i]
    #         current_phase_max = self._get_max_value_phase(
    #             phase, df_result, df_raw)
    #         previous_phase_max = self._get_max_value_phase(
    #             hw_phases_temp[i - 1], df_result, df_raw)
    #
    #         if self._sum_group_weeks(filtered_hw, phase) < self.phase4_min_weeks:
    #             hw_phases_temp.remove(phase)
    #             hw_phases_temp[i - 1].extend(phase)
    #         # if self._sum_group_weeks(filtered_hw, phase) < self.phase4_min_weeks \
    #         #         or current_phase_max > previous_phase_max * self.phase4_validation_previous_high:
    #         #     hw_phases_temp.remove(phase)
    #         #     hw_phases_temp[i - 1].extend(phase)
    #
    #     return hw_phases_temp

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

        df_weekid_above_max_price =  df_val_price_greater_than_max.loc[df_val_price_greater_than_max.loc[:, ('weekId')].idxmin()]

        return df_weekid_above_max_price['weekId'] if (df_weekid_above_max_price['close'] - max_price) / max_price < 0.1 else df_weekid_above_max_price['weekId'] - 1


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
    def _borne_raw_data_between_max_to_min(df):
        #     Born the dataframe from with all the value before weekId of Max and from them find the min to born the other side
        max_price_weekId = Hyperwave._get_week_id_max_price(df)
        df_until_max = df.loc[:max_price_weekId]
        min_price_weekId = Hyperwave._get_week_id_min_price(df_until_max)
        df_min_to_max = df_until_max.loc[min_price_weekId:]
        return df_min_to_max

    @staticmethod
    def _get_week_id_max_price(df):
        return df.loc[df.loc[:, ('close')].idxmax(), 'weekId']

    @staticmethod
    def _get_week_id_min_price(df):
        return df.loc[df.loc[:, ('close')].idxmin(), 'weekId']

    @staticmethod
    def _get_max_price(df, column_name='close'):
        return df.loc[df.loc[:, (column_name)].idxmax()][column_name]

    @staticmethod
    def _get_max_price_week_before(df, weekId, phase2_weeks_find_max):
        last_n_weeks_Items = df[(df.weekId <= weekId)].tail(phase2_weeks_find_max)
        max_price = Hyperwave._get_max_price(last_n_weeks_Items)
        return max_price

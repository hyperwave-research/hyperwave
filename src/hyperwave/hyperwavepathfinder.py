import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull


class HyperwavePathFinder:

    @staticmethod
    def get_hyperwave_path(df_input: pd.DataFrame):
        # Extract the hyperwave path using the ConvexHull.
        # The df_input need to contain at least the following columns
        #   - close
        #   - date
        #   - high
        #   - is_price_closing_up
        #   - low
        #   - open
        #   - weekId

        # Add the column with normalized value
        df_input.loc[:, 'close_normalize'] = HyperwavePathFinder.get_column_normalize_values(
            df_input, 'close')
        df_input.loc[:, 'weekId_normalize'] = HyperwavePathFinder.get_column_normalize_values(
            df_input, 'weekId')

        # Use convexHull to find the support lines
        hull = ConvexHull(
            df_input[['weekId_normalize', 'close_normalize']].dropna())

        hull_results = [[min(pair[0], pair[1]), max(pair[0], pair[1])]
                        for pair in hull.simplices]
        data_from_to = [{"x1": df_input['weekId'].iloc[pair[0]],
                         "x1_date": df_input['date'].iloc[pair[0]],
                         "x1_normalize": df_input['weekId_normalize'].iloc[pair[0]],
                         "y1": df_input['close'].iloc[pair[0]],
                         "y1_normalize": df_input['close_normalize'].iloc[pair[0]],
                         "x2": df_input['weekId'].iloc[pair[1]],
                         "x2_date": df_input['date'].iloc[pair[1]],
                         "x2_normalize": df_input['weekId_normalize'].iloc[pair[1]],
                         "y2": df_input['close'].iloc[pair[1]],
                         "y2_normalize": df_input['close_normalize'].iloc[pair[1]]} for pair in hull_results]

        df = pd.DataFrame(data_from_to)
        df['m'] = HyperwavePathFinder.get_line_slope(df,
                                                     x1_col_name='x1',
                                                     y1_col_name='y1',
                                                     x2_col_name='x2',
                                                     y2_col_name='y2')
        df['b'] = HyperwavePathFinder.get_line_origine(df,
                                                       x1_col_name='x1',
                                                       y1_col_name='y1',
                                                       m_col_name='m')
        df['m_normalize'] = HyperwavePathFinder.get_line_slope(df,
                                                               x1_col_name='x1_normalize',
                                                               y1_col_name='y1_normalize',
                                                               x2_col_name='x2_normalize',
                                                               y2_col_name='y2_normalize')
        df['b_normalize'] = HyperwavePathFinder.get_line_origine(df,
                                                                 x1_col_name='x1_normalize',
                                                                 y1_col_name='y1_normalize',
                                                                 m_col_name='m_normalize')
        df['angle'] = np.rad2deg(np.arctan2(df['m'], 1))
        df['angle_normalize'] = np.rad2deg(
            np.arctan2(df['m_normalize'], 1))
        df['weeks'] = np.abs(df['x1'] - df['x2'])
        df['mean_error'] = df.apply(
            lambda row: HyperwavePathFinder.calculate_mean_error(row, df_input), axis=1)
        df['nb_is_lower'] = df.apply(
            lambda row: HyperwavePathFinder.nb_cut_price_low(row, df_input), axis=1)
        df['ratio_error_cut'] = df['mean_error'] / (df['nb_is_lower'] * df['weeks'])
        df['ratio_slope_y1_normalize'] = df['y1_normalize'] / df['m_normalize']
        df['ratio_slope_y2_normalize'] = df['y2_normalize'] / df['m_normalize']
        return df

    @staticmethod
    def get_line_slope(df, x1_col_name='x1', y1_col_name='y1', x2_col_name='x2', y2_col_name='y2'):
        return (df[y1_col_name] - df[y2_col_name]) / (df[x1_col_name] - df[x2_col_name])

    @staticmethod
    def get_line_origine(df, x1_col_name='x1', y1_col_name='y1', m_col_name='m'):
        return df[y1_col_name] - (df[x1_col_name] * df[m_col_name])

    @staticmethod
    def get_column_normalize_values(df, column_name='close'):
        max_value = df.loc[df[column_name].idxmax()][column_name]
        min_value = df.loc[df[column_name].idxmin()][column_name]

        return (df[column_name] - min_value) / (max_value - min_value)

    @staticmethod
    def get_mean_error(y_true, y_pred):
        y_square_diff = y_true - y_pred
        return np.sum(y_square_diff) / len(y_true)

    @staticmethod
    def nb_is_lower(y_true, y_pred):
        lower_item = y_true[y_true <= y_pred]
        return len(lower_item)

    @staticmethod
    def get_y(x, m, b):
        return x * m + b

    @staticmethod
    def calculate_mean_error(row, df):
        y_pred = HyperwavePathFinder.get_y(df['weekId'], row['m'], row['b'])
        return HyperwavePathFinder.get_mean_error(df['close'], y_pred)

    @staticmethod
    def nb_cut_price_low(row, df):
        y_pred = HyperwavePathFinder.get_y(df['weekId'], row['m'], row['b'])
        return HyperwavePathFinder.nb_is_lower(df['low'], y_pred)

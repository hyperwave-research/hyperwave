import pandas as pd


def get_rolling_mean(df: pd.DataFrame, column_name: str, window: int):
    return df[column_name].rolling(window=window).mean()


def get_move_value(df: pd.DataFrame, column_name: str, down: int, up: int, equal: int):
    df2 = pd.DataFrame(index=df.index)
    mask_up = df[column_name] > df[column_name].shift()
    mask_down = df[column_name] < df[column_name].shift()
    mask_equal = df[column_name] == df[column_name].shift()
    df2.loc[mask_up, "close_up"] = up
    df2.loc[mask_equal, "close_up"] = equal
    df2.loc[mask_down, "close_up"] = down
    return df2["close_up"]


def get_value_between_two_col(
    df, colunm_name_high: str, column_name_low: str, value_up: int, value_down: int
):
    df2 = pd.DataFrame(index=df.index)
    mask_up = df[colunm_name_high] >= df[column_name_low]
    mask_down = df[colunm_name_high] < df[column_name_low]

    df2.loc[mask_up, "new_value"] = value_up
    df2.loc[mask_down, "new_value"] = value_down
    return df2["new_value"]


def get_consonsio(
    df_source: pd.DataFrame,
    column_name: str = "close",
    low_ma: int = 3,
    mid_ma: int = 7,
    high_ma=30,
):
    df = df_source.copy()
    df["low_MA"] = get_rolling_mean(df, column_name, low_ma)
    df["mid_MA"] = get_rolling_mean(df, column_name, mid_ma)
    df["high_MA"] = get_rolling_mean(df, column_name, high_ma)

    df["move_price"] = get_move_value(df, column_name, 0, 1, 0.5)
    df["price_above_low_MA"] = get_value_between_two_col(
        df, column_name, "low_MA", 2, 0
    )
    df["price_above_mid_MA"] = get_value_between_two_col(
        df, column_name, "mid_MA", 4, 0
    )
    df["price_above_high_MA"] = get_value_between_two_col(
        df, column_name, "high_MA", 8, 0
    )

    df["move_low_MA"] = get_move_value(df, "low_MA", 0, 16, 8)
    df["low_MA_above_mid_MA"] = get_value_between_two_col(df, "low_MA", "mid_MA", 32, 0)
    df["low_MA_above_high_MA"] = get_value_between_two_col(
        df, "low_MA", "high_MA", 64, 0
    )

    df["move_mid_MA"] = get_move_value(df, "mid_MA", 0, 128, 64)
    df["mid_MA_above_high_MA"] = get_value_between_two_col(
        df, "mid_MA", "high_MA", 256, 0
    )

    df["move_high_MA"] = get_move_value(df, "high_MA", 0, 512, 256)

    df["consensio"] = (
        df["move_price"]
        + df["price_above_low_MA"]
        + df["price_above_mid_MA"]
        + df["price_above_high_MA"]
        + df["move_low_MA"]
        + df["low_MA_above_mid_MA"]
        + df["low_MA_above_high_MA"]
        + df["move_mid_MA"]
        + df["mid_MA_above_high_MA"]
        + df["move_high_MA"]
    )
    return df

import pandas as pd
import numpy as np
from typing import List, Optional


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['Year'] = df['BidDate'].dt.year
    df['Month'] = df['BidDate'].dt.month
    df['DayOfWeek'] = df['BidDate'].dt.dayofweek
    df['Quarter'] = df['BidDate'].dt.quarter
    return df


def add_rolling_group_features(df: pd.DataFrame, group_cols: List[str], target_col: str, windows: List[int]) -> pd.DataFrame:
    df = df.copy()
    df = df.sort_values('BidDate')
    for g in group_cols:
        for w in windows:
            col_name_mean = f'{g}_rolling_{w}d_mean_{target_col}'
            col_name_win = f'{g}_rolling_{w}d_winrate'
            # Calculate rolling mean per group by reindexing with date
            df[col_name_mean] = df.groupby(g)[target_col].rolling(window=w, min_periods=1).mean().reset_index(level=0, drop=True)
            if 'WinStatus' in df.columns:
                df[col_name_win] = df.groupby(g)['WinStatus'].rolling(window=w, min_periods=1).mean().reset_index(level=0, drop=True)
    return df


def add_lag_features(df: pd.DataFrame, group_cols: List[str], cols_to_lag: List[str], lags: List[int]) -> pd.DataFrame:
    df = df.copy()
    for g in group_cols:
        for lag in lags:
            for c in cols_to_lag:
                name = f'{g}_lag_{lag}_{c}'
                df[name] = df.groupby(g)[c].shift(lag)
    return df


def merge_fred(df: pd.DataFrame, fred_df: Optional[pd.DataFrame], date_col: str = 'BidDate') -> pd.DataFrame:
    if fred_df is None or fred_df.empty:
        return df
    fred_df = fred_df.copy()
    fred_df.index = pd.to_datetime(fred_df.index)
    fred_df = fred_df.reset_index().rename(columns={'index': date_col})
    fred_df[date_col] = pd.to_datetime(fred_df[date_col])
    # Merge on nearest previous date (as economic indicators are lower frequency)
    df = pd.merge_asof(df.sort_values(date_col), fred_df.sort_values(date_col), on=date_col, direction='backward')
    return df

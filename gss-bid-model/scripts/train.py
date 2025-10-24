"""Train both win-probability and bid-amount models and save artifacts.

Usage:
    python scripts/train.py --data-path data/sample_bid_data.csv --output models/
"""
import argparse
from pathlib import Path
import pandas as pd
from src.data_loader import load_csv
from src.feature_engineering import add_time_features, add_rolling_group_features, add_lag_features, merge_fred
from src.fred_client import load_cached_fred, fetch_fred_series, save_fred
from src.models import train_models


def prepare_features(df: pd.DataFrame, fred_df=None):
    df = add_time_features(df)
    group_cols = ['ClientType', 'Location']
    group_cols = [c for c in group_cols if c in df.columns]
    df = add_rolling_group_features(df, group_cols=group_cols, target_col='BidAmount', windows=[7,30,90])
    df = add_lag_features(df, group_cols=group_cols, cols_to_lag=['BidAmount', 'WinStatus'], lags=[1,2])
    df = merge_fred(df, fred_df)
    return df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data-path', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--fred-series', nargs='*', default=['UNRATE'])
    args = parser.parse_args()

    df = load_csv(args.data_path)

    # Try to load cached fred or fetch
    fred_cache = Path('data/fred_cached.csv')
    fred_df = None
    if fred_cache.exists():
        fred_df = load_cached_fred(str(fred_cache))
    else:
        # attempt to fetch first series as example
        try:
            fred_df = fetch_fred_series(args.fred_series[0])
            if not fred_df.empty:
                save_fred(fred_df, str(fred_cache))
        except Exception:
            fred_df = None

    df_feat = prepare_features(df, fred_df)

    # Select feature columns: keep categorical and numeric
    categorical_cols = [c for c in ['ProjectType', 'Location', 'ClientType'] if c in df_feat.columns]
    numeric_cols = [c for c in df_feat.columns if c not in categorical_cols + ['BidDate', 'WinStatus'] and df_feat[c].dtype.name != 'object']

    # Target variables
    y_reg = df_feat['BidAmount']
    y_clf = df_feat['WinStatus']

    # Drop columns that are not features
    X = df_feat.drop(columns=['BidDate', 'BidAmount', 'WinStatus'], errors='ignore')

    artifacts = train_models(X, y_reg, y_clf, categorical_cols, numeric_cols, args.output)
    print('Training complete. Artifacts:', artifacts)


if __name__ == '__main__':
    main()

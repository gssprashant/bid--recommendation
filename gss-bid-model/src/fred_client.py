import os
import pandas as pd
from pathlib import Path


def fetch_fred_series(series_id: str, api_key: str = None, start: str = None, end: str = None) -> pd.DataFrame:
    """Fetch a single FRED series using fredapi if available. Returns a DataFrame indexed by date.

    If no API key or fredapi package available, returns empty DataFrame.
    """
    try:
        if api_key is None:
            api_key = os.getenv('FRED_API_KEY')
        if api_key is None:
            print('FRED API key not set; skipping FRED fetch')
            return pd.DataFrame()

        from fredapi import Fred
        fred = Fred(api_key=api_key)
        series = fred.get_series(series_id, observation_start=start, observation_end=end)
        df = pd.DataFrame(series)
        df.columns = [series_id]
        return df
    except Exception as e:
        print(f'Warning: unable to fetch FRED series {series_id}: {e}')
        return pd.DataFrame()


def load_cached_fred(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p, index_col=0, parse_dates=True)


def save_fred(df: pd.DataFrame, path: str):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p)

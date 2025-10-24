import pandas as pd
from pathlib import Path


def load_csv(path: str) -> pd.DataFrame:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Data file not found: {path}")
    df = pd.read_csv(p)
    # Basic checks
    if 'BidDate' in df.columns:
        df['BidDate'] = pd.to_datetime(df['BidDate'])
        df = df.sort_values('BidDate').reset_index(drop=True)
    return df


def save_sample_data(path: str, n=500):
    """Create a small sample dataset for testing/demonstration."""
    import numpy as np
    import pandas as pd
    start = pd.Timestamp('2023-01-01')
    dates = pd.date_range(start=start, periods=n, freq='D')
    project_types = ['Commercial', 'Residential', 'Industrial']
    locations = ['NY', 'LA', 'CHI']
    client_types = ['Government', 'Private']

    df = pd.DataFrame({
        'BidDate': dates,
        'ProjectType': np.random.choice(project_types, size=n),
        'Location': np.random.choice(locations, size=n),
        'ClientType': np.random.choice(client_types, size=n),
        'BidAmount': np.random.lognormal(mean=12, sigma=0.6, size=n),
        'EstimatedCost': np.random.lognormal(mean=12.2, sigma=0.6, size=n),
        'CompetitorCount': np.random.randint(1, 6, size=n)
    })

    # Simulate win status with some simple rule
    prob = 1 / (1 + np.exp(-(-0.2 + 0.3*(df['BidAmount'] < df['EstimatedCost']).astype(int) - 0.1*df['CompetitorCount'])))
    df['WinStatus'] = (np.random.rand(n) < prob).astype(int)
    df.to_csv(path, index=False)
    return df

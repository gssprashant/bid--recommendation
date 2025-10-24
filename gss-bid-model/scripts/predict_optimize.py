"""Given a new opportunity, search over candidate bid amounts and pick the fee that
maximizes expected profit = P(win | features, bid) * bid.

Usage:
    python scripts/predict_optimize.py --model-dir models/ --input-json examples/sample_input.json
"""
import argparse
import json
import numpy as np
import pandas as pd
from pathlib import Path
import joblib


def load_input(path: str) -> pd.DataFrame:
    p = Path(path)
    d = json.loads(p.read_text()) if p.exists() else path
    if isinstance(d, dict):
        return pd.DataFrame([d])
    elif isinstance(d, list):
        return pd.DataFrame(d)
    else:
        raise ValueError('Unsupported input JSON format')


def optimize_bid(model_dir: str, input_df: pd.DataFrame, pct_range=0.2, n_steps=41):
    p = Path(model_dir)
    clf = joblib.load(p / 'win_model.joblib')
    reg = joblib.load(p / 'bid_model.joblib')

    baseline = float(input_df.get('BidAmount', pd.Series([0])).iloc[0])
    if baseline <= 0:
        # choose an approximate baseline from EstimatedCost if present
        baseline = float(input_df.get('EstimatedCost', pd.Series([100000.0])).iloc[0])

    candidates = np.linspace(baseline*(1-pct_range), baseline*(1+pct_range), n_steps)

    results = []
    for c in candidates:
        Xc = input_df.copy()
        Xc['BidAmount'] = c
        # Align feature order is handled by pipeline inside models
        p_win = clf.predict_proba(Xc)[:, 1] if hasattr(clf, 'predict_proba') else clf.predict(Xc)
        # If classifier returns scalar, ensure shape
        p_win = np.asarray(p_win).ravel()
        # For regression we may want predicted expected fee but we already choose c as fee
        expected_profit = p_win * c
        results.append({'candidate': c, 'p_win': float(p_win[0]), 'expected_profit': float(expected_profit[0])})

    df_res = pd.DataFrame(results)
    best = df_res.loc[df_res['expected_profit'].idxmax()]
    return df_res, best


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-dir', required=True)
    parser.add_argument('--input-json', required=True)
    args = parser.parse_args()

    input_df = load_input(args.input_json)
    df_res, best = optimize_bid(args.model_dir, input_df)
    print('Best candidate:')
    print(best.to_dict())
    out = Path(args.model_dir) / 'last_opt_result.json'
    out.write_text(df_res.to_json(orient='records', indent=2))
    print('All results saved to', out)


if __name__ == '__main__':
    main()

"""
Bid Recommendation Inference Script
Usage:
    python bid_inference.py --input opportunity.json
    
Example opportunity.json:
{
    "ZipCode": "12345",
    "PropertyType": "Residential",
    "BidCompanyName": "ABC Corp",
    "Market": "Urban",
    "BidCompanyType": "Large"
}
"""
import os
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.isotonic import IsotonicRegression

def transform_row_for_model(row, features, encoders, train_medians, set_fee=None):
    """Transform a single opportunity row into model-ready features."""
    r = row.copy()
    if set_fee is not None:
        if 'median_BidFee' in r.index: r['median_BidFee'] = set_fee
        if 'lag_1' in r.index: r['lag_1'] = set_fee
    df_row = pd.DataFrame([r])[features].copy()
    for col,m in encoders.items():
        if col in df_row.columns:
            val = str(df_row.at[0,col]) if pd.notna(df_row.at[0,col]) else 'MISSING'
            df_row.at[0,col] = m.get(val,0.0)
    for c in df_row.columns:
        df_row[c] = pd.to_numeric(df_row[c], errors='coerce')
    df_row = df_row.fillna(train_medians)
    return df_row

def find_optimal_fee(sample_row, features, encoders, train_medians, model_full, clf=None, 
                    base_multiplier=0.2, steps=60):
    """Find fee that maximizes expected value."""
    cur_fee = float(sample_row.get('median_BidFee', np.nan) if pd.notna(sample_row.get('median_BidFee', np.nan)) 
                   else train_medians.get('lag_1', 0.0))
    if np.isnan(cur_fee) or cur_fee<=0: 
        cur_fee = float(train_medians.get('median_BidFee', 1.0))
    
    low,high = cur_fee*(1-base_multiplier), cur_fee*(1+base_multiplier)
    grid = np.linspace(low,high,steps)
    win_probs=[]; evs=[]
    
    for f in grid:
        xrow = transform_row_for_model(sample_row, features, encoders, train_medians, set_fee=f)
        if clf is not None:
            try:
                p = float(clf.predict_proba(xrow)[:,1][0])
            except Exception:
                p = 0.1  # fallback probability
        else:
            p = 0.1  # fallback if no classifier
            
        p = max(0.0, min(1.0, p))  # clip to [0,1]
        win_probs.append(p)
        evs.append(p*f)
    
    win_probs = np.array(win_probs)
    evs = np.array(evs)
    idx = int(np.nanargmax(evs))
    
    return {
        'fee_grid': grid,
        'win_probs': win_probs,
        'evs': evs,
        'best_fee': float(grid[idx]),
        'best_ev': float(evs[idx]),
        'best_prob': float(win_probs[idx])
    }

def recommend_bid_fee(opportunity_row, artifacts_path='models/bid_recommendation_artifacts.joblib'):
    """Production inference function that accepts a new opportunity and returns recommendations."""
    # Load artifacts
    if not os.path.exists(artifacts_path):
        raise FileNotFoundError(f"Model artifacts not found at {artifacts_path}")
    artifacts = joblib.load(artifacts_path)
    
    # Convert dict to series if needed
    if isinstance(opportunity_row, dict):
        opportunity_row = pd.Series(opportunity_row)
    
    # Validate required columns
    missing_cols = [c for c in ['ZipCode'] if c not in opportunity_row.index]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Run optimizer with loaded artifacts
    res = find_optimal_fee(
        sample_row=opportunity_row,
        features=artifacts['features'],
        encoders=artifacts['encoders'],
        train_medians=artifacts['train_medians'],
        model_full=artifacts['model_full'],
        clf=artifacts['clf'],
        base_multiplier=0.2,
        steps=60
    )
    
    # Add fee curve as DataFrame
    fee_curve = pd.DataFrame({
        'fee': res['fee_grid'],
        'win_prob': res['win_probs'],
        'expected_value': res['evs']
    })
    
    # Add diagnostics
    diagnostics = {
        'model_type': 'classifier' if artifacts['clf'] is not None else 'regressor_fallback',
        'features_present': sum(c in opportunity_row.index for c in artifacts['features']),
        'total_features': len(artifacts['features']),
        'warning': None
    }
    
    if diagnostics['features_present'] < diagnostics['total_features'] * 0.8:
        diagnostics['warning'] = 'Many features missing; predictions may be less reliable'
    
    return {
        'best_fee': float(res['best_fee']),
        'best_prob': float(res['best_prob']),
        'best_ev': float(res['best_ev']),
        'fee_curve': fee_curve.to_dict(orient='records'),
        'diagnostics': diagnostics
    }

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Get bid fee recommendations for an opportunity')
    parser.add_argument('--input', type=str, required=True, help='Path to JSON file with opportunity data')
    args = parser.parse_args()
    
    # Load opportunity
    with open(args.input) as f:
        opportunity = json.load(f)
    
    # Get recommendations
    result = recommend_bid_fee(opportunity)
    
    # Print results
    print(f"\nRecommended bid fee: ${result['best_fee']:.2f}")
    print(f"Win probability: {result['best_prob']:.1%}")
    print(f"Expected value: ${result['best_ev']:.2f}")
    print("\nModel diagnostics:", result['diagnostics'])
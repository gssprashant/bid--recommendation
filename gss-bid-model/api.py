from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import joblib
import os
import pandas as pd
import numpy as np
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response


app = FastAPI(title="GSS Bid Recommendation API")

# Metrics
PREDICTION_COUNT = Counter('prediction_requests_total', 'Total prediction requests')
PREDICTION_LATENCY = Histogram('prediction_latency_seconds', 'Prediction latency in seconds')


class BidRequest(BaseModel):
    BidDate: str = Field(..., example="2024-03-15")
    ProjectType: Optional[str]
    Location: Optional[str]
    ClientType: Optional[str]
    EstimatedCost: Optional[float]
    CompetitorCount: Optional[int]
    BidAmount: Optional[float]


class PredictResponse(BaseModel):
    predicted_bid: float
    win_probability: float
    timestamp: str


MODEL_DIR = os.getenv('MODEL_DIR', 'models')


def load_artifacts(model_dir: str = MODEL_DIR):
    """Attempt to load models. Supports either full pipelines saved as joblib or separate artifacts.

    Returns a dict with keys 'clf', 'reg', and optionally 'pre'.
    """
    artifacts = {}
    base = os.path.abspath(model_dir)
    try:
        # Try full pipeline names first
        clf_path = os.path.join(base, 'win_model.joblib')
        reg_path = os.path.join(base, 'bid_model.joblib')
        pre_path = os.path.join(base, 'preprocessor.joblib')
        if os.path.exists(clf_path):
            artifacts['clf'] = joblib.load(clf_path)
        if os.path.exists(reg_path):
            artifacts['reg'] = joblib.load(reg_path)
        if os.path.exists(pre_path):
            artifacts['pre'] = joblib.load(pre_path)

        # If none found, try the older single-file pickle
        if not artifacts:
            raise FileNotFoundError('No model artifacts found in ' + base)

        return artifacts
    except Exception as e:
        raise RuntimeError(f'Error loading model artifacts: {e}')


# Load on startup
artifacts = None


@app.on_event('startup')
def startup_event():
    global artifacts
    try:
        artifacts = load_artifacts(MODEL_DIR)
        app.state.models_loaded = True
    except Exception as e:
        # keep server alive but mark models missing
        artifacts = {}
        app.state.models_loaded = False
        print('Warning: models not loaded at startup:', e)


@app.get('/health')
def health():
    return {"status": "healthy", "models_loaded": app.state.models_loaded}


@app.get('/metrics')
def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)


def _prepare_df(payload: Dict[str, Any]) -> pd.DataFrame:
    # Minimal conversion to DataFrame and basic validation
    df = pd.DataFrame([payload])
    if 'BidDate' in df.columns:
        df['BidDate'] = pd.to_datetime(df['BidDate'])
    return df


@app.post('/predict', response_model=PredictResponse)
def predict(req: BidRequest):
    PREDICTION_COUNT.inc()
    with PREDICTION_LATENCY.time():
        if not app.state.models_loaded:
            raise HTTPException(status_code=503, detail='Models not loaded on server')

        payload = req.dict()
        try:
            X = _prepare_df(payload)

            # Prefer classifier pipeline that contains preprocessing
            clf = artifacts.get('clf')
            reg = artifacts.get('reg')

            if clf is None or reg is None:
                raise HTTPException(status_code=500, detail='Required model artifacts missing')

            # If clf is a pipeline that accepts DataFrame directly, call predict_proba
            try:
                if hasattr(clf, 'predict_proba'):
                    pwin = clf.predict_proba(X)[:, 1]
                else:
                    pwin = clf.predict(X)
            except Exception:
                # Try applying preprocessor if available
                pre = artifacts.get('pre')
                if pre is not None:
                    Xp = pre.transform(X)
                    if hasattr(clf, 'predict_proba'):
                        pwin = clf.named_steps['model'].predict_proba(Xp)[:, 1] if hasattr(clf, 'named_steps') else clf.predict_proba(Xp)[:,1]
                    else:
                        pwin = clf.named_steps['model'].predict(Xp) if hasattr(clf, 'named_steps') else clf.predict(Xp)
                else:
                    raise

            # Regression prediction: prefer using reg.predict (assumes it handles preprocessing)
            try:
                pred_bid = reg.predict(X)
            except Exception:
                pre = artifacts.get('pre')
                if pre is not None:
                    Xp = pre.transform(X)
                    pred_bid = reg.named_steps['model'].predict(Xp) if hasattr(reg, 'named_steps') else reg.predict(Xp)
                else:
                    raise

            pwin_val = float(np.asarray(pwin).ravel()[0])
            pred_bid_val = float(np.asarray(pred_bid).ravel()[0])

            return PredictResponse(predicted_bid=pred_bid_val, win_probability=pwin_val, timestamp=datetime.utcnow().isoformat())
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@app.post('/optimize')
def optimize(req: BidRequest, pct_range: float = 0.2, n_steps: int = 41):
    """Search for bid that maximizes expected profit = P(win) * bid"""
    if not app.state.models_loaded:
        raise HTTPException(status_code=503, detail='Models not loaded on server')
    payload = req.dict()
    X = _prepare_df(payload)

    clf = artifacts.get('clf')
    if clf is None:
        raise HTTPException(status_code=500, detail='Classifier missing')

    baseline = payload.get('BidAmount') or payload.get('EstimatedCost') or 100000.0
    candidates = np.linspace(baseline * (1 - pct_range), baseline * (1 + pct_range), n_steps)
    best = None
    rows = []
    for c in candidates:
        Xc = X.copy()
        Xc['BidAmount'] = float(c)
        try:
            if hasattr(clf, 'predict_proba'):
                p = clf.predict_proba(Xc)[:, 1]
            else:
                p = clf.predict(Xc)
            p = float(np.asarray(p).ravel()[0])
            expected = p * float(c)
            rows.append({'candidate': float(c), 'p_win': p, 'expected_profit': expected})
            if best is None or expected > best['expected_profit']:
                best = {'candidate': float(c), 'p_win': p, 'expected_profit': expected}
        except Exception as e:
            # skip candidate on failure
            continue

    return {"best": best, "candidates": rows}

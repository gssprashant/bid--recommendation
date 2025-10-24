# GSS Bid Model (MLOps-ready)

This workspace contains a production-ready scaffold for the Bid Recommendation models. It includes:

- Data pipeline and feature engineering with rolling and lagged features
- Integration helper for FRED economic data (requires FRED API key)
- Two-model training: Win probability (classification) and Bid amount (regression)
- SHAP analysis utilities
- Prediction + bid-optimization script that chooses the bid maximizing expected profit (P(win) * bid)

Quick start (Windows PowerShell):

1. Create a virtual environment and install dependencies

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Prepare data
- Place your CSV(s) into the `data/` directory. The training script expects a main CSV with columns: `BidDate`, `BidAmount`, `WinStatus`, and any optional columns like `ProjectType`, `Location`, `ClientType`, `EstimatedCost`, `CompetitorCount`.

3. Train models (smoke test)

```powershell
python scripts\train.py --data-path data/sample_bid_data.csv --output models/
```

4. Predict an optimal bid for a new opportunity

```powershell
python scripts\predict_optimize.py --model-dir models/ --input-json examples/sample_input.json
```

Notes:
- FRED integration requires setting environment variable `FRED_API_KEY` if you want to enrich data with official macro series.
- The pipeline saves preprocessing pipeline and trained models into the `models/` directory.

If you want, I can move your existing notebooks into `notebooks/` and run the smoke test. Confirm and I will proceed.
# GSS Bid Recommendation Model

An advanced machine learning system for optimal bid amount recommendations using XGBoost and time-series features.

## Project Structure

```
gss-bid-model/
├── src/               # Source code
│   ├── data/         # Data processing modules
│   ├── features/     # Feature engineering
│   ├── models/       # Model training and inference
│   └── api/          # FastAPI application
├── notebooks/        # Jupyter notebooks
├── models/          # Saved model artifacts
├── docker/          # Docker configuration
├── k8s/             # Kubernetes manifests
├── tests/           # Unit and integration tests
├── config/          # Configuration files
└── docs/           # Documentation
```

## Features

- XGBoost-based regression model
- Time-series feature engineering
- Cross-validation with time series split
- MLOps ready with Docker and Kubernetes
- Real-time predictions via REST API
- Monitoring and metrics collection

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Train the model:
```bash
python src/models/train.py
```

3. Run the API locally:
```bash
uvicorn src.api.main:app --reload
```

4. Deploy with Docker:
```bash
docker-compose up -d
```

## Model Details

The bid recommendation model uses:
- Historical bid data
- Project characteristics
- Market conditions
- Competitor analysis
- Time-based features

## API Documentation

Endpoints:
- `POST /predict`: Get bid recommendations
- `GET /health`: Health check
- `GET /metrics`: Prometheus metrics

## MLOps Integration

- Docker containerization
- Kubernetes deployment
- Prometheus metrics
- Grafana dashboards
- CI/CD pipelines

## Development

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

2. Install dev dependencies:
```bash
pip install -r requirements-dev.txt
```

3. Run tests:
```bash
pytest tests/
```

## License

MIT License
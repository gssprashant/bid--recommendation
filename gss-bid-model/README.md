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
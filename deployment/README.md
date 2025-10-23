# Bid Fee Prediction Model Deployment

This repository contains a machine learning model for predicting optimal bid fees based on property and market data.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/gssprashant/bid--recommendation.git
cd bid--recommendation/deployment
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

3. Ensure model files are in place:
The following files should be in the `models` directory:
- `bid_fee_model.joblib`
- `model_metadata.joblib`

## Running the API

1. Start the FastAPI server:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

2. Access the API documentation:
- OpenAPI docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### POST /predict
Make a bid fee prediction

Example request:
```json
{
    "ZipCode": "12345",
    "PropertyType": "Office",
    "DistanceInMiles": 10.5,
    "BidDate": "2025-10-23",
    "Market": "NYC",
    "BusinessSegment": "Commercial",
    "PopulationEstimate": 50000,
    "AverageHouseValue": 500000
}
```

Example response:
```json
{
    "predicted_fee": 2500.50,
    "confidence_score": 0.85,
    "timestamp": "2025-10-23T12:34:56.789Z",
    "model_version": "1.0.0",
    "features_used": ["ZipCode_encoded", "PropertyType_encoded", ...]
}
```

### GET /health
Health check endpoint

### GET /model-info
Get model information and metadata

## Docker Deployment

1. Build the Docker image:
```bash
docker build -t bid-fee-predictor .
```

2. Run the container:
```bash
docker run -d -p 8000:8000 bid-fee-predictor
```

## Model Updates

To update the model:

1. Run the notebook `bidmodelv2.ipynb`
2. New model files will be saved to `models/`
3. Restart the API server to load the new model

## Environment Variables

- `MODEL_PATH`: Path to model file (default: models/bid_fee_model.joblib)
- `METADATA_PATH`: Path to metadata file (default: models/model_metadata.joblib)
- `LOG_LEVEL`: Logging level (default: INFO)

## Monitoring

The API provides basic monitoring through:
- Health check endpoint (/health)
- Model info endpoint (/model-info)
- Standard FastAPI logging

For production, consider adding:
- Prometheus metrics
- ELK stack integration
- APM monitoring
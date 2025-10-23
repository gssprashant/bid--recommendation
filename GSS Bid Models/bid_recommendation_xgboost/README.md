# XGBoost Bid Recommendation Model

This directory contains the XGBoost-based bid recommendation model that predicts optimal bid amounts based on historical bid data and project characteristics.

## Model Features

- Time-series based feature engineering
- Cross-validation with time-series split
- Feature importance analysis
- Model persistence and MLOps integration
- Production-ready inference API

## Files Description

- `bid_recommendation_model.ipynb`: Main notebook with model development and training
- `requirements.txt`: Required Python packages
- `models/`: Directory containing saved model artifacts
- `config/`: Configuration files and model metadata

## Model Performance

The model uses time-series cross-validation to ensure robust performance:
- Uses XGBoost Regressor
- Includes rolling window features
- Handles categorical variables
- Provides win probability estimates

## MLOps Integration

The model is compatible with the existing MLOps infrastructure:
- Docker containerization
- Kubernetes deployment
- FastAPI interface
- Prometheus metrics

## Usage

1. Run the Jupyter notebook to train the model
2. Model artifacts are saved in the `models` directory
3. Use the existing deployment scripts to deploy
4. Access predictions via the REST API

## Input Features

Required:
- `BidDate`: Date of the bid
- `ProjectType`: Type of project
- `Location`: Project location
- `ClientType`: Type of client
- `EstimatedCost`: Estimated project cost
- `CompetitorCount`: Number of competitors

## Model Output

The model provides:
- Predicted optimal bid amount
- Win probability estimate
- Expected value calculation
- Bid amount recommendations curve
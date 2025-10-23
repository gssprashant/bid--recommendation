from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import joblib
import os
from typing import Dict, Optional, List
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="Bid Fee Prediction API",
    description="API for predicting optimal bid fees based on property and market data",
    version="1.0.0"
)

# Load model and metadata
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models/bid_fee_model.joblib")
METADATA_PATH = os.path.join(os.path.dirname(__file__), "models/model_metadata.joblib")

try:
    model = joblib.load(MODEL_PATH)
    metadata = joblib.load(METADATA_PATH)
    feature_cols = metadata['feature_cols']
    encoders = metadata['encoders']
    cat_cols = metadata['cat_cols']
except Exception as e:
    raise RuntimeError(f"Failed to load model files: {str(e)}")

class BidRequest(BaseModel):
    """Request model for bid fee prediction"""
    ZipCode: str
    PropertyType: str
    DistanceInMiles: float
    BidDate: str  # Format: YYYY-MM-DD
    # Add optional fields
    SubType: Optional[str] = None
    PropertyState: Optional[str] = None
    Market: Optional[str] = None
    Submarket: Optional[str] = None
    BusinessSegment: Optional[str] = None
    BidCompanyType: Optional[str] = None
    # Market metrics
    PopulationEstimate: Optional[float] = None
    AverageHouseValue: Optional[float] = None
    IncomePerHousehold: Optional[float] = None
    MedianAge: Optional[float] = None
    NumberofBusinesses: Optional[float] = None
    NumberofEmployees: Optional[float] = None
    ZipPopulation: Optional[float] = None
    # Historical metrics
    JobCount: Optional[int] = None
    IECount: Optional[int] = None
    LeaseCount: Optional[int] = None
    SaleCount: Optional[int] = None

class BidResponse(BaseModel):
    """Response model for bid fee prediction"""
    predicted_fee: float
    confidence_score: float
    timestamp: str
    model_version: str
    features_used: List[str]

def prepare_features(data: Dict) -> pd.DataFrame:
    """Prepare features for prediction"""
    # Convert to DataFrame
    df = pd.DataFrame([data])
    
    # Convert date
    df['BidDate'] = pd.to_datetime(df['BidDate'])
    df['Year'] = df['BidDate'].dt.year
    df['Month'] = df['BidDate'].dt.month
    df['Week'] = df['BidDate'].dt.isocalendar().week
    df['DayOfWeek'] = df['BidDate'].dt.dayofweek
    
    # Process categorical columns
    for col in cat_cols:
        if col in df.columns:
            df[f'{col}_encoded'] = df[col].astype(str).map(
                lambda x: encoders[col].transform([x])[0] if x in encoders[col].classes_ else -1
            )
    
    # Calculate market-based features
    market_cols = [
        'PopulationEstimate', 'AverageHouseValue', 'IncomePerHousehold',
        'MedianAge', 'NumberofBusinesses', 'NumberofEmployees', 'ZipPopulation'
    ]
    
    for col in market_cols:
        if col in df.columns:
            df[f'{col}_zip_ratio'] = 1.0  # Default to 1.0 for single predictions
    
    # Ensure all feature columns exist
    for col in feature_cols:
        if col not in df.columns:
            df[col] = 0  # Default value for missing features
    
    return df[feature_cols]

@app.post("/predict", response_model=BidResponse)
async def predict(request: BidRequest):
    """
    Predict optimal bid fee based on property and market data
    """
    try:
        # Convert request to dict
        data = request.dict()
        
        # Prepare features
        features = prepare_features(data)
        
        # Make prediction
        prediction = model.predict(features)[0]
        
        # Get prediction probability as confidence score
        confidence = min(max(model.predict_proba(features)[0].max(), 0.5), 0.99)
        
        return BidResponse(
            predicted_fee=float(prediction),
            confidence_score=float(confidence),
            timestamp=datetime.now().isoformat(),
            model_version="1.0.0",
            features_used=feature_cols
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "metadata_loaded": metadata is not None
    }

@app.get("/model-info")
async def model_info():
    """
    Get model information
    """
    return {
        "version": "1.0.0",
        "feature_columns": feature_cols,
        "categorical_columns": cat_cols,
        "model_type": type(model).__name__,
        "last_updated": datetime.fromtimestamp(os.path.getmtime(MODEL_PATH)).isoformat()
    }
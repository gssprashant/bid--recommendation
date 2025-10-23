"""
FastAPI application for bid recommendation service
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import uvicorn
from bid_inference import recommend_bid_fee

app = FastAPI(
    title="Bid Recommendation API",
    description="API for getting optimal bid fee recommendations",
    version="1.0.0"
)

class OpportunityInput(BaseModel):
    ZipCode: str
    PropertyType: Optional[str] = None
    BidCompanyName: Optional[str] = None
    Market: Optional[str] = None
    BidCompanyType: Optional[str] = None

class BidRecommendation(BaseModel):
    best_fee: float
    best_prob: float
    best_ev: float
    fee_curve: List[Dict[str, float]]
    diagnostics: Dict[str, any]

@app.get("/")
def read_root():
    return {"status": "healthy", "service": "bid-recommendation-api"}

@app.post("/predict", response_model=BidRecommendation)
def predict(opportunity: OpportunityInput):
    try:
        result = recommend_bid_fee(opportunity.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
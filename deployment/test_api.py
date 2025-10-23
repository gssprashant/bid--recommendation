import requests
import json
from datetime import datetime, timedelta

def test_prediction_api():
    """Test the bid fee prediction API"""
    # API endpoint
    url = "http://localhost:8000/predict"
    
    # Test data
    test_data = {
        "ZipCode": "12345",
        "PropertyType": "Office",
        "DistanceInMiles": 10.5,
        "BidDate": datetime.now().strftime("%Y-%m-%d"),
        "Market": "NYC",
        "BusinessSegment": "Commercial",
        "PopulationEstimate": 50000,
        "AverageHouseValue": 500000,
        "IncomePerHousehold": 75000,
        "MedianAge": 35,
        "NumberofBusinesses": 1000,
        "NumberofEmployees": 10000,
        "ZipPopulation": 25000
    }
    
    try:
        # Make prediction request
        response = requests.post(url, json=test_data)
        
        if response.status_code == 200:
            result = response.json()
            print("\nPrediction successful!")
            print(f"Predicted bid fee: ${result['predicted_fee']:.2f}")
            print(f"Confidence score: {result['confidence_score']:.2%}")
            print(f"Model version: {result['model_version']}")
            return True
        else:
            print(f"\nError: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"\nError: {str(e)}")
        return False

def test_health_check():
    """Test the health check endpoint"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("\nHealth check successful!")
            print(json.dumps(response.json(), indent=2))
            return True
        return False
    except Exception as e:
        print(f"\nHealth check failed: {str(e)}")
        return False

def test_model_info():
    """Test the model info endpoint"""
    try:
        response = requests.get("http://localhost:8000/model-info")
        if response.status_code == 200:
            print("\nModel info retrieved successfully!")
            print(json.dumps(response.json(), indent=2))
            return True
        return False
    except Exception as e:
        print(f"\nModel info request failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Bid Fee Prediction API...")
    
    # Run all tests
    health_ok = test_health_check()
    model_info_ok = test_model_info()
    prediction_ok = test_prediction_api()
    
    # Print summary
    print("\nTest Summary:")
    print(f"Health Check: {'✓' if health_ok else '✗'}")
    print(f"Model Info: {'✓' if model_info_ok else '✗'}")
    print(f"Prediction: {'✓' if prediction_ok else '✗'}")
    
    if all([health_ok, model_info_ok, prediction_ok]):
        print("\nAll tests passed successfully!")
        exit(0)
    else:
        print("\nSome tests failed!")
        exit(1)
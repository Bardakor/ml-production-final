import pytest
import requests
import time
import os
from unittest.mock import patch

BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")

@pytest.fixture(scope="module")
def api_ready():
    """Wait for API to be ready"""
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/")
            if response.status_code == 200:
                return True
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    pytest.fail("API not ready after 30 seconds")

def test_full_prediction_workflow(api_ready):
    """Test complete prediction workflow"""
    # 1. Check health
    health_response = requests.get(f"{BASE_URL}/")
    assert health_response.status_code == 200
    health_data = health_response.json()
    assert health_data["status"] == "healthy"
    
    # 2. Check model info
    model_response = requests.get(f"{BASE_URL}/model/info")
    assert model_response.status_code == 200
    model_data = model_response.json()
    assert model_data["model_loaded"] is True
    
    # 3. Make prediction
    prediction_data = {
        "features": [1.0, 2.0, 3.0, 4.0],
        "user_id": "integration-test-user"
    }
    
    pred_response = requests.post(f"{BASE_URL}/predict", json=prediction_data)
    assert pred_response.status_code == 200
    pred_data = pred_response.json()
    
    assert "prediction" in pred_data
    assert "confidence" in pred_data
    assert "model_version" in pred_data
    assert isinstance(pred_data["prediction"], float)
    assert 0 <= pred_data["confidence"] <= 1

def test_api_error_handling(api_ready):
    """Test API error handling"""
    # Test with invalid features
    invalid_data = {"features": []}
    response = requests.post(f"{BASE_URL}/predict", json=invalid_data)
    assert response.status_code in [400, 422, 500]  # Some kind of error

def test_concurrent_predictions(api_ready):
    """Test multiple concurrent predictions"""
    import concurrent.futures
    
    def make_prediction(i):
        data = {
            "features": [i, i+1, i+2, i+3],
            "user_id": f"concurrent-user-{i}"
        }
        response = requests.post(f"{BASE_URL}/predict", json=data)
        return response.status_code == 200
    
    # Make 5 concurrent requests
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_prediction, i) for i in range(5)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    # All requests should succeed
    assert all(results) 
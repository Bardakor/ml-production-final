import pytest
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))

from main import app, load_model, PredictionRequest

@pytest.fixture
def client():
    """Create a test client"""
    from fastapi.testclient import TestClient
    return TestClient(app)

def test_health_endpoint(client):
    """Test the health check endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model_loaded" in data
    assert "timestamp" in data

def test_model_info_endpoint(client):
    """Test the model info endpoint"""
    response = client.get("/model/info")
    assert response.status_code == 200
    data = response.json()
    assert "model_loaded" in data
    assert "model_version" in data
    assert "model_type" in data

@patch('main.model')
def test_prediction_endpoint(mock_model, client):
    """Test the prediction endpoint"""
    # Mock the model prediction
    mock_model.predict.return_value = np.array([1.5])
    
    prediction_data = {
        "features": [1.0, 2.0, 3.0, 4.0],
        "user_id": "test-user"
    }
    
    response = client.post("/predict", json=prediction_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "prediction" in data
    assert "confidence" in data
    assert "model_version" in data
    assert "timestamp" in data

def test_prediction_invalid_input(client):
    """Test prediction with invalid input"""
    prediction_data = {
        "features": "invalid"
    }
    
    response = client.post("/predict", json=prediction_data)
    assert response.status_code == 422  # Validation error 
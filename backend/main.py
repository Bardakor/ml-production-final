from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ML Production API",
    description="A production-ready ML API serving predictions",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase client (optional for now)
try:
    from supabase import create_client, Client
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    supabase: Client = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None
except ImportError:
    logger.warning("Supabase client not available")
    supabase = None

# Simple dummy model class
class DummyModel:
    def __init__(self):
        self.coefficients = np.array([2.0, 1.5, 0.5, 0.8])
        self.intercept = 0.1
        
    def predict(self, X):
        """Simple linear model prediction"""
        if len(X.shape) == 1:
            X = X.reshape(1, -1)
        return np.dot(X, self.coefficients) + self.intercept

# Global model variable
model = DummyModel()
model_version = "dummy-v1.0"

class PredictionRequest(BaseModel):
    features: List[float]
    user_id: str = None

class PredictionResponse(BaseModel):
    prediction: float
    confidence: float
    model_version: str
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    timestamp: str

def load_model():
    """Load or create the model"""
    global model, model_version
    try:
        # Try to load MLflow model if available
        try:
            import mlflow
            import mlflow.sklearn
            
            mlflow_uri = os.getenv("MLFLOW_TRACKING_URI")
            if mlflow_uri:
                mlflow.set_tracking_uri(mlflow_uri)
                
                client = mlflow.MlflowClient()
                model_name = os.getenv("MODEL_NAME", "ml-production-model")
                
                try:
                    latest_version = client.get_latest_versions(model_name, stages=["Production"])[0]
                    model_uri = f"models:/{model_name}/{latest_version.version}"
                    model = mlflow.sklearn.load_model(model_uri)
                    model_version = latest_version.version
                    logger.info(f"Loaded MLflow model: {model_name} version {latest_version.version}")
                    return latest_version.version
                except Exception as e:
                    logger.warning(f"Could not load MLflow model: {e}")
                    
        except ImportError:
            logger.info("MLflow not available, using dummy model")
            
        # Fallback to dummy model
        model = DummyModel()
        model_version = "dummy-v1.0"
        logger.info("Using dummy linear model")
        return model_version
        
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        model = DummyModel()
        model_version = "dummy-v1.0"
        return model_version

# Load model on startup
load_model()

@app.get("/", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        model_loaded=model is not None,
        timestamp=datetime.now().isoformat()
    )

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Make a prediction using the loaded model"""
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    try:
        # Validate input
        if len(request.features) != 4:
            raise HTTPException(status_code=400, detail="Expected 4 features")
            
        # Make prediction
        features_array = np.array(request.features).reshape(1, -1)
        prediction = model.predict(features_array)[0]
        
        # Calculate confidence (simplified)
        confidence = min(0.95, max(0.5, 0.8 + np.random.random() * 0.15))
        
        # Log prediction to Supabase if available
        if supabase and request.user_id:
            try:
                supabase.table("predictions").insert({
                    "user_id": request.user_id,
                    "features": request.features,
                    "prediction": float(prediction),
                    "confidence": confidence,
                    "model_version": model_version,
                    "created_at": datetime.now().isoformat()
                }).execute()
            except Exception as e:
                logger.warning(f"Failed to log prediction to Supabase: {e}")
        
        return PredictionResponse(
            prediction=float(prediction),
            confidence=confidence,
            model_version=model_version,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/model/info")
async def get_model_info():
    """Get information about the current model"""
    return {
        "model_loaded": model is not None,
        "model_version": model_version,
        "model_type": type(model).__name__ if model else None,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/predictions/history")
async def get_prediction_history(user_id: str = None, limit: int = 100):
    """Get prediction history from Supabase"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not available")
    
    try:
        query = supabase.table("predictions").select("*").limit(limit)
        
        if user_id:
            query = query.eq("user_id", user_id)
        
        result = query.order("created_at", desc=True).execute()
        return result.data
    
    except Exception as e:
        logger.error(f"Error fetching prediction history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Load environment variables
load_dotenv()

def generate_sample_data(n_samples=1000):
    """Generate sample data for demonstration"""
    np.random.seed(42)
    
    # Generate 4 features with different patterns
    X = np.random.randn(n_samples, 4)
    
    # Create a target variable with some relationship to features
    y = (2 * X[:, 0] + 
         1.5 * X[:, 1] + 
         0.5 * X[:, 2] + 
         0.8 * X[:, 3] + 
         np.random.randn(n_samples) * 0.1)
    
    # Create DataFrame
    df = pd.DataFrame(X, columns=['feature_1', 'feature_2', 'feature_3', 'feature_4'])
    df['target'] = y
    
    return df

def train_model():
    """Train and register the model with MLflow"""
    print("🤖 Training ML model with MLflow...")
    
    # Configure MLflow
    mlflow_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    mlflow.set_tracking_uri(mlflow_uri)
    mlflow.set_experiment("ml-production-experiment")
    
    # Generate data
    df = generate_sample_data()
    print(f"Generated {len(df)} samples with 4 features")
    
    # Split features and target
    X = df.drop('target', axis=1)
    y = df['target']
    
    # Split data for training and testing
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Start MLflow run
    with mlflow.start_run() as run:
        # Model parameters
        n_estimators = 100
        max_depth = 10
        random_state = 42
        
        # Train model
        model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state
        )
        
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        print(f"Model Performance:")
        print(f"MSE: {mse:.4f}")
        print(f"R2 Score: {r2:.4f}")
        
        # Log parameters
        mlflow.log_param("n_estimators", n_estimators)
        mlflow.log_param("max_depth", max_depth)
        mlflow.log_param("random_state", random_state)
        mlflow.log_param("n_features", 4)
        mlflow.log_param("n_samples", len(df))
        
        # Log metrics
        mlflow.log_metric("mse", mse)
        mlflow.log_metric("r2_score", r2)
        
        # Log model
        mlflow.sklearn.log_model(
            model, 
            "model",
            registered_model_name="ml-production-model"
        )
        
        print("✅ Model logged to MLflow successfully!")
        print(f"Run ID: {run.info.run_id}")
        print(f"MLflow UI: {mlflow_uri}")
        
    # Save model locally as backup
    model_dir = "models"
    os.makedirs(model_dir, exist_ok=True)
    
    import joblib
    joblib.dump(model, os.path.join(model_dir, "model.pkl"))
    
    print(f"✅ Model also saved locally in {model_dir}/")
    print("🎉 Model training completed successfully!")
    
    return {
        "model": model,
        "mse": mse,
        "r2_score": r2,
        "run_id": run.info.run_id
    }

if __name__ == "__main__":
    model_info = train_model() 
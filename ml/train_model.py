import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_sample_data(n_samples=1000):
    """Generate sample data for demonstration"""
    np.random.seed(42)
    
    # Generate 4 features
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
    """Train and save a simple model"""
    print("🤖 Training ML model...")
    
    # Generate data
    df = generate_sample_data()
    print(f"Generated {len(df)} samples with 4 features")
    
    # Split features and target
    X = df.drop('target', axis=1)
    y = df['target']
    
    # Simple linear regression coefficients (manually calculated)
    # This is a simplified version - in production you'd use proper ML libraries
    
    # Calculate means
    X_mean = X.mean()
    y_mean = y.mean()
    
    # Calculate coefficients using normal equation approximation
    coefficients = []
    for col in X.columns:
        # Simple correlation-based coefficient
        correlation = np.corrcoef(X[col], y)[0, 1]
        std_ratio = y.std() / X[col].std()
        coef = correlation * std_ratio
        coefficients.append(coef)
    
    coefficients = np.array(coefficients)
    intercept = y_mean - np.dot(X_mean.values, coefficients)
    
    print(f"Model coefficients: {coefficients}")
    print(f"Model intercept: {intercept}")
    
    # Calculate simple metrics
    y_pred = np.dot(X.values, coefficients) + intercept
    mse = np.mean((y - y_pred) ** 2)
    r2 = 1 - (np.sum((y - y_pred) ** 2) / np.sum((y - y_mean) ** 2))
    
    print(f"MSE: {mse:.4f}")
    print(f"R2 Score: {r2:.4f}")
    
    # Try to log to MLflow if available
    try:
        import mlflow
        import mlflow.sklearn
        
        # Configure MLflow
        mlflow_uri = os.getenv("MLFLOW_TRACKING_URI")
        if mlflow_uri:
            mlflow.set_tracking_uri(mlflow_uri)
            mlflow.set_experiment("ml-production-experiment")
            
            # Start MLflow run
            with mlflow.start_run():
                # Log parameters
                mlflow.log_param("model_type", "simple_linear")
                mlflow.log_param("n_features", 4)
                mlflow.log_param("n_samples", len(df))
                
                # Log metrics
                mlflow.log_metric("mse", mse)
                mlflow.log_metric("r2_score", r2)
                
                # Log coefficients as metrics
                for i, coef in enumerate(coefficients):
                    mlflow.log_metric(f"coef_{i}", coef)
                mlflow.log_metric("intercept", intercept)
                
                print("✅ Model logged to MLflow successfully!")
                
    except ImportError:
        print("ℹ️  MLflow not available - model metrics logged locally only")
    except Exception as e:
        print(f"⚠️  Could not log to MLflow: {e}")
    
    # Save model locally as simple numpy arrays
    model_dir = "models"
    os.makedirs(model_dir, exist_ok=True)
    
    np.save(os.path.join(model_dir, "coefficients.npy"), coefficients)
    np.save(os.path.join(model_dir, "intercept.npy"), intercept)
    
    print(f"✅ Model saved locally in {model_dir}/")
    print("🎉 Model training completed successfully!")
    
    return {
        "coefficients": coefficients,
        "intercept": intercept,
        "mse": mse,
        "r2_score": r2
    }

if __name__ == "__main__":
    model = train_model() 
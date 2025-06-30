#!/bin/bash

# Quick Start Script for ML Production App
echo "🚀 Quick Start - ML Production App"

# Set up environment files if they don't exist
if [ ! -f "backend/.env" ]; then
    echo "[INFO] Setting up basic environment files..."
    cat > backend/.env << EOF
# Backend Configuration
MLFLOW_TRACKING_URI=http://localhost:5000
MODEL_NAME=ml-production-model
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
BACKEND_PORT=8000
EOF
    echo "[WARNING] Created backend/.env - please update with your actual credentials"
fi

if [ ! -f "frontend/.env.local" ]; then
    cat > frontend/.env.local << EOF
# Frontend Configuration
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_APP_ENV=development
EOF
    echo "[WARNING] Created frontend/.env.local - please update with your actual credentials"
fi

# Install backend dependencies
echo "[INFO] Installing backend dependencies..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
source venv/bin/activate
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install backend dependencies"
    echo "[INFO] This might be due to Python 3.13 compatibility issues"
    echo "[INFO] The current setup works with basic dependencies. For full ML features:"
    echo "       - Install scikit-learn separately: pip install 'scikit-learn>=1.5.0'"
    echo "       - Install MLflow separately: pip install mlflow"
    echo "       - Install Supabase separately: pip install supabase"
fi

cd ..

# Install frontend dependencies
echo "[INFO] Installing frontend dependencies..."
cd frontend
npm install

if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install frontend dependencies"
    exit 1
fi

# Build frontend to verify everything works
echo "[INFO] Building frontend..."
npm run build

if [ $? -ne 0 ]; then
    echo "[ERROR] Frontend build failed"
    exit 1
fi

cd ..

# Train initial model
echo "[INFO] Training initial model..."
cd backend
source venv/bin/activate
cd ../ml
python train_model.py

if [ $? -ne 0 ]; then
    echo "[WARNING] Model training failed, but app will work with dummy model"
fi

cd ..

echo ""
echo "✅ Quick start completed!"
echo ""
echo "📝 Next steps:"
echo "   1. Start the backend:"
echo "      cd backend && source venv/bin/activate && python main.py"
echo ""
echo "   2. In another terminal, start the frontend:"
echo "      cd frontend && npm run dev"
echo ""
echo "   3. Open http://localhost:3000 in your browser"
echo ""
echo "🔧 Optional enhancements:"
echo "   - Update .env files with real credentials"
echo "   - Install additional ML packages as needed"
echo "   - Set up MLflow tracking server"
echo "   - Configure Supabase database"
echo ""
echo "🎉 Happy coding!" 
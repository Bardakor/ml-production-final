# ML Production App - DevOps Final Project

A complete machine learning production web application built with FastAPI, Next.js, and modern DevOps practices.

## 🎯 Project Overview

This project demonstrates a full production-ready ML application including:
- **Backend**: FastAPI with ML model serving
- **Frontend**: Next.js with modern UI components
- **Machine Learning**: Model training and serving
- **Testing**: Unit, integration, and E2E tests
- **CI/CD**: GitHub Actions pipeline
- **Containerization**: Docker and Docker Compose
- **Cloud Deployment**: Google Cloud Platform ready

## ✅ Current Status

The application is **working** with Python 3.13 and includes:
- ✅ FastAPI backend with dummy ML model
- ✅ Next.js frontend with prediction interface
- ✅ Basic model training script
- ✅ Docker containerization
- ✅ Test suite structure
- ✅ CI/CD pipeline configuration

## 🚀 Quick Start

Run the setup script to get started immediately:

```bash
./scripts/quick-start.sh
```

Then follow these steps:

### 1. Start the Backend
```bash
cd backend
source venv/bin/activate
python main.py
```

The backend will be available at http://localhost:8000

### 2. Start the Frontend (in another terminal)
```bash
cd frontend
npm run dev
```

The frontend will be available at http://localhost:3000

### 3. Test the Application
- Open http://localhost:3000 in your browser
- Enter 4 numerical feature values
- Click "Get Prediction" to test the ML model

## 🏗️ Architecture

```
├── backend/           # FastAPI application
│   ├── main.py       # API endpoints and ML serving
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/         # Next.js application
│   ├── src/app/page.tsx  # Main UI component
│   ├── package.json
│   └── Dockerfile
├── ml/              # Machine learning components
│   └── train_model.py   # Model training script
├── tests/           # Test suites
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── scripts/         # Automation scripts
└── docker-compose.yml
```

## 🔧 Python 3.13 Compatibility

This project is configured to work with Python 3.13. Due to compatibility issues with some ML libraries, the current setup uses:
- **Working**: FastAPI, pandas, numpy (basic ML functionality)
- **Optional**: scikit-learn, MLflow, Supabase (install separately if needed)

### Installing Optional Dependencies

For full ML features, install these separately:

```bash
cd backend
source venv/bin/activate

# For advanced ML models
pip install 'scikit-learn>=1.5.0'

# For experiment tracking
pip install mlflow

# For database integration
pip install supabase
```

## 🧪 Testing

Run the test suites:

```bash
# Unit tests
cd backend && source venv/bin/activate
pytest tests/unit/

# Integration tests
pytest tests/integration/

# E2E tests
cd frontend
npm run test:e2e
```

## 🐳 Docker Deployment

Build and run with Docker:

```bash
# Build images
docker-compose build

# Run services
docker-compose up -d

# View logs
docker-compose logs -f
```

## ☁️ Cloud Deployment

The project includes GitHub Actions CI/CD for deployment to Google Cloud Platform:

1. Configure GCP credentials in GitHub secrets
2. Push to `main` branch for production deployment
3. Push to `staging` branch for staging deployment

## 📊 Features

- **Real-time ML Predictions**: REST API for model inference
- **Modern UI**: React-based interface with status monitoring
- **Health Monitoring**: API and model status indicators
- **Scalable Architecture**: Containerized microservices
- **Production Ready**: Logging, error handling, and monitoring

## 🔮 Roadmap / Optional Enhancements

- [ ] Install scikit-learn for advanced ML models
- [ ] Set up MLflow tracking server for experiment management
- [ ] Configure Supabase for data persistence
- [ ] Add DVC for data versioning with S3
- [ ] Implement user authentication
- [ ] Add model performance monitoring
- [ ] Set up alerts and notifications

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📝 License

This project is for educational purposes as part of a DevOps final project.

---

**Built with ❤️ for DevOps learning**

For questions or issues, please check the GitHub issues or create a new one. 

3 unt test, 1 integration test, 1 e2e test
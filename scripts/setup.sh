#!/bin/bash

set -e

echo "🚀 Setting up ML Production App..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3 first."
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    
    print_status "All dependencies are available!"
}

# Setup Google Cloud CLI
setup_gcp() {
    print_status "Setting up Google Cloud CLI..."
    
    if ! command -v gcloud &> /dev/null; then
        print_warning "Google Cloud CLI not found. Installing..."
        
        # Install gcloud (for macOS)
        if [[ "$OSTYPE" == "darwin"* ]]; then
            curl https://sdk.cloud.google.com | bash
            exec -l $SHELL
        else
            # For Linux
            curl https://sdk.cloud.google.com | bash
            exec -l $SHELL
        fi
    else
        print_status "Google Cloud CLI already installed"
    fi
    
    # Initialize gcloud
    print_status "Please authenticate with Google Cloud..."
    gcloud auth login
    gcloud config set project $(gcloud projects list --format="value(projectId)" --limit=1)
    
    print_status "Google Cloud CLI setup complete!"
}

# Setup Supabase CLI
setup_supabase() {
    print_status "Setting up Supabase CLI..."
    
    if ! command -v supabase &> /dev/null; then
        print_warning "Supabase CLI not found. Installing..."
        npm install -g supabase
    else
        print_status "Supabase CLI already installed"
    fi
    
    print_status "Please log in to Supabase..."
    supabase login
    
    print_status "Supabase CLI setup complete!"
}

# Setup DVC
setup_dvc() {
    print_status "Setting up DVC..."
    
    cd $(dirname "$0")/..
    
    # Initialize DVC
    if [ ! -d ".dvc" ]; then
        dvc init
        print_status "DVC initialized"
    else
        print_status "DVC already initialized"
    fi
    
    # Setup DVC remote (AWS S3)
    read -p "Enter your S3 bucket name for DVC: " bucket_name
    if [ ! -z "$bucket_name" ]; then
        dvc remote add -d myremote s3://$bucket_name/dvc
        print_status "DVC remote configured"
    fi
}

# Setup environment files
setup_env() {
    print_status "Setting up environment files..."
    
    cd $(dirname "$0")/..
    
    # Backend environment
    if [ ! -f "backend/.env" ]; then
        cp backend/env.example backend/.env
        print_warning "Please edit backend/.env with your actual values"
    fi
    
    # Frontend environment
    if [ ! -f "frontend/.env.local" ]; then
        cat > frontend/.env.local << EOF
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
EOF
        print_warning "Please edit frontend/.env.local with your actual values"
    fi
}

# Setup Supabase database
setup_database() {
    print_status "Setting up Supabase database..."
    
    cd $(dirname "$0")/..
    
    # Create Supabase project (if not exists)
    read -p "Enter your Supabase project name: " project_name
    if [ ! -z "$project_name" ]; then
        supabase projects create $project_name || print_warning "Project might already exist"
    fi
    
    # Create predictions table
    cat > setup_database.sql << EOF
-- Create predictions table
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    user_id TEXT NOT NULL,
    features JSONB NOT NULL,
    prediction FLOAT NOT NULL,
    confidence FLOAT NOT NULL,
    model_version TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_predictions_user_id ON predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON predictions(created_at);
EOF
    
    print_status "Database schema created. Please run the SQL commands in your Supabase dashboard."
    print_status "SQL file created: setup_database.sql"
}

# Setup MLflow on DagsHub
setup_mlflow() {
    print_status "Setting up MLflow with DagsHub..."
    
    print_status "Please follow these steps to setup DagsHub:"
    echo "1. Go to https://dagshub.com"
    echo "2. Create an account if you don't have one"
    echo "3. Create a new repository called 'ml-production-app'"
    echo "4. Get your access token from Settings > Access Tokens"
    echo "5. Update backend/.env with your DagsHub credentials"
    
    read -p "Press enter when you've completed the DagsHub setup..."
}

# Install project dependencies
install_dependencies() {
    print_status "Installing project dependencies..."
    
    cd $(dirname "$0")/..
    
    # Backend dependencies
    print_status "Installing backend dependencies..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    
    # Frontend dependencies
    print_status "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    
    print_status "Dependencies installed!"
}

# Train initial model
train_model() {
    print_status "Training initial ML model..."
    
    cd $(dirname "$0")/..
    cd backend
    source venv/bin/activate
    python ../ml/train_model.py
    cd ..
    
    print_status "Initial model trained and registered!"
}

# Main setup function
main() {
    print_status "Starting ML Production App setup..."
    
    check_dependencies
    
    echo
    read -p "Do you want to setup Google Cloud CLI? (y/n): " setup_gcp_choice
    if [[ $setup_gcp_choice == "y" ]]; then
        setup_gcp
    fi
    
    echo
    read -p "Do you want to setup Supabase CLI? (y/n): " setup_supabase_choice
    if [[ $setup_supabase_choice == "y" ]]; then
        setup_supabase
        setup_database
    fi
    
    echo
    read -p "Do you want to setup DVC? (y/n): " setup_dvc_choice
    if [[ $setup_dvc_choice == "y" ]]; then
        setup_dvc
    fi
    
    setup_env
    setup_mlflow
    install_dependencies
    
    echo
    read -p "Do you want to train an initial model? (y/n): " train_choice
    if [[ $train_choice == "y" ]]; then
        train_model
    fi
    
    print_status "Setup complete! 🎉"
    echo
    print_status "Next steps:"
    echo "1. Edit the .env files with your actual credentials"
    echo "2. Run 'docker-compose up' to start the development environment"
    echo "3. Visit http://localhost:3000 to see your app"
    echo "4. Visit http://localhost:5000 to see MLflow UI"
    echo
    print_status "Happy coding! 🚀"
}

# Run main function
main "$@" 
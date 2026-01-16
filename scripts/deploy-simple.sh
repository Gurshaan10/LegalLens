#!/bin/bash

# Simple Legal Lens Deployment Script (No Docker Required)
# This script helps deploy directly to cloud platforms

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Setup environment variables
setup_env() {
    print_status "Setting up environment variables..."
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        cp env.example .env
        print_warning "Created .env file from template. Please edit it with your actual values."
        print_status "Required variables:"
        echo "  - OPENAI_API_KEY"
        echo "  - REACT_APP_FIREBASE_API_KEY"
        echo "  - REACT_APP_FIREBASE_AUTH_DOMAIN"
        echo "  - REACT_APP_FIREBASE_PROJECT_ID"
        echo "  - REACT_APP_FIREBASE_STORAGE_BUCKET"
        echo "  - REACT_APP_FIREBASE_MESSAGING_SENDER_ID"
        echo "  - REACT_APP_FIREBASE_APP_ID"
    fi
    
    print_success "Environment setup completed"
}

# Deploy to Fly.io
deploy_fly() {
    print_status "Deploying to Fly.io..."
    
    # Check if fly CLI is installed
    if ! command -v fly &> /dev/null; then
        print_error "Fly CLI is not installed. Please install it first:"
        echo "curl -L https://fly.io/install.sh | sh"
        exit 1
    fi
    
    # Check if logged in to Fly
    if ! fly auth whoami &> /dev/null; then
        print_warning "Not logged in to Fly.io. Please run: fly auth login"
        exit 1
    fi
    
    # Create app if it doesn't exist
    if ! fly apps list | grep -q "legal-lens"; then
        print_status "Creating Fly.io app..."
        fly apps create legal-lens
    fi
    
    # Set secrets
    print_status "Setting environment variables..."
    if [ -f .env ]; then
        source .env
        fly secrets set OPENAI_API_KEY="$OPENAI_API_KEY"
        fly secrets set FIREBASE_ADMIN_CREDENTIAL="firebase-admin.json"
    fi
    
    # Deploy
    print_status "Deploying application..."
    fly deploy
    
    print_success "Deployed to Fly.io successfully"
    print_status "Your app is available at: https://legal-lens.fly.dev"
}

# Deploy to Railway
deploy_railway() {
    print_status "Deploying to Railway..."
    
    # Check if Railway CLI is installed
    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI is not installed. Please install it first:"
        echo "npm install -g @railway/cli"
        exit 1
    fi
    
    # Check if logged in to Railway
    if ! railway whoami &> /dev/null; then
        print_warning "Not logged in to Railway. Please run: railway login"
        exit 1
    fi
    
    # Initialize project if needed
    if [ ! -f railway.json ]; then
        print_status "Initializing Railway project..."
        railway init
    fi
    
    # Set environment variables
    print_status "Setting environment variables..."
    if [ -f .env ]; then
        source .env
        railway variables set OPENAI_API_KEY="$OPENAI_API_KEY"
        railway variables set FIREBASE_ADMIN_CREDENTIAL="firebase-admin.json"
    fi
    
    # Deploy
    print_status "Deploying application..."
    railway up
    
    print_success "Deployed to Railway successfully"
    print_status "Getting deployment URL..."
    railway domain
}

# Deploy to Render
deploy_render() {
    print_status "Deploying to Render..."
    
    print_status "Render deployment requires manual setup:"
    echo ""
    echo "1. Go to https://render.com"
    echo "2. Create a new account or sign in"
    echo "3. Click 'New +' and select 'Web Service'"
    echo "4. Connect your GitHub repository"
    echo "5. Configure the service:"
    echo "   - Name: legal-lens"
    echo "   - Environment: Python"
    echo "   - Build Command: pip install -r backend/requirements.txt"
    echo "   - Start Command: cd backend && uvicorn main:app --host 0.0.0.0 --port \$PORT"
    echo "6. Add environment variables:"
    echo "   - OPENAI_API_KEY"
    echo "   - FIREBASE_ADMIN_CREDENTIAL"
    echo "7. Deploy!"
    echo ""
    print_success "Render deployment guide completed"
}

# Deploy to Vercel (Frontend only)
deploy_vercel() {
    print_status "Deploying frontend to Vercel..."
    
    # Check if Vercel CLI is installed
    if ! command -v vercel &> /dev/null; then
        print_error "Vercel CLI is not installed. Please install it first:"
        echo "npm install -g vercel"
        exit 1
    fi
    
    # Check if logged in to Vercel
    if ! vercel whoami &> /dev/null; then
        print_warning "Not logged in to Vercel. Please run: vercel login"
        exit 1
    fi
    
    # Deploy frontend
    cd frontend
    print_status "Deploying React frontend..."
    vercel --prod
    
    print_success "Frontend deployed to Vercel successfully"
    print_warning "Note: You'll need to deploy the backend separately (Fly.io, Railway, etc.)"
}

# Setup Firebase
setup_firebase() {
    print_status "Setting up Firebase..."
    
    echo "Firebase Setup Instructions:"
    echo ""
    echo "1. Go to https://console.firebase.google.com/"
    echo "2. Create a new project or select existing"
    echo "3. Enable Google Authentication:"
    echo "   - Go to Authentication > Sign-in method"
    echo "   - Enable Google provider"
    echo "4. Get Frontend Config:"
    echo "   - Go to Project Settings > General"
    echo "   - Add a web app"
    echo "   - Copy the config to your .env file"
    echo "5. Get Backend Credentials:"
    echo "   - Go to Project Settings > Service Accounts"
    echo "   - Generate new private key"
    echo "   - Save as backend/firebase-admin.json"
    echo ""
    print_success "Firebase setup guide completed"
}

# Setup OpenAI
setup_openai() {
    print_status "Setting up OpenAI..."
    
    echo "OpenAI Setup Instructions:"
    echo ""
    echo "1. Go to https://platform.openai.com/"
    echo "2. Create an account or sign in"
    echo "3. Go to API Keys section"
    echo "4. Create a new API key"
    echo "5. Add the key to your .env file:"
    echo "   OPENAI_API_KEY=your_key_here"
    echo ""
    print_success "OpenAI setup guide completed"
}

# Main deployment function
main() {
    echo "🚀 Legal Lens Simple Deployment Script"
    echo "====================================="
    
    # Parse command line arguments
    case "${1:-help}" in
        "fly")
            setup_env
            deploy_fly
            ;;
        "railway")
            setup_env
            deploy_railway
            ;;
        "render")
            deploy_render
            ;;
        "vercel")
            deploy_vercel
            ;;
        "firebase")
            setup_firebase
            ;;
        "openai")
            setup_openai
            ;;
        "help"|*)
            echo "Usage: $0 {fly|railway|render|vercel|firebase|openai|help}"
            echo ""
            echo "Commands:"
            echo "  fly      - Deploy to Fly.io (recommended)"
            echo "  railway  - Deploy to Railway"
            echo "  render   - Deploy to Render (manual setup)"
            echo "  vercel   - Deploy frontend to Vercel"
            echo "  firebase - Firebase setup guide"
            echo "  openai   - OpenAI setup guide"
            echo "  help     - Show this help message"
            echo ""
            echo "Before deploying:"
            echo "1. Run: $0 firebase"
            echo "2. Run: $0 openai"
            echo "3. Edit .env file with your credentials"
            echo "4. Deploy with: $0 fly"
            ;;
    esac
}

# Run main function
main "$@" 
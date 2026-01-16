#!/bin/bash

# Legal Lens Deployment Script
# This script helps deploy the application to various platforms

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
    
    print_success "All dependencies are installed"
}

# Build and test locally
build_and_test() {
    print_status "Building and testing application..."
    
    # Build Docker images
    docker-compose build
    
    # Run tests
    print_status "Running tests..."
    docker-compose run --rm backend pytest
    
    print_success "Build and tests completed successfully"
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
    
    # Deploy
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
    
    # Deploy
    railway up
    
    print_success "Deployed to Railway successfully"
}

# Deploy to Heroku
deploy_heroku() {
    print_status "Deploying to Heroku..."
    
    # Check if Heroku CLI is installed
    if ! command -v heroku &> /dev/null; then
        print_error "Heroku CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if logged in to Heroku
    if ! heroku auth:whoami &> /dev/null; then
        print_warning "Not logged in to Heroku. Please run: heroku login"
        exit 1
    fi
    
    # Create app if it doesn't exist
    if ! heroku apps:info legal-lens &> /dev/null; then
        heroku create legal-lens
    fi
    
    # Deploy
    git push heroku main
    
    print_success "Deployed to Heroku successfully"
}

# Setup environment variables
setup_env() {
    print_status "Setting up environment variables..."
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        cp env.example .env
        print_warning "Created .env file from template. Please edit it with your actual values."
    fi
    
    # Check if required environment variables are set
    if [ -z "$OPENAI_API_KEY" ]; then
        print_warning "OPENAI_API_KEY is not set. Please add it to your .env file or environment."
    fi
    
    if [ -z "$REACT_APP_FIREBASE_API_KEY" ]; then
        print_warning "REACT_APP_FIREBASE_API_KEY is not set. Please add it to your .env file or environment."
    fi
    
    print_success "Environment setup completed"
}

# Main deployment function
main() {
    echo "🚀 Legal Lens Deployment Script"
    echo "================================"
    
    # Parse command line arguments
    case "${1:-help}" in
        "fly")
            check_dependencies
            setup_env
            build_and_test
            deploy_fly
            ;;
        "railway")
            check_dependencies
            setup_env
            build_and_test
            deploy_railway
            ;;
        "heroku")
            check_dependencies
            setup_env
            build_and_test
            deploy_heroku
            ;;
        "local")
            check_dependencies
            setup_env
            build_and_test
            print_status "Starting local development environment..."
            docker-compose up -d
            print_success "Local deployment completed"
            print_status "Frontend: http://localhost:3000"
            print_status "Backend: http://localhost:8000"
            ;;
        "test")
            check_dependencies
            build_and_test
            ;;
        "help"|*)
            echo "Usage: $0 {fly|railway|heroku|local|test|help}"
            echo ""
            echo "Commands:"
            echo "  fly      - Deploy to Fly.io"
            echo "  railway  - Deploy to Railway"
            echo "  heroku   - Deploy to Heroku"
            echo "  local    - Deploy locally with Docker"
            echo "  test     - Run tests only"
            echo "  help     - Show this help message"
            echo ""
            echo "Before deploying, make sure to:"
            echo "1. Set up your environment variables in .env file"
            echo "2. Install the CLI for your chosen platform"
            echo "3. Log in to your chosen platform"
            ;;
    esac
}

# Run main function
main "$@" 
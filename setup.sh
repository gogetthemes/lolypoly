#!/bin/bash
# LolyPoly setup script

set -e

echo "🚀 LolyPoly Setup Script"
echo "========================"

# Check Python version
echo "📍 Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
    source venv/bin/activate
else
    echo "📦 Using existing virtual environment..."
    source venv/bin/activate
fi

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing requirements..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration"
fi

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs

# Initialize database
echo "🗄️  Initializing database..."
python -c "from src.database.database import init_db; init_db()"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your configuration"
echo "2. Start the application: python -m src.main"
echo "3. API will be available at http://localhost:8000"
echo ""
echo "For Docker setup, run: docker-compose up -d"

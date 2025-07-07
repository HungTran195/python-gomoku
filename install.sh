#!/bin/bash

# Python Gomoku Game Installation Script
# This script automates the installation process for Unix-like systems

set -e  # Exit on any error

echo "🚀 Starting Python Gomoku Game Installation..."

# Check if Python 3.11+ is installed
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.11 or higher is required. Found: $python_version"
    echo "Please install Python 3.11+ and try again."
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ Error: pip3 is not installed. Please install pip and try again."
    exit 1
fi

echo "✅ pip3 found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"

# Upgrade pip
echo "🔧 Upgrading pip..."
pip install --upgrade pip
echo "✅ pip upgraded"

# Install requirements
echo "📦 Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "🔧 Creating .env file..."
    cat > .env << EOF
DEBUG=True
DJANGO_SECRET_KEY=your-secret-key-change-this-in-production
ALLOWED_HOSTS_URL=localhost
EOF
    echo "✅ .env file created"
    echo "⚠️  Please edit .env file with your actual configuration"
else
    echo "✅ .env file already exists"
fi

# Run database migrations
echo "🗄️  Running database migrations..."
python manage.py migrate
echo "✅ Database migrations completed"

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput
echo "✅ Static files collected"

echo ""
echo "🎉 Installation completed successfully!"
echo ""
echo "To start the development server:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Then open your browser and go to: http://localhost:8000"
echo ""
echo "Happy gaming! 🎮" 
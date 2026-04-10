#!/bin/bash

echo "🚀 E-Commerce Platform Setup Script"
echo "===================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version found"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt > /dev/null 2>&1
    echo "✓ Dependencies installed"
else
    echo "✗ requirements.txt not found"
    exit 1
fi
echo ""

# Check for .env file
echo "Checking environment configuration..."
if [ ! -f ".env" ]; then
    echo "⚠ .env file not found"
    echo "Copying .env.example to .env..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ .env file created"
        echo "ℹ Please edit .env with your configuration"
    fi
else
    echo "✓ .env file exists"
fi
echo ""

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p logs
mkdir -p media
mkdir -p staticfiles
echo "✓ Directories created"
echo ""

# Run migrations
echo "Running migrations..."
python manage.py migrate > /dev/null 2>&1
echo "✓ Migrations completed"
echo ""

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput > /dev/null 2>&1
echo "✓ Static files collected"
echo ""

# Create sample data
read -p "Do you want to create sample data? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Creating sample data..."
    python manage.py create_sample_data > /dev/null 2>&1
    echo "✓ Sample data created"
    echo ""
    echo "Default admin account:"
    echo "  Email: admin@ecommerce.com"
    echo "  Password: admin123"
fi
echo ""

echo "✓ Setup completed successfully!"
echo ""
echo "To start the development server, run:"
echo "  python manage.py runserver"
echo ""
echo "Admin panel: http://localhost:8000/admin"
echo ""

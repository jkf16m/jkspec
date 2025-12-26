#!/bin/bash
# Setup script for py-snake game

echo "Setting up PY-SNAKE..."
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Python 3 not found! Please install Python 3.7+"; exit 1; }

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate and install dependencies
echo ""
echo "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo ""
echo "Setup complete!"
echo ""
echo "To run the game:"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "Or use the run script:"
echo "  ./run.sh"

#!/bin/bash
# Run script for py-snake game

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup..."
    ./setup.sh
fi

# Activate venv and run game
source venv/bin/activate
python main.py

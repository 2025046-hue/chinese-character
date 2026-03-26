#!/bin/bash

# Chinese Character Learning App Setup Script for Unix/Linux/Mac

echo
echo "=================================="
echo "Chinese Character Learning App Setup"
echo "=================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 is not installed or not in PATH."
    echo "Please install Python 3.11 or higher and try again."
    exit 1
fi

echo "Step 1: Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment."
    exit 1
fi

echo "Virtual environment created successfully."

echo
echo "Step 2: Activating virtual environment..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment."
    exit 1
fi

echo "Virtual environment activated."

echo
echo "Step 3: Upgrading pip..."
python -m pip install --upgrade pip

echo
echo "Step 4: Installing dependencies from requirements.txt..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies."
    exit 1
fi

echo "Dependencies installed successfully."

echo
echo "Step 5: Starting the application..."
streamlit run streamlit_app.py

echo
echo "If you see this message, the app may have closed unexpectedly."
echo "Please check for any error messages above."
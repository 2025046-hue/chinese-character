@echo off
REM Chinese Character Learning App Setup Script for Windows

echo.
echo ================================================
echo Chinese Character Learning App Setup
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.11 or higher and try again.
    pause
    exit /b 1
)

echo Step 1: Creating virtual environment...
python -m venv venv

if errorlevel 1 (
    echo Error: Failed to create virtual environment.
    pause
    exit /b 1
)

echo Virtual environment created successfully.

echo.
echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo Error: Failed to activate virtual environment.
    pause
    exit /b 1
)

echo Virtual environment activated.

echo.
echo Step 3: Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Step 4: Installing dependencies from requirements.txt...
pip install -r requirements.txt

if errorlevel 1 (
    echo Error: Failed to install dependencies.
    pause
    exit /b 1
)

echo Dependencies installed successfully.

echo.
echo Step 5: Starting the application...
streamlit run streamlit_app.py

echo.
echo If you see this message, the app may have closed unexpectedly.
echo Please check for any error messages above.

pause
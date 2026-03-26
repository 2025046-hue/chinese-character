# Chinese Character Learning App Setup Script for PowerShell

Write-Host ""
Write-Host "===============================================" -ForegroundColor Green
Write-Host "Chinese Character Learning App Setup" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} 
catch {
    Write-Host "Error: Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.11 or higher and try again." -ForegroundColor Red
    Read-Host "Press any key to exit"
    exit 1
}

Write-Host ""
Write-Host "Step 1: Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to create virtual environment." -ForegroundColor Red
    Read-Host "Press any key to exit"
    exit 1
}

Write-Host "Virtual environment created successfully." -ForegroundColor Green

Write-Host ""
Write-Host "Step 2: Activating virtual environment..." -ForegroundColor Yellow
& venv\Scripts\Activate.ps1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to activate virtual environment." -ForegroundColor Red
    Read-Host "Press any key to exit"
    exit 1
}

Write-Host "Virtual environment activated." -ForegroundColor Green

Write-Host ""
Write-Host "Step 3: Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

Write-Host ""
Write-Host "Step 4: Installing dependencies from requirements.txt..." -ForegroundColor Yellow
pip install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error: Failed to install dependencies." -ForegroundColor Red
    Read-Host "Press any key to exit"
    exit 1
}

Write-Host "Dependencies installed successfully." -ForegroundColor Green

Write-Host ""
Write-Host "Step 5: Starting the application..." -ForegroundColor Yellow
streamlit run streamlit_app.py

Write-Host ""
Write-Host "If you see this message, the app may have closed unexpectedly." -ForegroundColor Yellow
Write-Host "Please check for any error messages above." -ForegroundColor Yellow

Read-Host "Press any key to exit"
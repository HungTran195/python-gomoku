@echo off
REM Python Gomoku Game Installation Script for Windows
REM This script automates the installation process for Windows systems

echo 🚀 Starting Python Gomoku Game Installation...

REM Check if Python 3.11+ is installed
echo 📋 Checking Python version...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python 3.11+ and try again.
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo ✅ Python version check passed: %python_version%

REM Check if pip is installed
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: pip is not installed. Please install pip and try again.
    pause
    exit /b 1
)

echo ✅ pip found

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 🔧 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat
echo ✅ Virtual environment activated

REM Upgrade pip
echo 🔧 Upgrading pip...
python -m pip install --upgrade pip
echo ✅ pip upgraded

REM Install requirements
echo 📦 Installing dependencies...
pip install -r requirements.txt
echo ✅ Dependencies installed

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo 🔧 Creating .env file...
    (
        echo DEBUG=True
        echo DJANGO_SECRET_KEY=your-secret-key-change-this-in-production
        echo ALLOWED_HOSTS_URL=localhost
    ) > .env
    echo ✅ .env file created
    echo ⚠️  Please edit .env file with your actual configuration
) else (
    echo ✅ .env file already exists
)

REM Run database migrations
echo 🗄️ Running database migrations...
python manage.py migrate
echo ✅ Database migrations completed

REM Collect static files
echo 📁 Collecting static files...
python manage.py collectstatic --noinput
echo ✅ Static files collected

echo.
echo 🎉 Installation completed successfully!
echo.
echo To start the development server:
echo   venv\Scripts\activate
echo   python manage.py runserver
echo.
echo Then open your browser and go to: http://localhost:8000
echo.
echo Happy gaming! 🎮
pause 
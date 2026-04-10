@echo off
echo 🚀 E-Commerce Platform Setup Script
echo ====================================
echo.

echo Checking Python version...
python --version
echo ✓ Python found
echo.

echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment already exists
)
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated
echo.

echo Upgrading pip...
python -m pip install --upgrade pip > nul 2>&1
echo ✓ pip upgraded
echo.

echo Installing dependencies...
if exist "requirements.txt" (
    pip install -r requirements.txt > nul 2>&1
    echo ✓ Dependencies installed
) else (
    echo ✗ requirements.txt not found
    exit /b 1
)
echo.

echo Checking environment configuration...
if not exist ".env" (
    echo ⚠ .env file not found
    if exist ".env.example" (
        copy .env.example .env
        echo ✓ .env file created
        echo ℹ Please edit .env with your configuration
    )
) else (
    echo ✓ .env file exists
)
echo.

echo Creating necessary directories...
if not exist "logs" mkdir logs
if not exist "media" mkdir media
if not exist "staticfiles" mkdir staticfiles
echo ✓ Directories created
echo.

echo Running migrations...
python manage.py migrate > nul 2>&1
echo ✓ Migrations completed
echo.

echo Collecting static files...
python manage.py collectstatic --noinput > nul 2>&1
echo ✓ Static files collected
echo.

set /p CREATE_SAMPLE="Do you want to create sample data? (y/n) "
if /i "%CREATE_SAMPLE%"=="y" (
    echo Creating sample data...
    python manage.py create_sample_data > nul 2>&1
    echo ✓ Sample data created
    echo.
    echo Default admin account:
    echo   Email: admin@ecommerce.com
    echo   Password: admin123
)
echo.

echo ✓ Setup completed successfully!
echo.
echo To start the development server, run:
echo   python manage.py runserver
echo.
echo Admin panel: http://localhost:8000/admin
echo.

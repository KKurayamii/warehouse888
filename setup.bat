@echo off
echo ========================================
echo Smart Sales Analytics - Setup Script
echo ========================================
echo.

:: Check if virtual environment exists
if not exist "venv\" (
    echo [ERROR] Virtual environment not found!
    echo Please run: python -m venv venv
    exit /b 1
)

:: Activate virtual environment
call venv\Scripts\activate.bat

echo [1/6] Installing Python dependencies...
pip install -q -r requirements.txt

echo [2/6] Building Tailwind CSS...
call npm run build:css

echo [3/6] Running Django migrations...
python manage.py migrate

echo [4/6] Creating analytics migrations...
python manage.py makemigrations analytics
python manage.py migrate analytics

echo [5/6] Collecting static files...
python manage.py collectstatic --noinput --clear

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file and add your OpenAI API key
echo 2. Install and start ClickHouse
echo 3. Run: python manage.py setup_clickhouse
echo 4. Run: python manage.py createsuperuser
echo 5. Run: python manage.py runserver
echo.
echo Then visit: http://localhost:8000
echo ========================================
pause

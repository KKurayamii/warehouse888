@echo off
echo ========================================
echo Smart Sales Analytics - Starting Server
echo ========================================
echo.

:: Check if virtual environment exists
if not exist "venv\" (
    echo [ERROR] Virtual environment not found!
    echo Please run setup.bat first
    exit /b 1
)

:: Activate virtual environment
call venv\Scripts\activate.bat

echo Starting Django development server...
echo.
echo Server will be available at:
echo   http://localhost:8000
echo   http://127.0.0.1:8000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python manage.py runserver 0.0.0.0:8000

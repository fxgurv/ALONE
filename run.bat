@echo off
setlocal

:: Check if venv directory exists
IF EXIST venv (
    echo Virtual environment found.
) ELSE (
    echo Creating virtual environment...
    python -m venv venv
    IF ERRORLEVEL 1 (
        echo Failed to create virtual environment. Please make sure Python is installed.
        exit /b 1
    )
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Virtual environment is ready!
echo Type 'deactivate' to exit the virtual environment.
echo.

:: Keep the window open
cmd /k
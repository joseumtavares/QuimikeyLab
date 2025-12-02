@echo off
REM Periodic Table Viewer - Automated Setup Script for Windows

echo ==================================
echo Periodic Table Viewer Setup
echo ==================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from python.org
    pause
    exit /b 1
)

echo [OK] Python found
python --version

REM Check if pip is installed
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip is not installed
    pause
    exit /b 1
)

echo [OK] pip found

REM Create project structure
echo.
echo Creating project structure...
if not exist Elements\json mkdir Elements\json
if not exist templates mkdir templates
if not exist static\css mkdir static\css
if not exist static\js mkdir static\js
if not exist tests mkdir tests

echo [OK] Created directories

REM Create virtual environment
echo.
echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists
    set /p recreate="Do you want to recreate it? (y/n): "
    if /i "%recreate%"=="y" (
        rmdir /s /q venv
        python -m venv venv
        echo [OK] Virtual environment recreated
    )
) else (
    python -m venv venv
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Could not activate virtual environment
    pause
    exit /b 1
)

echo [OK] Virtual environment activated

REM Install dependencies
echo.
echo Installing Python dependencies...
if exist requirements.txt (
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    echo [OK] Dependencies installed
) else (
    echo Error: requirements.txt not found
    pause
    exit /b 1
)

REM Detect serial ports
echo.
echo Detecting serial ports...
python -c "import serial.tools.list_ports; ports = serial.tools.list_ports.comports(); print('\nAvailable serial ports:') if ports else print('\nNo serial ports detected'); [print(f'  {i}. {port.device} - {port.description}') for i, port in enumerate(ports, 1)]"

REM Configure serial port
echo.
echo Configuring serial port...
if exist config.json (
    echo config.json already exists
    set /p update="Do you want to update the serial port? (y/n): "
    if /i not "%update%"=="y" goto skip_config
)

set /p serial_port="Enter your serial port (e.g., COM3, COM4): "
set /p baudrate="Enter baudrate [9600]: "
if "%baudrate%"=="" set baudrate=9600

echo { > config.json
echo   "serial_port": "%serial_port%", >> config.json
echo   "baudrate": %baudrate%, >> config.json
echo   "elements_json_path": "Elements/json/PeriodicTableJSON.json", >> config.json
echo   "web_port": 5000, >> config.json
echo   "auto_start_serial": false >> config.json
echo } >> config.json

echo [OK] config.json created

:skip_config

REM Check for required files
echo.
echo Checking required files...

if not exist app.py (
    echo [WARNING] app.py not found
    echo Please ensure app.py is in the current directory
) else (
    echo [OK] app.py found
)

if not exist templates\index.html (
    echo [WARNING] templates\index.html not found
    echo Please create this file
) else (
    echo [OK] templates\index.html found
)

if not exist Elements\json\PeriodicTableJSON.json (
    echo [WARNING] Elements\json\PeriodicTableJSON.json not found
    echo Please create this file with your element data
) else (
    echo [OK] PeriodicTableJSON.json found
)

REM Create run script
echo.
echo Creating run script...

echo @echo off > run.bat
echo REM Run Periodic Table Viewer >> run.bat
echo. >> run.bat
echo if not exist venv\Scripts\activate.bat ^( >> run.bat
echo     echo Error: Virtual environment not found >> run.bat
echo     echo Run setup.bat first >> run.bat
echo     pause >> run.bat
echo     exit /b 1 >> run.bat
echo ^) >> run.bat
echo. >> run.bat
echo call venv\Scripts\activate.bat >> run.bat
echo python app.py >> run.bat
echo pause >> run.bat

echo [OK] Created run.bat

REM Print summary
echo.
echo ==================================
echo Setup Complete!
echo ==================================
echo.
echo Next steps:
echo.
echo 1. Activate virtual environment:
echo    venv\Scripts\activate
echo.
echo 2. Ensure all files are in place:
echo    - app.py
echo    - templates\index.html
echo    - Elements\json\elements.json
echo.
echo 3. Run the application:
echo    python app.py
echo    or
echo    run.bat
echo.
echo 4. Access the web interface:
echo    http://localhost:5000
echo.
echo For Docker deployment, run:
echo    docker-compose up --build
echo.
pause

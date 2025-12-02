# Complete Setup Guide

## Creating requirements.txt

### Method 1: Manual Creation (Recommended for this project)

Create a file named `requirements.txt` in your project root with this content:

```txt
# Web Framework
flask==3.0.0
Werkzeug==3.0.1

# Serial Communication
pyserial==3.5

# HTTP Requests
requests==2.31.0

# CORS support (optional)
flask-cors==4.0.0
```

### Method 2: Auto-generate from existing environment

If you already have packages installed:

```bash
# Create from current environment (includes EVERYTHING)
pip freeze > requirements.txt

# Or create only for this project (better approach)
pip install pipreqs
pipreqs . --force
```

### Method 3: Using pip-tools (Professional approach)

```bash
# Install pip-tools
pip install pip-tools

# Create requirements.in with just package names
echo "flask
pyserial
requests
flask-cors" > requirements.in

# Generate pinned requirements.txt
pip-compile requirements.in
```

---

## Complete Project Setup from Scratch

### Step 1: Create Project Directory Structure

```bash
# Create main directory
mkdir periodic-table-viewer
cd periodic-table-viewer

# Create subdirectories
mkdir -p Elements/json
mkdir -p templates
mkdir -p static/css
mkdir -p static/js
mkdir -p tests
```

### Step 2: Create All Required Files

#### 2.1 Create requirements.txt
```bash
cat > requirements.txt << 'EOF'
# Web Framework
flask==3.0.0
Werkzeug==3.0.1

# Serial Communication
pyserial==3.5

# HTTP Requests
requests==2.31.0

# CORS support
flask-cors==4.0.0
EOF
```

#### 2.2 Create config.json
```bash
cat > config.json << 'EOF'
{
  "serial_port": "COM3",
  "baudrate": 9600,
  "elements_json_path": "Elements/json/elements.json",
  "web_port": 5000,
  "auto_start_serial": false
}
EOF
```

#### 2.3 Create Dockerfile
```bash
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libgl1-mesa-glx \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p Elements/json templates static

# Expose port
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "app.py"]
EOF
```

#### 2.4 Create docker-compose.yml
```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  periodic-viewer:
    build: 
      context: .
      dockerfile: Dockerfile
    container_name: periodic-table-viewer
    ports:
      - "5000:5000"
    volumes:
      - ./Elements:/app/Elements
      - ./config.json:/app/config.json
      - ./templates:/app/templates
      - ./static:/app/static
    
    # Uncomment and configure for your serial device
    # devices:
    #   - /dev/ttyUSB0:/dev/ttyUSB0
    
    environment:
      - FLASK_ENV=production
      - PYTHONUNBUFFERED=1
    
    restart: unless-stopped
    networks:
      - periodic-network

networks:
  periodic-network:
    driver: bridge
EOF
```

#### 2.5 Create .dockerignore
```bash
cat > .dockerignore << 'EOF'
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
.git/
.gitignore
README.md
.DS_Store
*.swp
*.swo
*~
.vscode/
.idea/
EOF
```

#### 2.6 Create .gitignore
```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Config (if contains sensitive data)
# config.json

# Logs
*.log

# Docker
docker-compose.override.yml
EOF
```

---

## Finding Your Serial Port

### Windows
```cmd
# In Command Prompt or PowerShell
mode

# Or in Python
python -c "import serial.tools.list_ports; [print(p.device) for p in serial.tools.list_ports.comports()]"
```

Common Windows ports: `COM1`, `COM3`, `COM4`, etc.

### macOS
```bash
# List all serial devices
ls /dev/cu.*

# Common patterns:
# /dev/cu.usbserial-*
# /dev/cu.usbmodem*
# /dev/cu.SLAB_USBtoUART

# Or in Python
python3 -c "import serial.tools.list_ports; [print(p.device) for p in serial.tools.list_ports.comports()]"
```

### Linux
```bash
# List USB serial devices
ls /dev/ttyUSB*
ls /dev/ttyACM*

# Or with more details
dmesg | grep tty

# Or in Python
python3 -c "import serial.tools.list_ports; [print(p.device) for p in serial.tools.list_ports.comports()]"
```

---

## Installation & Running

### Option 1: Docker (Recommended)

```bash
# 1. Navigate to project directory
cd periodic-table-viewer

# 2. Configure serial port in docker-compose.yml
# Edit the 'devices:' section with your port

# 3. Build and run
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Option 2: Virtual Environment (Native Python)

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Update config.json with your serial port

# 5. Run application
python app.py

# Access at: http://localhost:5000
```

### Option 3: System-wide Python (Not recommended)

```bash
# Install dependencies globally
pip install -r requirements.txt

# Run application
python app.py
```

---

## Configuring Serial Port in Docker

### For Linux:

1. Find your device:
   ```bash
   ls /dev/ttyUSB*
   # Output: /dev/ttyUSB0
   ```

2. Edit `docker-compose.yml`:
   ```yaml
   devices:
     - /dev/ttyUSB0:/dev/ttyUSB0
   ```

3. Add user to dialout group (if permission issues):
   ```yaml
   group_add:
     - dialout
   ```

### For macOS:

1. Find your device:
   ```bash
   ls /dev/cu.*
   # Output: /dev/cu.usbserial-1420
   ```

2. Edit `docker-compose.yml`:
   ```yaml
   devices:
     - /dev/cu.usbserial-1420:/dev/cu.usbserial-1420
   ```

### For Windows (WSL2):

Windows requires USB/IP passthrough. See: https://docs.microsoft.com/en-us/windows/wsl/connect-usb

Alternatively, run natively without Docker:
```powershell
# Install Python dependencies
pip install -r requirements.txt

# Update config.json with COM port
# "serial_port": "COM3"

# Run directly
python app.py
```

---

## Testing Serial Communication

### Create test script (test_serial.py):

```python
import serial
import json
import time

# Configure your port
PORT = 'COM3'  # or '/dev/ttyUSB0', '/dev/cu.usbserial', etc.
BAUDRATE = 9600

try:
    ser = serial.Serial(PORT, BAUDRATE, timeout=1)
    time.sleep(2)  # Wait for connection
    
    # Test elements
    elements = ['H', 'He', 'C', 'O', 'Au', 'Fe']
    
    for element in elements:
        instruction = {"element": element}
        message = json.dumps(instruction) + '\n'
        
        print(f"Sending: {message.strip()}")
        ser.write(message.encode())
        
        time.sleep(3)  # Wait 3 seconds between elements
    
    ser.close()
    print("Test completed!")
    
except serial.SerialException as e:
    print(f"Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check if port exists")
    print("2. Ensure no other program is using the port")
    print("3. Check port permissions (Linux: add user to dialout group)")
```

Run test:
```bash
python test_serial.py
```

---

## Troubleshooting

### Issue: "Permission denied" on Linux

```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Log out and back in, or:
newgrp dialout

# Verify
groups
```

### Issue: "Port not found"

```bash
# List available ports
python -c "import serial.tools.list_ports; [print(p) for p in serial.tools.list_ports.comports()]"
```

### Issue: Docker container can't access serial port

```bash
# Check device exists on host
ls -l /dev/ttyUSB0

# Run container with privileged mode (temporary test)
docker run --privileged --device=/dev/ttyUSB0 ...
```

### Issue: Flask won't start

```bash
# Check if port 5000 is already in use
# Linux/macOS:
lsof -i :5000

# Windows:
netstat -ano | findstr :5000

# Change port in config.json if needed
```

---

## Development Workflow

### 1. Setup development environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8
```

### 2. Run in development mode

```bash
# Enable Flask debug mode
export FLASK_ENV=development  # Linux/macOS
# or
set FLASK_ENV=development  # Windows

python app.py
```

### 3. Auto-reload on changes

Flask development mode automatically reloads on file changes.

---

## Next Steps

1. ✅ Install Docker or Python environment
2. ✅ Create all project files
3. ✅ Find your serial port device
4. ✅ Update config.json or docker-compose.yml
5. ✅ Run the application
6. ✅ Test with serial communication
7. ✅ Add your element data to Elements/json/elements.json
8. ✅ Add 3D models and images

---

## Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [PySerial Documentation](https://pyserial.readthedocs.io/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Three.js Documentation](https://threejs.org/docs/)

---

**Need help?** Check the main README.md or create an issue!
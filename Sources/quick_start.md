# Quick Start Guide

## 🚀 Fastest Way to Get Started

### For Docker Users (Recommended)

```bash
# 1. Find your serial port
# Linux:
ls /dev/ttyUSB*
# macOS:
ls /dev/cu.*
# Windows:
mode

# 2. Edit docker-compose.yml - uncomment and set your device:
#   devices:
#     - /dev/ttyUSB0:/dev/ttyUSB0  # Your actual port here

# 3. Run!
docker-compose up --build

# 4. Open browser
# http://localhost:5000
```

---

### For Python Users

**Linux/macOS:**
```bash
# 1. Run setup script
chmod +x setup.sh
./setup.sh

# 2. Activate environment (if not already active)
source venv/bin/activate

# 3. Run app
python app.py
# or
./run.sh
```

**Windows:**
```cmd
REM 1. Run setup script
setup.bat

REM 2. Activate environment (if not already active)
venv\Scripts\activate

REM 3. Run app
python app.py
REM or
run.bat
```

---

## 📁 Required Files Checklist

Before running, ensure you have:

```
✓ app.py                           (Main application)
✓ templates/index.html              (Web interface)
✓ Elements/json/elements.json       (Element database)
✓ requirements.txt                  (Python packages)
✓ config.json                       (Configuration)
✓ Dockerfile                        (Docker image)
✓ docker-compose.yml                (Docker orchestration)
```

---

## ⚡ One-Command Setup

### Create everything from scratch:

**Linux/macOS:**
```bash
# Create requirements.txt
cat > requirements.txt << 'EOF'
flask==3.0.0
Werkzeug==3.0.1
pyserial==3.5
requests==2.31.0
flask-cors==4.0.0
EOF

# Install and run
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

**Windows:**
```cmd
REM Create requirements.txt (copy content manually or use echo commands)

REM Install and run
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

---

## 🔌 Serial Port Quick Reference

### Find Your Port

**Windows:**
```cmd
python -c "import serial.tools.list_ports; [print(p.device) for p in serial.tools.list_ports.comports()]"
```

**Linux:**
```bash
ls /dev/ttyUSB* /dev/ttyACM*
# or
dmesg | grep tty
```

**macOS:**
```bash
ls /dev/cu.*
```

### Test Your Port

```python
# test_serial.py
import serial
import json
import time

ser = serial.Serial('COM3', 9600)  # Change to your port
time.sleep(2)

# Send test element
ser.write(b'{"element":"H"}\n')
print("Sent: H")

time.sleep(2)
ser.close()
```

---

## 🧪 Testing the Application

### 1. Test without serial port:

```bash
# Start app
python app.py

# Open browser: http://localhost:5000

# Use the web interface to manually select elements
# (if you implement a selector, or test via API)
```

### 2. Test with serial port:

```bash
# Terminal 1: Run app
python app.py

# Terminal 2: Send test data
python -c "import serial, json, time; s=serial.Serial('COM3',9600); time.sleep(2); s.write(json.dumps({'element':'Au'}).encode()); s.close()"
```

---

## 📊 Sample elements.json

If you don't have an elements.json file yet:

```json
{
  "elements": [
    {
      "symbol": "H",
      "name": "Hydrogen",
      "atomicNumber": 1,
      "atomicMass": "1.008",
      "category": "Nonmetal",
      "phase": "Gas",
      "discoveredBy": "Henry Cavendish (1766)",
      "model3D": null,
      "image2D": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Hydrogen_discharge_tube.jpg/320px-Hydrogen_discharge_tube.jpg"
    },
    {
      "symbol": "Au",
      "name": "Gold",
      "atomicNumber": 79,
      "atomicMass": "196.967",
      "category": "Transition Metal",
      "phase": "Solid",
      "discoveredBy": "Ancient",
      "model3D": null,
      "image2D": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Gold-crystals.jpg/320px-Gold-crystals.jpg"
    }
  ]
}
```

Save this to `Elements/json/elements.json`

---

## 🐛 Common Issues & Fixes

### Issue: "Module not found"
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

### Issue: "Permission denied" (Linux)
```bash
# Solution: Add user to dialout group
sudo usermod -a -G dialout $USER
# Then log out and back in
```

### Issue: "Port already in use"
```bash
# Solution: Change port in config.json
{
  "web_port": 5001  # or any available port
}
```

### Issue: "Serial port not found"
```bash
# Solution: List available ports
python -c "import serial.tools.list_ports; [print(p) for p in serial.tools.list_ports.comports()]"
# Then update config.json with correct port
```

### Issue: Docker can't access serial port
```bash
# Solution: Run with privileged mode (testing only)
docker run --privileged --device=/dev/ttyUSB0 ...

# Or add to docker-compose.yml:
privileged: true
```

---

## 🎯 Quick Commands Reference

### Docker Commands
```bash
docker-compose up --build          # Build and run
docker-compose up -d               # Run in background
docker-compose down                # Stop containers
docker-compose logs -f             # View logs
docker-compose restart             # Restart services
```

### Python Environment
```bash
# Create venv
python -m venv venv

# Activate
source venv/bin/activate           # Linux/macOS
venv\Scripts\activate              # Windows

# Deactivate
deactivate

# Install packages
pip install -r requirements.txt

# Freeze current packages
pip freeze > requirements.txt
```

### Application Commands
```bash
# Run normally
python app.py

# Run with debug
FLASK_ENV=development python app.py

# Run on specific port
# (edit config.json or set environment variable)
```

---

## 📖 More Help

- **Full Setup Guide:** See `SETUP_GUIDE.md`
- **Complete Documentation:** See `README.md`
- **API Documentation:** Available at `/api/docs` when running

---

## 🎉 Success Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Config file created with correct serial port
- [ ] Elements JSON file exists
- [ ] App starts without errors (`python app.py`)
- [ ] Web interface loads (http://localhost:5000)
- [ ] Serial port connects successfully
- [ ] Element displays when instruction received

**All checked?** You're ready to go! 🚀
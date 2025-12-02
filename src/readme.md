# Periodic Table Element Viewer

A cross-platform application that listens to serial port instructions and displays 3D/2D visualizations of periodic table elements.

## Features

- 🔌 **Serial Port Listening**: Receives JSON instructions via serial port (COM/USB)
- 🎨 **3D Visualization**: Displays .glb 3D models with interactive controls
- 🖼️ **2D Fallback**: Shows 2D images when 3D models unavailable
- 📊 **Element Information**: Complete periodic table data display
- 🐳 **Docker Support**: Easy desktop deployment with Docker
- 📱 **Mobile Ready**: Kivy-based mobile application for Android/iOS
- ⚙️ **Configurable**: JSON-based configuration for ports and settings

## Project Structure

```
periodic-table-viewer/
├── app.py                          # Main Flask application
├── mobile_app.py                   # Kivy mobile application
├── requirements.txt                # Python dependencies
├── config.json                     # Configuration file
├── Dockerfile                      # Docker container definition
├── docker-compose.yml              # Docker Compose configuration
├── buildozer.spec                  # Android build configuration
├── templates/
│   └── index.html                  # Web interface template
└── Elements/
    └── json/
        └── elements.json           # Element database
```

## Installation

### Desktop (Docker Method - Recommended)

1. **Clone or create the project structure**

2. **Install Docker and Docker Compose**
   - [Docker Desktop](https://www.docker.com/products/docker-desktop)

3. **Configure serial port** (edit `docker-compose.yml`):
   ```yaml
   devices:
     # Windows (WSL2)
     - /dev/ttyUSB0:/dev/ttyUSB0
     # macOS/Linux
     - /dev/cu.usbserial:/dev/cu.usbserial
   ```

4. **Build and run**:
   ```bash
   docker-compose up --build
   ```

5. **Access the application**:
   - Open browser: `http://localhost:5000`

### Desktop (Native Python Method)

1. **Install Python 3.11+**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Update config.json** with your serial port:
   ```json
   {
     "serial_port": "COM3",  // Windows
     // or "/dev/ttyUSB0"   // Linux
     // or "/dev/cu.usbserial"  // macOS
     "baudrate": 9600,
     "web_port": 5000
   }
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. **Access**: `http://localhost:5000`

### Mobile (Android)

1. **Install Buildozer** (Linux/macOS):
   ```bash
   pip install buildozer
   sudo apt-get install -y \
       python3-pip \
       build-essential \
       git \
       python3 \
       python3-dev \
       ffmpeg \
       libsdl2-dev \
       libsdl2-image-dev \
       libsdl2-mixer-dev \
       libsdl2-ttf-dev \
       libportmidi-dev \
       libswscale-dev \
       libavformat-dev \
       libavcodec-dev \
       zlib1g-dev
   ```

2. **Build APK**:
   ```bash
   buildozer -v android debug
   ```

3. **Install on device**:
   ```bash
   adb install bin/*.apk
   ```

### Mobile (iOS) - Using Kivy-iOS

1. **Install Kivy-iOS tools** (macOS only):
   ```bash
   pip install kivy-ios
   ```

2. **Build for iOS**:
   ```bash
   toolchain build kivy
   toolchain create periodic-table-viewer mobile_app.py
   ```

3. **Open in Xcode and deploy**

## Usage

### Serial Communication

The application expects JSON instructions in this format:

```json
{
  "element": "H"
}
```

**Supported element identifiers**:
- Symbol: `"H"`, `"He"`, `"Au"`, etc.
- Name: `"Hydrogen"`, `"Helium"`, `"Gold"`, etc.

### Sending Test Data

**Arduino Example**:
```cpp
void setup() {
  Serial.begin(9600);
}

void loop() {
  Serial.println("{\"element\":\"Au\"}");
  delay(5000);
}
```

**Python Script**:
```python
import serial
import json
import time

ser = serial.Serial('COM3', 9600)
time.sleep(2)

element = {"element": "Fe"}
ser.write(json.dumps(element).encode())
ser.close()
```

**Manual Testing** (using screen/minicom):
```bash
# Linux/macOS
screen /dev/ttyUSB0 9600
# Then type: {"element":"C"}

# Or use echo
echo '{"element":"O"}' > /dev/ttyUSB0
```

## Element Database Configuration

Edit `Elements/json/elements.json` to add/modify elements:

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
      "model3D": "https://example.com/models/hydrogen.glb",
      "image2D": "https://example.com/images/hydrogen.jpg"
    }
  ]
}
```

### Adding 3D Models

1. Place `.glb` files in a web-accessible location
2. Update the `model3D` URL in `elements.json`
3. The viewer supports:
   - Rotation (left-click + drag)
   - Panning (right-click + drag)
   - Zoom (scroll wheel)

## Configuration Options

### config.json

```json
{
  "serial_port": "COM3",           // Serial port device
  "baudrate": 9600,                 // Serial baud rate
  "elements_json_path": "Elements/json/elements.json",
  "web_port": 5000,                 // Web server port
  "auto_start_serial": false        // Auto-connect on startup
}
```

### Docker Environment Variables

Set in `docker-compose.yml`:
```yaml
environment:
  - FLASK_ENV=production
  - SERIAL_PORT=/dev/ttyUSB0
  - BAUDRATE=9600
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/api/current_element` | GET | Get currently displayed element |
| `/api/element/<symbol>` | GET | Get element by symbol |
| `/api/serial/ports` | GET | List available serial ports |
| `/api/serial/start` | POST | Start serial listener |
| `/api/serial/stop` | POST | Stop serial listener |

## Troubleshooting

### Serial Port Issues

**Permission denied (Linux)**:
```bash
sudo usermod -a -G dialout $USER
# Log out and back in
```

**Port not found**:
```bash
# List ports
python -c "import serial.tools.list_ports; print([p.device for p in serial.tools.list_ports.comports()])"
```

**Docker serial access (Linux)**:
```bash
# Find device group
ls -l /dev/ttyUSB0
# Add to docker-compose.yml
group_add:
  - dialout
```

### 3D Model Not Loading

1. Check browser console for CORS errors
2. Ensure `.glb` URL is publicly accessible
3. Verify model file format (must be `.glb`, not `.gltf`)
4. Test URL directly in browser

### Mobile Build Issues

**Buildozer fails**:
```bash
# Clean build
buildozer android clean
# Try again
buildozer -v android debug
```

**USB permission (Android)**:
- App must request USB permission at runtime
- Add to AndroidManifest.xml if needed

## Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/

# With coverage
pytest --cov=. tests/
```

### Adding New Features

1. Create feature branch
2. Update relevant files (app.py, templates, etc.)
3. Test with both Docker and native methods
4. Update documentation

## Performance Optimization

### 3D Models
- Keep `.glb` files under 10MB
- Use compressed textures
- Optimize polygon count (<100k triangles)

### Serial Buffer
- Application buffers incomplete JSON
- Handles up to 10KB buffer size
- Clears buffer after successful parse

## Security Considerations

1. **Docker**: Container runs as non-root user
2. **Serial Access**: Limit device permissions in production
3. **Web Interface**: No authentication (add if exposing publicly)
4. **CORS**: Configure for production domains

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## Support

- **Issues**: Report bugs via issue tracker
- **Documentation**: See `/docs` folder
- **Examples**: Check `/examples` folder

## Credits

- Three.js for 3D rendering
- Flask for web framework
- Kivy for mobile framework
- PySerial for serial communication

## Version History

- **1.0.0** (2024-12): Initial release
  - Serial port listening
  - 3D/2D visualization
  - Docker deployment
  - Mobile support

---

**Happy Element Viewing! ⚛️**
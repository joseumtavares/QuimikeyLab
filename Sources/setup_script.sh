#!/bin/bash

# Periodic Table Viewer - Automated Setup Script
# For Linux and macOS

set -e  # Exit on error

echo "=================================="
echo "Periodic Table Viewer Setup"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is installed
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}Error: Python 3 is not installed${NC}"
        echo "Please install Python 3.8 or higher"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Found Python: $($PYTHON_CMD --version)${NC}"
}

# Check if pip is installed
check_pip() {
    if ! $PYTHON_CMD -m pip --version &> /dev/null; then
        echo -e "${RED}Error: pip is not installed${NC}"
        echo "Please install pip"
        exit 1
    fi
    echo -e "${GREEN}✓ Found pip${NC}"
}

# Create project structure
create_structure() {
    echo ""
    echo "Creating project structure..."
    
    mkdir -p Elements/json
    mkdir -p templates
    mkdir -p static/css
    mkdir -p static/js
    mkdir -p tests
    
    echo -e "${GREEN}✓ Created directories${NC}"
}

# Create virtual environment
create_venv() {
    echo ""
    echo "Creating virtual environment..."
    
    if [ -d "venv" ]; then
        echo -e "${YELLOW}Virtual environment already exists${NC}"
        read -p "Do you want to recreate it? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf venv
            $PYTHON_CMD -m venv venv
            echo -e "${GREEN}✓ Virtual environment recreated${NC}"
        fi
    else
        $PYTHON_CMD -m venv venv
        echo -e "${GREEN}✓ Virtual environment created${NC}"
    fi
}

# Activate virtual environment
activate_venv() {
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo -e "${GREEN}✓ Virtual environment activated${NC}"
    else
        echo -e "${RED}Error: Could not find venv/bin/activate${NC}"
        exit 1
    fi
}

# Install dependencies
install_dependencies() {
    echo ""
    echo "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip install --upgrade pip
        pip install -r requirements.txt
        echo -e "${GREEN}✓ Dependencies installed${NC}"
    else
        echo -e "${RED}Error: requirements.txt not found${NC}"
        exit 1
    fi
}

# Detect serial ports
detect_serial_ports() {
    echo ""
    echo "Detecting serial ports..."
    
    # Create a temporary Python script
    cat > /tmp/detect_ports.py << 'PYEOF'
import serial.tools.list_ports
ports = serial.tools.list_ports.comports()
if ports:
    print("\nAvailable serial ports:")
    for i, port in enumerate(ports, 1):
        print(f"  {i}. {port.device} - {port.description}")
else:
    print("\nNo serial ports detected")
PYEOF
    
    $PYTHON_CMD /tmp/detect_ports.py
    rm /tmp/detect_ports.py
}

# Configure serial port
configure_serial() {
    echo ""
    echo "Configuring serial port..."
    
    if [ -f "config.json" ]; then
        echo -e "${YELLOW}config.json already exists${NC}"
        read -p "Do you want to update the serial port? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return
        fi
    fi
    
    echo "Enter your serial port (e.g., /dev/ttyUSB0, /dev/cu.usbserial, COM3):"
    read -r serial_port
    
    echo "Enter baudrate [9600]:"
    read -r baudrate
    baudrate=${baudrate:-9600}
    
    cat > config.json << EOF
{
  "serial_port": "$serial_port",
  "baudrate": $baudrate,
  "elements_json_path": "Elements/json/PeriodicTableJSON.json",
  "web_port": 5000,
  "auto_start_serial": false
}
EOF
    
    echo -e "${GREEN}✓ config.json created${NC}"
}

# Check if PeriodicTableJSON.json exists
check_elements_json() {
    if [ ! -f "Elements/json/PeriodicTableJSON.json" ]; then
        echo -e "${YELLOW}Warning: Elements/json/PeriodicTableJSON.json not found${NC}"
        echo "Please create this file with your element data"
    else
        echo -e "${GREEN}✓ PeriodicTableJSON.json found${NC}"
    fi
}

# Check if app.py exists
check_app() {
    if [ ! -f "app.py" ]; then
        echo -e "${RED}Error: app.py not found${NC}"
        echo "Please ensure app.py is in the current directory"
        exit 1
    else
        echo -e "${GREEN}✓ app.py found${NC}"
    fi
}

# Check if templates exist
check_templates() {
    if [ ! -f "templates/index.html" ]; then
        echo -e "${YELLOW}Warning: templates/index.html not found${NC}"
        echo "Please create this file"
    else
        echo -e "${GREEN}✓ templates/index.html found${NC}"
    fi
}

# Add user to dialout group (Linux only)
setup_permissions() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo ""
        echo "Setting up serial port permissions (Linux)..."
        
        if groups | grep -q dialout; then
            echo -e "${GREEN}✓ User already in dialout group${NC}"
        else
            echo "Adding user to dialout group for serial port access..."
            sudo usermod -a -G dialout $USER
            echo -e "${YELLOW}! You need to log out and back in for group changes to take effect${NC}"
        fi
    fi
}

# Create run script
create_run_script() {
    echo ""
    echo "Creating run script..."
    
    cat > run.sh << 'EOF'
#!/bin/bash

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment not found"
    echo "Run ./setup.sh first"
    exit 1
fi

# Run the application
python app.py
EOF
    
    chmod +x run.sh
    echo -e "${GREEN}✓ Created run.sh${NC}"
}

# Print summary
print_summary() {
    echo ""
    echo "=================================="
    echo "Setup Complete!"
    echo "=================================="
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Activate virtual environment:"
    echo "   source venv/bin/activate"
    echo ""
    echo "2. Ensure all files are in place:"
    echo "   - app.py"
    echo "   - templates/index.html"
    echo "   - Elements/json/PeriodicTableJSON.json"
    echo ""
    echo "3. Run the application:"
    echo "   python app.py"
    echo "   or"
    echo "   ./run.sh"
    echo ""
    echo "4. Access the web interface:"
    echo "   http://localhost:5000"
    echo ""
    
    if [[ "$OSTYPE" == "linux-gnu"* ]] && ! groups | grep -q dialout; then
        echo -e "${YELLOW}IMPORTANT: Log out and back in for serial port permissions${NC}"
        echo ""
    fi
    
    echo "For Docker deployment, run:"
    echo "   docker-compose up --build"
    echo ""
}

# Main execution
main() {
    check_python
    check_pip
    create_structure
    create_venv
    activate_venv
    install_dependencies
    detect_serial_ports
    configure_serial
    check_app
    check_templates
    check_elements_json
    setup_permissions
    create_run_script
    print_summary
}

# Run main function
main

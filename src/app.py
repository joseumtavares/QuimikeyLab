"""
Periodic Table Element Viewer
Main application that listens to serial port for element requests

Contribution: Thanks to Bowserinator (https://github.com/Bowserinator/Periodic-Table-JSON) for the Json elements.
"""

import json
import os
import sys
import threading
import time
from pathlib import Path
from typing import Optional, Dict, Any

import serial
import serial.tools.list_ports
from flask import Flask, render_template, jsonify, request
import requests


class ElementDatabase:
    """Handles element data lookup from JSON file"""
    
    def __init__(self, json_path: str = "Elements/json/PeriodicTableJSON.json"):
        self.json_path = json_path
        self.elements = self._load_elements()
    
    def _load_elements(self) -> Dict[str, Any]:
        """Load elements from JSON file"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Elements JSON not found at {self.json_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return {}
    
    def get_element(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get element by symbol (e.g., 'H', 'He', 'Li')"""
        symbol_upper = symbol.upper()
        for element in self.elements.get('elements', []):
            if element.get('symbol', '').upper() == symbol_upper:
                return element
        return None
    
    def get_element_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get element by name (e.g., 'Hydrogen')"""
        name_lower = name.lower()
        for element in self.elements.get('elements', []):
            if element.get('name', '').lower() == name_lower:
                return element
        return None


class SerialPortListener:
    """Listens to serial port for element requests"""
    
    def __init__(self, port: str, baudrate: int = 9600, callback=None):
        self.port = port
        self.baudrate = baudrate
        self.callback = callback
        self.serial_conn = None
        self.running = False
        self.thread = None
    
    @staticmethod
    def list_ports():
        """List all available serial ports"""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def start(self):
        """Start listening to serial port"""
        try:
            self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
            self.running = True
            self.thread = threading.Thread(target=self._listen_loop, daemon=True)
            self.thread.start()
            print(f"Serial port listener started on {self.port}")
            return True
        except serial.SerialException as e:
            print(f"Error opening serial port: {e}")
            return False
    
    def stop(self):
        """Stop listening to serial port"""
        self.running = False
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        if self.thread:
            self.thread.join(timeout=2)
        print("Serial port listener stopped")
    
    def _listen_loop(self):
        """Main listening loop"""
        buffer = ""
        while self.running:
            try:
                if self.serial_conn.in_waiting > 0:
                    data = self.serial_conn.read(self.serial_conn.in_waiting).decode('utf-8', errors='ignore')
                    buffer += data
                    
                    # Look for complete JSON objects
                    if '{' in buffer and '}' in buffer:
                        start = buffer.index('{')
                        end = buffer.index('}', start) + 1
                        json_str = buffer[start:end]
                        buffer = buffer[end:]
                        
                        try:
                            instruction = json.loads(json_str)
                            if self.callback:
                                self.callback(instruction)
                        except json.JSONDecodeError:
                            print(f"Invalid JSON received: {json_str}")
                
                time.sleep(0.1)
            except Exception as e:
                print(f"Error in serial listener: {e}")
                time.sleep(1)


class ElementViewerApp:
    """Main application coordinating serial listening and element display"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.database = ElementDatabase(self.config.get('elements_json_path', 'Elements/json/PeriodicTableJSON.json'))
        self.serial_listener = None
        self.current_element = None
        self.flask_app = self._create_flask_app()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        default_config = {
            "serial_port": "COM3" if sys.platform == "win32" else "/dev/ttyUSB0",
            "baudrate": 9600,
            "elements_json_path": "Elements/json/PeriodicTableJSON.json",
            "web_port": 5000
        }
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                default_config.update(config)
        except FileNotFoundError:
            print(f"Config file not found, using defaults")
            # Save default config
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
        
        return default_config
    
    def _create_flask_app(self) -> Flask:
        """Create Flask web application"""
        app = Flask(__name__)
        
        @app.route('/')
        def index():
            return render_template('index.html')
        
        @app.route('/api/current_element')
        def get_current_element():
            if self.current_element:
                return jsonify(self.current_element)
            return jsonify({"error": "No element loaded"}), 404
        
        @app.route('/api/element/<symbol>')
        def get_element(symbol):
            element = self.database.get_element(symbol)
            if element:
                return jsonify(element)
            return jsonify({"error": "Element not found"}), 404
        
        @app.route('/api/serial/ports')
        def list_serial_ports():
            return jsonify({"ports": SerialPortListener.list_ports()})
        
        @app.route('/api/serial/start', methods=['POST'])
        def start_serial():
            data = request.json
            port = data.get('port', self.config['serial_port'])
            baudrate = data.get('baudrate', self.config['baudrate'])
            
            if self.serial_listener:
                self.serial_listener.stop()
            
            self.serial_listener = SerialPortListener(port, baudrate, self._handle_serial_instruction)
            success = self.serial_listener.start()
            
            return jsonify({"success": success, "port": port})
        
        @app.route('/api/serial/stop', methods=['POST'])
        def stop_serial():
            if self.serial_listener:
                self.serial_listener.stop()
            return jsonify({"success": True})
        
        return app
    
    def _handle_serial_instruction(self, instruction: Dict[str, Any]):
        """Handle instruction received from serial port"""
        print(f"Received instruction: {instruction}")
        
        # Tentar buscar o elemento de diferentes formas (campo 'element' ou 'symbol')
        element_symbol = instruction.get('element') or instruction.get('symbol')
        
        if not element_symbol:
            print("No element specified in instruction")
            return
        
        # Lookup element
        element = self.database.get_element(element_symbol)
        if not element:
            element = self.database.get_element_by_name(element_symbol)
        
        if element:
            print(f"Element found: {element.get('name')}")
            self.current_element = element
        else:
            print(f"Element not found: {element_symbol}")
            self.current_element = None
    
    def run(self):
        """Run the application"""
        # Start serial listener
        if self.config.get('auto_start_serial', True):
            self.serial_listener = SerialPortListener(
                self.config['serial_port'],
                self.config['baudrate'],
                self._handle_serial_instruction
            )
            self.serial_listener.start()
        
        # Start Flask web server
        print(f"Starting web server on port {self.config['web_port']}")
        self.flask_app.run(
            host='0.0.0.0',
            port=self.config['web_port'],
            debug=False
        )


if __name__ == "__main__":
    app = ElementViewerApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
        if app.serial_listener:
            app.serial_listener.stop()

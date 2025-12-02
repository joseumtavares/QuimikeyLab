"""
Mobile Periodic Table Element Viewer
Built with Kivy for cross-platform mobile deployment
"""

import json
import threading
from pathlib import Path
from typing import Optional, Dict, Any

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image as KivyImage
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

# For serial communication on mobile
try:
    from jnius import autoclass, cast
    ANDROID = True
    # Android USB Serial
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    UsbManager = autoclass('android.hardware.usb.UsbManager')
    Context = autoclass('android.content.Context')
except ImportError:
    ANDROID = False
    import serial
    import serial.tools.list_ports


class ElementDatabase:
    """Handles element data lookup from JSON file"""
    
    def __init__(self, json_path: str = "Elements/json/elements.json"):
        self.json_path = json_path
        self.elements = self._load_elements()
    
    def _load_elements(self) -> Dict[str, Any]:
        """Load elements from JSON file"""
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading elements: {e}")
            return {"elements": []}
    
    def get_element(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get element by symbol"""
        symbol_upper = symbol.upper()
        for element in self.elements.get('elements', []):
            if element.get('symbol', '').upper() == symbol_upper:
                return element
        return None
    
    def get_all_elements(self):
        """Get all elements"""
        return self.elements.get('elements', [])


class SerialHandler:
    """Handles serial communication - cross-platform"""
    
    def __init__(self, callback=None):
        self.callback = callback
        self.serial_conn = None
        self.running = False
        self.thread = None
    
    @staticmethod
    def list_ports():
        """List available serial ports"""
        if ANDROID:
            # Android USB device listing
            try:
                context = PythonActivity.mActivity
                usb_manager = cast('android.hardware.usb.UsbManager',
                                  context.getSystemService(Context.USB_SERVICE))
                device_list = usb_manager.getDeviceList()
                return [str(device) for device in device_list.values()]
            except Exception as e:
                print(f"Error listing Android USB devices: {e}")
                return []
        else:
            # Desktop serial ports
            ports = serial.tools.list_ports.comports()
            return [port.device for port in ports]
    
    def connect(self, port: str, baudrate: int = 9600):
        """Connect to serial port"""
        try:
            if ANDROID:
                # Android USB serial implementation would go here
                print(f"Android USB connection to {port} not yet implemented")
                return False
            else:
                self.serial_conn = serial.Serial(port, baudrate, timeout=1)
                self.running = True
                self.thread = threading.Thread(target=self._listen_loop, daemon=True)
                self.thread.start()
                return True
        except Exception as e:
            print(f"Error connecting to serial port: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from serial port"""
        self.running = False
        if self.serial_conn and hasattr(self.serial_conn, 'is_open') and self.serial_conn.is_open:
            self.serial_conn.close()
        if self.thread:
            self.thread.join(timeout=2)
    
    def _listen_loop(self):
        """Listen for serial data"""
        buffer = ""
        while self.running:
            try:
                if self.serial_conn.in_waiting > 0:
                    data = self.serial_conn.read(self.serial_conn.in_waiting).decode('utf-8', errors='ignore')
                    buffer += data
                    
                    if '{' in buffer and '}' in buffer:
                        start = buffer.index('{')
                        end = buffer.index('}', start) + 1
                        json_str = buffer[start:end]
                        buffer = buffer[end:]
                        
                        try:
                            instruction = json.loads(json_str)
                            if self.callback:
                                Clock.schedule_once(lambda dt: self.callback(instruction), 0)
                        except json.JSONDecodeError:
                            print(f"Invalid JSON: {json_str}")
            except Exception as e:
                print(f"Error in serial listener: {e}")


class ElementInfoPanel(BoxLayout):
    """Panel displaying element information"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        with self.canvas.before:
            Color(0.95, 0.95, 0.97, 1)
            self.rect = Rectangle(pos=self.pos, size=self.size)
        
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        # Element symbol (large)
        self.symbol_label = Label(
            text='-',
            font_size='80sp',
            color=(0.4, 0.49, 0.92, 1),
            size_hint_y=0.3,
            bold=True
        )
        self.add_widget(self.symbol_label)
        
        # Element name
        self.name_label = Label(
            text='-',
            font_size='32sp',
            color=(0.2, 0.2, 0.2, 1),
            size_hint_y=0.15
        )
        self.add_widget(self.name_label)
        
        # Properties scroll view
        self.properties_layout = GridLayout(
            cols=1,
            spacing=5,
            size_hint_y=None
        )
        self.properties_layout.bind(minimum_height=self.properties_layout.setter('height'))
        
        scroll = ScrollView(size_hint_y=0.55)
        scroll.add_widget(self.properties_layout)
        self.add_widget(scroll)
    
    def _update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
    
    def update_element(self, element: Dict[str, Any]):
        """Update displayed element information"""
        self.symbol_label.text = element.get('symbol', '-')
        self.name_label.text = element.get('name', '-')
        
        # Clear existing properties
        self.properties_layout.clear_widgets()
        
        # Add property rows
        properties = [
            ('Atomic Number', element.get('atomicNumber', '-')),
            ('Atomic Mass', element.get('atomicMass', '-')),
            ('Category', element.get('category', '-')),
            ('Phase', element.get('phase', '-')),
            ('Discovered By', element.get('discoveredBy', '-'))
        ]
        
        for label, value in properties:
            prop_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
            prop_box.add_widget(Label(
                text=f"[b]{label}:[/b]",
                markup=True,
                size_hint_x=0.5,
                color=(0.4, 0.4, 0.4, 1)
            ))
            prop_box.add_widget(Label(
                text=str(value),
                size_hint_x=0.5,
                color=(0.2, 0.2, 0.2, 1)
            ))
            self.properties_layout.add_widget(prop_box)


class PeriodicTableMobileApp(App):
    """Main mobile application"""
    
    def build(self):
        Window.clearcolor = (0.4, 0.49, 0.92, 1)
        
        self.database = ElementDatabase()
        self.serial_handler = SerialHandler(callback=self.on_serial_data)
        self.current_element = None
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=5, spacing=5)
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=0.08)
        header.add_widget(Label(
            text='⚛️ Periodic Table Viewer',
            font_size='24sp',
            bold=True,
            color=(1, 1, 1, 1)
        ))
        main_layout.add_widget(header)
        
        # Serial controls
        controls = BoxLayout(orientation='horizontal', size_hint_y=0.08, spacing=5)
        
        self.port_spinner = Spinner(
            text='Select Port',
            values=SerialHandler.list_ports(),
            size_hint_x=0.5
        )
        controls.add_widget(self.port_spinner)
        
        self.connect_btn = Button(
            text='Connect',
            size_hint_x=0.25,
            background_color=(0.16, 0.65, 0.27, 1)
        )
        self.connect_btn.bind(on_press=self.connect_serial)
        controls.add_widget(self.connect_btn)
        
        self.disconnect_btn = Button(
            text='Disconnect',
            size_hint_x=0.25,
            background_color=(0.86, 0.20, 0.27, 1)
        )
        self.disconnect_btn.bind(on_press=self.disconnect_serial)
        controls.add_widget(self.disconnect_btn)
        
        main_layout.add_widget(controls)
        
        # Content area
        content = BoxLayout(orientation='horizontal', size_hint_y=0.84, spacing=5)
        
        # Visualization area (left side)
        viz_layout = BoxLayout(orientation='vertical', size_hint_x=0.5)
        
        self.image_widget = KivyImage(
            source='',
            size_hint=(1, 0.8)
        )
        viz_layout.add_widget(self.image_widget)
        
        self.status_label = Label(
            text='Waiting for element data...',
            size_hint=(1, 0.2),
            color=(1, 1, 1, 1)
        )
        viz_layout.add_widget(self.status_label)
        
        content.add_widget(viz_layout)
        
        # Info panel (right side)
        self.info_panel = ElementInfoPanel(size_hint_x=0.5)
        content.add_widget(self.info_panel)
        
        main_layout.add_widget(content)
        
        # Refresh ports button
        refresh_btn = Button(
            text='Refresh Ports',
            size_hint_y=0.05,
            background_color=(0.5, 0.5, 0.5, 1)
        )
        refresh_btn.bind(on_press=self.refresh_ports)
        main_layout.add_widget(refresh_btn)
        
        return main_layout
    
    def refresh_ports(self, instance):
        """Refresh available serial ports"""
        self.port_spinner.values = SerialHandler.list_ports()
    
    def connect_serial(self, instance):
        """Connect to selected serial port"""
        port = self.port_spinner.text
        if port == 'Select Port':
            self.status_label.text = 'Please select a port first'
            return
        
        if self.serial_handler.connect(port):
            self.status_label.text = f'Connected to {port}'
            self.connect_btn.disabled = True
            self.disconnect_btn.disabled = False
        else:
            self.status_label.text = 'Failed to connect'
    
    def disconnect_serial(self, instance):
        """Disconnect from serial port"""
        self.serial_handler.disconnect()
        self.status_label.text = 'Disconnected'
        self.connect_btn.disabled = False
        self.disconnect_btn.disabled = True
    
    def on_serial_data(self, instruction: Dict[str, Any]):
        """Handle received serial instruction"""
        element_symbol = instruction.get('element')
        if not element_symbol:
            return
        
        element = self.database.get_element(element_symbol)
        if element:
            self.display_element(element)
        else:
            self.status_label.text = f'Element not found: {element_symbol}'
    
    def display_element(self, element: Dict[str, Any]):
        """Display element information"""
        self.current_element = element
        self.info_panel.update_element(element)
        
        # Load image
        image_url = element.get('image2D') or element.get('model3D')
        if image_url:
            self.status_label.text = f'Displaying {element.get("name")}'
            # Note: For production, you'd need to download and cache images
            # self.image_widget.source = image_url
        else:
            self.status_label.text = f'{element.get("name")} - No visualization'
    
    def on_stop(self):
        """Cleanup on app close"""
        self.serial_handler.disconnect()


if __name__ == '__main__':
    PeriodicTableMobileApp().run()

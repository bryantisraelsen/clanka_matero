# Clanka Matero - Hot Water Dispenser Control

Clanka Matero is a Raspberry Pi-based hot water dispenser control system. It provides a web interface to monitor and control water heating and dispensing operations, featuring automatic temperature maintenance, manual dispensing controls, and real-time status monitoring.

## Features

- **Real-time Monitoring**: Displays current temperature, target temperature, water level, heating status, and dispensing status
- **Automatic Heating Control**: Maintains water at a specified temperature with configurable hysteresis
- **Manual Dispensing**: Dispenses hot water for a set duration with enable/disable controls
- **Physical Button Controls**: Hardware buttons for timer-based dispensing and hold-to-dispense functionality
- **Web Interface**: Responsive web UI with dark/light theme support
- **REST API**: Full API for integration with other systems
- **Configuration Persistence**: Settings saved to JSON files for reliability

## Hardware Requirements

- Raspberry Pi (any model with GPIO pins)
- DS18B20 digital temperature sensor
- Water level sensor (normally open switch)
- Relay module for heater control
- Solenoid valve for water dispensing
- Push buttons (2x) for physical controls
- Appropriate power supplies and wiring

### GPIO Pin Mapping

| Component | GPIO Pin | BCM Number |
|-----------|----------|------------|
| Water Level Sensor | GPIO 5 | 5 |
| Heater Relay | GPIO 6 | 6 |
| Solenoid Valve | GPIO 22 | 22 |
| Timer Button | GPIO 17 | 17 |
| Hold Button | GPIO 27 | 27 |
| DS18B20 Data | GPIO 4 | 4 (1-Wire) |

## Software Requirements

- Python 3.7+
- Raspberry Pi OS (or any Linux with GPIO support)
- 1-Wire interface enabled for temperature sensor

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd clanka_matero
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Enable 1-Wire interface** (if not already enabled):
   ```bash
   sudo raspi-config
   # Navigate to Interfacing Options > 1-Wire > Enable
   sudo reboot
   ```

5. **Connect hardware** according to the GPIO pin mapping above.

## Running the Server

1. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

2. **Run the server**:
   ```bash
   ./start_server.sh
   ```

   Or manually:
   ```bash
   export FLASK_APP=clanka_matero
   flask run --host=0.0.0.0 --port=5000
   ```

3. **Access the web interface**:
   Open a web browser and navigate to `http://<raspberry-pi-ip>:5000`

The server will start in development mode. For production deployment, consider using a WSGI server like Gunicorn.

## Using the Webapp

### Status Section

The status section displays real-time information about the dispenser:

- **Current Temperature**: Current water temperature in °F
- **Desired Temperature**: Target temperature setting
- **Heater**: ON/OFF status of the heating element
- **Water Level**: OK/LOW status based on water sensor
- **Auto Heat**: ON/OFF status of automatic heating control
- **Dispense Time**: Configured dispensing duration in seconds
- **Dispense Enabled**: Whether dispensing is allowed
- **Dispensing**: Current dispensing status

### Controls Section

#### Temperature Control
- Enter desired temperature (70-212°F)
- Click "Set" to update the target temperature

#### Dispense Time
- Enter dispense duration (1-10 seconds recommended)
- Click "Set" to update the dispense time

#### Auto Heat Toggle
- Click to start/stop automatic temperature maintenance
- When ON, the system will heat water to maintain the target temperature

#### Dispense Enable
- Click to enable/disable dispensing functionality
- Must be enabled to dispense water via web or physical buttons

#### Dispense Button
- Click to manually dispense water for the configured duration
- Only works when dispensing is enabled

### Theme Toggle

Click the theme button (🌙/☀️) in the header to switch between dark and light themes. Your preference is saved locally.

## Configuration

Configuration is stored in JSON files:

- `.config/config.json`: Stores target temperature and dispense time
- `.status/sys_status.json`: Stores current system status (auto-generated)

Default configuration:
```json
{
  "target_temp_f": 150.0,
  "dispense_time_sec": 2.0
}
```

## Physical Controls

- **Timer Button (GPIO 17)**: Press to dispense water for the configured duration
- **Hold Button (GPIO 27)**: Hold to dispense water continuously while pressed (only when dispensing is enabled)

## API Reference

The system provides a REST API for programmatic control:

### Status Endpoints

- `GET /api/status`: Get all status information
- `GET /api/auto_heat_status`: Get auto heat running status
- `GET /api/water_ok_status`: Get water level status
- `GET /api/current_temp_f_status`: Get current temperature
- `GET /api/target_temp_f_status`: Get target temperature
- `GET /api/dispense_time_status`: Get dispense time
- `GET /api/heating_status`: Get heating status
- `GET /api/dispense_enable_status`: Get dispense enabled status
- `GET /api/dispensing_status`: Get dispensing status

### Control Endpoints

- `POST /api/set_temp`: Set target temperature
  - Body: `{"temp_f": 150.0}`
- `POST /api/set_dispense`: Set dispense time
  - Body: `{"seconds": 2.0}`
- `POST /api/start_auto`: Start automatic heating
- `POST /api/stop_auto`: Stop automatic heating
- `POST /api/dispense`: Trigger dispensing
- `POST /api/dispense_enable`: Enable dispensing
- `POST /api/dispense_disable`: Disable dispensing

## Troubleshooting

### Temperature Sensor Not Found
- Ensure DS18B20 is properly connected to GPIO 4
- Verify 1-Wire interface is enabled in raspi-config
- Check sensor power and data connections

### GPIO Libraries Not Available
- Install RPi.GPIO: `pip install RPi.GPIO`
- Install gpiozero: `pip install gpiozero`
- Run on actual Raspberry Pi hardware

### Web Interface Not Loading
- Check that Flask is running on the correct host/port
- Verify firewall settings allow access to port 5000
- Check browser console for JavaScript errors

### Heating Not Working
- Verify relay connections and power supply
- Check GPIO pin assignments
- Ensure water level sensor is functioning

### Dispensing Not Working
- Check solenoid valve connections
- Verify dispense is enabled in the web interface
- Test physical buttons for functionality

## Development

For development and testing without hardware:

- The system includes mock GPIO implementations when hardware libraries are unavailable
- Run on any system with Python 3.7+
- Use the web interface to test functionality
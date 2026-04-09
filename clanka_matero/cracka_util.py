# cracka_util.py

import glob
import time
import threading
import json
import os
from logging import getLogger
logger = getLogger("application")
try:
    from gpiozero import OutputDevice, Button, LED, DigitalInputDevice
except ImportError:
    logger.warning("GPIO libraries not found, using mock implementations. This code will not control real hardware.")
    # Mock GPIO and gpiozero for non-Raspberry Pi environments

    class OutputDevice:
        def __init__(self, pin):
            self.pin = pin

        def on(self):
            print(f"OutputDevice on pin {self.pin} turned ON")

        def off(self):
            print(f"OutputDevice on pin {self.pin} turned OFF")

    class Button:
        def __init__(self, pin, pull_up=True, bounce_time=0.05):
            self.pin = pin
            self.when_pressed = None
            self.when_released = None

    class LED(OutputDevice):
        pass

    class DigitalInputDevice:
        def __init__(self, pin, pull_up=True):
            self.pin = pin
            self.pull_up = pull_up

        @property
        def value(self):
            return True  # Always return water level OK for testing


class CrackaController:
    def __init__(self):
        # ---- Files ----
        self.CONFIG_FILE = ".config/config.json"
        self.STATUS_FILE = ".status/sys_status.json"

        os.makedirs(".config", exist_ok=True)
        os.makedirs(".status", exist_ok=True)

        # ---- GPIO ----
        self.WATER_PIN = 5
        self.water_sensor = DigitalInputDevice(self.WATER_PIN, pull_up=True)

        self.heater = OutputDevice(6)

        # Valve
        self.valve = LED(22)

        # Buttons
        self.button_hold = Button(17, pull_up=True, bounce_time=0.05)
        self.button_timer = Button(27, pull_up=True, bounce_time=0.05)

        # ---- Temp sensor ----
        base_dir = '/sys/bus/w1/devices/'
        device_folder_glob = glob.glob(base_dir + '28*')
        if not device_folder_glob or len(device_folder_glob) == 0:
            logger.error("No temperature sensor found! Make sure the DS18B20 is connected properly.")
            device_folder = ""
        else:
            device_folder = glob.glob(base_dir + '28*')[0]
        self.device_file = device_folder + '/w1_slave'

        # ---- State ----
        self.heater_on = False
        self.auto_thread = None
        self.auto_running = False

        # Dispense control
        self.dispensing = False
        self.dispense_enabled = False
        self.dispense_lock = threading.Lock()

        self._ensure_default_config()
        self._setup_button_handlers()

    # ---------------- BUTTON SETUP ----------------

    def _setup_button_handlers(self):
        self.button_timer.when_pressed = self.start_dispense
        self.button_hold.when_pressed = self._hold_pressed
        self.button_hold.when_released = self._hold_released

    def _hold_pressed(self):
        if not self.dispense_enabled:
            return

        self.valve.on()

    def _hold_released(self):
        self.valve.off()

    # ---------------- CONFIG ----------------

    def _ensure_default_config(self):
        if not os.path.exists(self.CONFIG_FILE):
            self._write_config({
                "target_temp_f": 150.0,
                "dispense_time_sec": 2.0
            })

    def _read_config(self):
        try:
            with open(self.CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return {
                "target_temp_f": 150.0,
                "dispense_time_sec": 2.0
            }

    def _write_config(self, data):
        tmp = self.CONFIG_FILE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, self.CONFIG_FILE)

    # ---------------- BASIC GETTERS ----------------

    def get_water_level_ok(self):
        # print(self.water_sensor.value)
        return self.water_sensor.value == 0

    def get_curr_temperature(self):
        try:
            with open(self.device_file, 'r') as f:
                lines = f.readlines()

            if lines[0].strip()[-3:] != 'YES':
                return None

            temp_pos = lines[1].find('t=')
            temp_c = float(lines[1][temp_pos+2:]) / 1000.0
            return temp_c * 9.0 / 5.0 + 32
        except:
            return None

    def get_specified_temperature(self):
        return self._read_config().get("target_temp_f")

    def set_specified_temperature(self, temp_f):
        config = self._read_config()
        config["target_temp_f"] = float(temp_f)
        self._write_config(config)

    def set_dispense_time(self, seconds):
        config = self._read_config()
        config["dispense_time_sec"] = float(seconds)
        self._write_config(config)

    def get_dispense_time(self):
        return self._read_config().get("dispense_time_sec")

    def get_if_currently_heating(self):
        return self.heater_on

    def get_if_auto_heat_running(self):
        return self.auto_running

    def get_if_dispensing(self):
        return self.dispensing

    def get_if_dispense_enabled(self):
        return self.dispense_enabled

    # ---------------- DISPENSE ENABLE CONTROL ----------------

    def enable_dispense(self):
        self.dispense_enabled = True

    def disable_dispense(self):
        self.dispense_enabled = False
        self.valve.off()

    # ---------------- STATUS ----------------

    def _write_status(self, data):
        tmp = self.STATUS_FILE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, self.STATUS_FILE)

    # ---------------- AUTO HEAT ----------------

    def _auto_loop(self):
        hysteresis_f = 1.0

        while self.auto_running:
            config = self._read_config()
            target_temp_f = config["target_temp_f"]

            water_ok = self.get_water_level_ok()

            if not water_ok:
                self.heater.off()
                self.heater_on = False

                self._write_status({
                    "water_low": True,
                    "target_temp_f": target_temp_f
                })

                time.sleep(1)
                continue

            curr_temp = self.get_curr_temperature()

            if curr_temp is None:
                time.sleep(1)
                continue

            if (not self.heater_on) and curr_temp < (target_temp_f - hysteresis_f):
                self.heater.on()
                self.heater_on = True

            elif self.heater_on and curr_temp >= target_temp_f:
                self.heater.off()
                self.heater_on = False

            self._write_status({
                "water_low": False,
                "heater_on": self.heater_on,
                "current_temp_f": round(curr_temp, 2),
                "target_temp_f": target_temp_f
            })

            time.sleep(1)
        self.heater.off()
        self.heater_on = False

    def start_automatic_heat_control(self):
        if self.auto_running:
            return

        self.auto_running = True
        self.auto_thread = threading.Thread(target=self._auto_loop, daemon=True)
        self.auto_thread.start()

    def stop_automatic_heat_control(self):
        self.auto_running = False
        self.heater.off()
        self.heater_on = False

    def get_if_auto_heat_running(self):
        return self.auto_running

# ---------------- DISPENSING ----------------

    def start_dispense(self):
        if not self.dispense_enabled:
            return False

        if self.dispensing:
            return False

        def _dispense():
            with self.dispense_lock:
                self.dispensing = True

                config = self._read_config()
                duration = config.get("dispense_time_sec", 2.0)

                try:
                    self.valve.on()
                    time.sleep(duration)
                    self.valve.off()
                finally:
                    self.dispensing = False

        threading.Thread(target=_dispense, daemon=True).start()
        return True

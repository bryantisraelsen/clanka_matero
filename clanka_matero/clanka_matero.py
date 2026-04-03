import glob
import time
import sys
import threading
from gpiozero import Button, LED, OutputDevice
from signal import pause
import RPi.GPIO as GPIO

# ---- Arguments ----
duration = 3
target_temp_f = 100

if len(sys.argv) >= 2:
    duration = float(sys.argv[1])

if len(sys.argv) >= 3:
    target_temp_f = float(sys.argv[2])

print("Timer duration:", duration)
print("Target temperature:", target_temp_f, "F")

target_temp_c = (target_temp_f - 32) * 5.0 / 9.0

# ---- Temperature sensor setup ----
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

# ---- GPIO setup ----
GPIO.setmode(GPIO.BCM)

WATER_PIN = 5
GPIO.setup(WATER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ---- GPIO devices ----
button_hold = Button(17, pull_up=True, bounce_time=0.05)
button_timer = Button(27, pull_up=True, bounce_time=0.05)
led = LED(22)

# Heater output (GPIO 6)
heater = OutputDevice(6)

timer_active = False
temp_reached = False

# ---- Water Level Check ----
def water_ok():
    return GPIO.input(WATER_PIN) == 1  # HIGH = water present

# ---- Temperature Reading ----
def read_temp():
    with open(device_file, 'r') as f:
        lines = f.readlines()

    if lines[0].strip()[-3:] != 'YES':
        return None

    temp_pos = lines[1].find('t=')
    temp_c = float(lines[1][temp_pos+2:]) / 1000.0
    return temp_c


def temperature_monitor():
    hysteresis_f = 1.0
    hysteresis_c = hysteresis_f * 5.0 / 9.0

    heater_on = False

    while True:

        # 🚨 Always check water level first
        if not water_ok():
            if heater_on:
                print("⚠️ Water level LOW - heater OFF")
            heater.off()
            heater_on = False
            time.sleep(1)
            continue

        temp_c = read_temp()

        if temp_c is None:
            time.sleep(1)
            continue

        temp_f = temp_c * 9.0 / 5.0 + 32
        print(f"Temp: {temp_f:.2f} F")

        # ---- Thermostat logic ----
        if not heater_on and temp_c < (target_temp_c - hysteresis_c):
            print("Heater ON")
            heater.on()
            heater_on = True

        elif heater_on and temp_c >= target_temp_c:
            print("Heater OFF (target reached)")
            heater.off()
            heater_on = False

        time.sleep(1)


# ---- Button Logic ----
def hold_pressed():
    led.on()

def hold_released():
    if not timer_active:
        led.off()

def timed_led():
    global timer_active
    timer_active = True

    led.on()
    time.sleep(duration)

    timer_active = False

    if not button_hold.is_pressed:
        led.off()

def start_timer():
    threading.Thread(target=timed_led, daemon=True).start()

# ---- Button bindings ----
button_hold.when_pressed = hold_pressed
button_hold.when_released = hold_released
button_timer.when_pressed = start_timer

# ---- Start temperature thread ----
threading.Thread(target=temperature_monitor, daemon=True).start()

pause()

# backend.py

from flask import Flask, request, jsonify
from cracka_util import CrackaController

app = Flask(__name__)
ctrl = CrackaController()

# -------- GET endpoints --------

@app.route("/status")
def status():
    return jsonify({
        "water_ok": ctrl.get_water_level_ok(),
        "current_temp_f": ctrl.get_curr_temperature(),
        "target_temp_f": ctrl.get_specified_temperature(),
        "dispense_time_sec": ctrl.get_dispense_time(),
        "heating": ctrl.get_if_currently_heating(),
        "auto_heat_running": ctrl.get_if_auto_heat_running()
    })

@app.route("/auto_heat_status")
def auto_status():
    return jsonify({
        "auto_heat_running": ctrl.get_if_auto_heat_running()
    })

@app.route("/water_ok_status")
def water_ok_status():
    return jsonify({
        "water_ok": ctrl.get_water_level_ok()
    })

@app.route("/current_temp_f_status")
def current_temp_f_status():
    return jsonify({
        "current_temp_f": ctrl.get_curr_temperature()
    })

@app.route("/target_temp_f_status")
def target_temp_f_status():
    return jsonify({
        "target_temp_f": ctrl.get_specified_temperature()
    })

@app.route("/dispense_time_status")
def dispense_time_status():
    return jsonify({
        "dispense_time_sec": ctrl.get_dispense_time()
    })

@app.route("/heating_status")
def heating_status():
    return jsonify({
        "heating": ctrl.get_if_currently_heating()
    })

# -------- SET endpoints --------

@app.route("/set_temp", methods=["POST"])
def set_temp():
    temp = request.json.get("temp_f")
    ctrl.set_specified_temperature(temp)
    return jsonify({"ok": True})

@app.route("/set_dispense", methods=["POST"])
def set_dispense():
    t = request.json.get("seconds")
    ctrl.set_dispense_time(t)
    return jsonify({"ok": True})

# -------- CONTROL --------

@app.route("/start_auto", methods=["POST"])
def start_auto():
    ctrl.start_automatic_heat_control()
    return jsonify({"ok": True})

@app.route("/stop_auto", methods=["POST"])
def stop_auto():
    ctrl.stop_automatic_heat_control()
    return jsonify({"ok": True})

# -------- Run --------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

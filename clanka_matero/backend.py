# backend.py

from flask import Blueprint, request, jsonify
from .cracka_util import CrackaController


ctrl = CrackaController()
bp = Blueprint('backend', __name__, url_prefix='/api')
# -------- GET endpoints --------

@bp.route("/status")
def status():
    return jsonify({
        "water_ok": ctrl.get_water_level_ok(),
        "current_temp_f": ctrl.get_curr_temperature(),
        "target_temp_f": ctrl.get_specified_temperature(),
        "dispense_time_sec": ctrl.get_dispense_time(),
        "heating": ctrl.get_if_currently_heating(),
        "auto_heat_running": ctrl.get_if_auto_heat_running(),
        "dispense_enabled": ctrl.get_if_dispense_enabled(),
        "dispensing": ctrl.get_if_dispensing()
    })

@bp.route("/auto_heat_status")
def auto_status():
    return jsonify({
        "auto_heat_running": ctrl.get_if_auto_heat_running()
    })

@bp.route("/water_ok_status")
def water_ok_status():
    return jsonify({
        "water_ok": ctrl.get_water_level_ok()
    })

@bp.route("/current_temp_f_status")
def current_temp_f_status():
    return jsonify({
        "current_temp_f": ctrl.get_curr_temperature()
    })

@bp.route("/target_temp_f_status")
def target_temp_f_status():
    return jsonify({
        "target_temp_f": ctrl.get_specified_temperature()
    })

@bp.route("/dispense_time_status")
def dispense_time_status():
    return jsonify({
        "dispense_time_sec": ctrl.get_dispense_time()
    })

@bp.route("/heating_status")
def heating_status():
    return jsonify({
        "heating": ctrl.get_if_currently_heating()
    })

@bp.route("/dispense_enable_status")
def dispense_enabled_status():
    return jsonify({
        "dispense_enabled": ctrl.get_if_dispense_enabled()
    })

@bp.route("/dispensing_status")
def dispensing_status():
    return jsonify({
        "dispensing": ctrl.get_if_dispensing()
    })

# -------- SET endpoints --------

@bp.route("/set_temp", methods=["POST"])
def set_temp():
    temp = request.json.get("temp_f")
    ctrl.set_specified_temperature(temp)
    return jsonify({"ok": True})

@bp.route("/set_dispense", methods=["POST"])
def set_dispense():
    t = request.json.get("seconds")
    ctrl.set_dispense_time(t)
    return jsonify({"ok": True})

# -------- CONTROL --------

@bp.route("/start_auto", methods=["POST"])
def start_auto():
    ctrl.start_automatic_heat_control()
    return jsonify({"ok": True})

@bp.route("/stop_auto", methods=["POST"])
def stop_auto():
    ctrl.stop_automatic_heat_control()
    return jsonify({"ok": True})

@bp.route("/dispense", methods=["POST"])
def dispense():
    success = ctrl.start_dispense()

    if not success:
        return jsonify({"error": "Cannot dispense"}), 409

    return jsonify({"ok": True})

@bp.route("/dispense_enable", methods=["POST"])
def enable_dispense():
    ctrl.enable_dispense()
    return jsonify({"ok": True})

@bp.route("/dispense_disable", methods=["POST"])
def disable_dispense():
    ctrl.disable_dispense()
    return jsonify({"ok": True})

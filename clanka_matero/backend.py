from flask import (
    Blueprint,
    request
)

bp = Blueprint('backend', __name__, url_prefix='/api')



@bp.route('/temperature', methods=['GET'])
def get_temperature():
    return {
        'temperature': 22.5
    }

@bp.route('/temperature', methods=['POST'])
def set_temperature():
    data = request.get_json()
    return {
        'message': 'Temperature updated successfully'
    }
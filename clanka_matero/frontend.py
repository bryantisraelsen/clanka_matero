import functools

from flask import (
    Blueprint, render_template, abort
)


bp = Blueprint('frontend', __name__)


@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')


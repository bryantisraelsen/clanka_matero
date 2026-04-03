import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)


bp = Blueprint('frontend', __name__, url_prefix='/frontend')


@bp.route('/', methods=['GET'])
def index():
    return render_template('frontend/index.html')


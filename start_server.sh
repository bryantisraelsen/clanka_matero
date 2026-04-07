#!/bin/bash

# Start the Flask server
. venv/bin/activate
export FLASK_APP=clanka_matero

flask run --host=0.0.0.0 --port=5000
#!/bin/bash

# start virtual environment
source venv/bin/activate

export FLASK_ENV='development'

# start flask site
python3 run.py

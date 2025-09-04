#!/bin/bash
# Install Python dependencies
pip install -r requirements.txt

# Collect Django static files
python manage.py collectstatic --noinput

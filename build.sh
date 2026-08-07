#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt
python manage.py migrate
python restore_real_user_images.py
python manage.py collectstatic --no-input


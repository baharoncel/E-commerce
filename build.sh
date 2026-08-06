#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py seed_data
python marketplace/scripts/populate_all_categories.py || true
python marketplace/scripts/add_perfume_products.py || true
python marketplace/scripts/add_skincare_products.py || true
python marketplace/scripts/add_haircare_products.py || true

#!/bin/bash
echo "=========================================="
echo "   Campus Lost & Found - Setup Script     "
echo "=========================================="

python3 -m venv venv
source venv/bin/activate

echo "[1/5] Installing requirements (Django + Channels + Pillow)..."
pip install -r requirements.txt

echo "[2/5] Running migrations..."
python manage.py makemigrations items
python manage.py makemigrations messaging
python manage.py migrate

echo "[3/5] Loading default categories..."
python manage.py loaddata fixtures/categories.json

echo "[4/5] Create superuser..."
python manage.py createsuperuser

echo "[5/5] Starting server..."
echo ""
echo "App:   http://127.0.0.1:8000/"
echo "Admin: http://127.0.0.1:8000/admin/"
echo ""
python manage.py runserver

#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Making migrations..."
python manage.py makemigrations
python manage.py makemigrations EcoffeeBase
python manage.py makemigrations login_system
python manage.py makemigrations qr_codes
python manage.py makemigrations add_to_database

echo "Applying migrations..."
python manage.py migrate
python manage.py migrate EcoffeeBase
python manage.py migrate login_system
python manage.py migrate qr_codes
python manage.py migrate add_to_database

echo "Collecting static files..."
python manage.py collectstatic --no-input

# Optional: Create a superuser
# Uncomment and modify if needed
# echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell 
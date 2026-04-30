#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Installing Node.js via nodeenv..."
nodeenv -p --node=20.11.0

echo "Installing Node dependencies..."
npm install

echo "Building Tailwind CSS..."
npm run build

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running database migrations..."
python manage.py migrate

echo "Build finished successfully!"
exit 0

#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Installing Node.js via nodeenv..."
nodeenv -p --node=20.11.0

echo "Installing Node dependencies..."
npm install --include=dev

echo "Building Tailwind CSS..."
npm run build

if [ -f "./static/css/output.css" ]; then
    echo "Tailwind build successful: output.css generated."
else
    echo "ERROR: Tailwind build failed: output.css NOT found."
    # We don't exit here to allow collectstatic to run for other files, 
    # but the error message will be in the logs.
fi

echo "Cleaning previous static files..."
rm -rf ./staticfiles

echo "Collecting static files..."
python manage.py collectstatic --no-input --clear --upload-unhashed-files

echo "Verifying static files..."
ls -R staticfiles/css || echo "staticfiles/css directory not found"

echo "Running database migrations..."
python manage.py migrate


echo "Build finished successfully!"
exit 0

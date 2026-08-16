#!/usr/bin/env bash
# Render build step. Runs on every deploy, with the service's environment
# variables (SECRET_KEY, DATABASE_URL, …) already available.
set -o errexit   # abort on first error
set -o nounset   # treat unset variables as an error
set -o pipefail  # a failing command in a pipe fails the whole pipe

echo "==> Upgrading pip"
python -m pip install --upgrade pip

echo "==> Installing production dependencies"
pip install -r requirements/production.txt

echo "==> Collecting static files"
python manage.py collectstatic --no-input

echo "==> Applying database migrations"
python manage.py migrate --no-input

echo "==> Build complete"

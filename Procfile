# Process definitions for Procfile-based hosts (Railway, Heroku-style PaaS).
# Render uses render.yaml instead, but this keeps the app portable.
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --worker-class gthread --timeout 60 --graceful-timeout 30 --access-logfile - --error-logfile -
release: python manage.py migrate --no-input

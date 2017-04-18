web: newrelic-admin run-program python manage.py run_gunicorn -b "0.0.0.0:$PORT" -w 3 -t 300
worker: celery -A casp worker -l info

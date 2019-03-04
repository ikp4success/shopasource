web: gunicorn app:app
worker: celery -A tasks.celery worker --loglevel=info

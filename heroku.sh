#!/bin/bash
celery -A tasks.celery worker --loglevel=info &
gunicorn app:app

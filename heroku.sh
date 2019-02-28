#!/bin/bash
celery worker -A app.celery &
gunicorn app:app

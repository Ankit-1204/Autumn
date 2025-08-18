#!/bin/bash
# This was created because the worker service was using entrypoint.h
# which belonged to backend
# Wait for database to be ready
echo "Waiting for database..."
while ! nc -z db 5432; do
  sleep 1
done
echo "Database is ready!"

# Run migrations
echo "Running database migrations..."
alembic upgrade head

# Start the Celery worker
echo "Starting Celery worker..."
exec celery -A celery_app.celery_app worker --loglevel=info --concurrency=1

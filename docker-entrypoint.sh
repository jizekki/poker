#!/bin/bash
set -e

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Load environment variables from .env file
export $(cat .env | xargs)

# Wait for database to be ready
echo "Wait for database to be ready"
while ! nc -z $SQL_HOST $SQL_PORT; do
	sleep 1
done

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Create a superuser if it doesn't exist
echo "Create a superuser if it doesn't exist"
echo "from django.contrib.auth.models import User; User.objects.filter(username=\"$DJANGO_SUPERUSER_USERNAME\").count() or User.objects.create_superuser(\"$DJANGO_SUPERUSER_USERNAME\", '', \"$DJANGO_SUPERUSER_PASSWORD\")" | python manage.py shell

# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000

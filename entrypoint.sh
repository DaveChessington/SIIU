#!/bin/sh

python manage.py makemigrations

# Applies migration files
echo "Applying migrations..."
python manage.py migrate

#Creates a user user if not exists already
echo "Setting superuser..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='$DJANGO_SUPERUSER_EMAIL').exists():
    User.objects.create_superuser(email='$DJANGO_SUPERUSER_EMAIL', password='$DJANGO_SUPERUSER_PASSWORD', first_name='$DJANGO_SUPERUSER_NAME', last_name='$DJANGO_SUPERUSER_LASTNAME')
    print('Superuser created!')
else:
    print('Superuser already exists.')
END

echo "Starting Server..."
exec python manage.py runserver 0.0.0.0:8000
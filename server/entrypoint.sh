#!/bin/sh

python manage.py migrate --noinput

echo "from django.contrib.auth import get_user_model; \
User = get_user_model(); \
User.objects.filter(username='admin').exists() or \
User.objects.create_superuser('admin', 'shomdan2004@gmail.com', 'admin123')" \
| python manage.py shell

python manage.py runserver 0.0.0.0:8000
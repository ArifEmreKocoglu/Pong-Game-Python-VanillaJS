#!/bin/bash

# Veritabanının hazır olup olmadığını kontrol edin
while !</dev/tcp/postgres/5432; do sleep 1; done

# Django komutlarını çalıştır
export DJANGO_SETTINGS_MODULE=backend.settings
python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Uygulamayı başlat
exec "$@"

#!/bin/sh

echo "⏳ Attente de la base de données..."
until nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done
echo "✅ Base de données accessible"

echo "🛠️  Migration de la base de données..."
python manage.py migrate --noinput

# Créer un superutilisateur s’il n’existe pas déjà
echo "from django.contrib.auth import get_user_model; \
User = get_user_model(); \
username = '${SUPERUSER_USERNAME}'; \
email = '${SUPERUSER_EMAIL}'; \
password = '${SUPERUSER_PASSWORD}'; \
User.objects.filter(username=username).exists() or \
User.objects.create_superuser(username=username, email=email, password=password)" \
| python manage.py shell

echo "📦 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "🚀 Lancement de Gunicorn..."
exec gunicorn django_project.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --threads 2 \
    --timeout 120

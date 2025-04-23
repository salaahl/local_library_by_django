#!/bin/sh

echo "⏳ Attente de la base de données..."
until nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done
echo "✅ Base de données accessible"

echo "🛠️  Migration de la base de données..."
python manage.py migrate --noinput

echo "📦 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "🚀 Lancement de Gunicorn..."
exec gunicorn django_project.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --threads 2 \
    --timeout 120

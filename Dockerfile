# Dockerfile pour Django en production

FROM python:3.10-slim

# Variables d'environnement
ENV PYTHONUNBUFFERED 1

# Installation des dépendances
RUN apt-get update \
    && apt-get install -y build-essential \
    && apt-get install -y netcat-traditional \
    && apt-get clean

# Créer et définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de l'application dans l'image
COPY . /app/

# Installer les dépendances Python
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copier le script d'entrypoint
COPY entrypoint.sh /entrypoint.sh

# Donner les droits d'exécution au script d'entrypoint
RUN chmod +x /entrypoint.sh

# Définir le script d'entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Exposer le port 8000
EXPOSE 8000

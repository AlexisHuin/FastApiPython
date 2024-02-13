# Utilisez une image Python officielle en tant que base
FROM python:3.9-slim

# Définissez le répertoire de travail dans le conteneur
WORKDIR /app

# Copiez le fichier requirements.txt et installez les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && apt-get update && apt-get install sqlite3

# Copiez le reste des fichiers de l'application dans le conteneur
COPY . .

# Exposez le port sur lequel l'application FastAPI écoute
EXPOSE 8000

# Commande pour lancer l'application lorsque le conteneur démarre
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

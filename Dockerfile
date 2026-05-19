# On part d'une image Python officielle
FROM python:3.11-slim

# On crée le dossier de travail dans le conteneur
WORKDIR /app

# On copie d'abord requirements.txt pour installer les dépendances
COPY requirements.txt .

# On installe les dépendances Python
RUN pip install -r requirements.txt

# On copie tout le reste du projet
COPY . .

# Le port sur lequel Flask écoute
EXPOSE 5000

# Commande pour lancer Flask au démarrage
CMD ["python", "app.py"]
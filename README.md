# Library Chatbot AI

Application de gestion de bibliotheque avec une API Flask, une base PostgreSQL, une interface desktop en CustomTkinter et un chatbot local alimente par Mistral via Ollama.

Le projet utilise du SQL direct avec `psycopg2` au lieu d'un ORM. Le comportement reste simple a lire, facile a depanner et parfaitement adapte a un depot GitHub de presentation.

## Badges

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-API-black)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-316192)](https://www.postgresql.org/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20AI-000000)](https://ollama.com/)

## Sommaire

- [Presentation](#presentation)
- [Fonctionnalites](#fonctionnalites)
- [Architecture](#architecture)
- [Installation](#installation)
- [Execution](#execution)
- [API](#api)
- [Structure](#structure)
- [Schema de donnees](#schema-de-donnees)
- [Depannage](#depannage)

## Presentation

L'application permet de:

- consulter les livres en base
- ajouter un livre
- modifier un livre
- supprimer un livre
- rechercher un livre par titre ou auteur
- discuter avec un chatbot qui repond a partir des donnees reelles de la bibliotheque

## Fonctionnalites

- CRUD complet des livres
- recherche texte sur le titre et l'auteur
- chatbot local connecte a Mistral via Ollama
- interface desktop avec formulaire et tableau
- stockage PostgreSQL gere par requetes SQL explicites

## Architecture

Le projet est decoupe en quatre couches:

### API Flask

Le point d'entree `run.py` lance Flask via `create_app()`.

### Acces aux donnees

`app/models/livre.py` contient les fonctions SQL directes pour lire et modifier les livres.

### Service chatbot

`app/services/chatbot.py` construit un contexte texte a partir des livres en base, puis l'envoie a Mistral.

### Interface graphique

`gui.py` consomme l'API locale avec `requests` et affiche les resultats dans une interface desktop.

## Installation

### 1. Recuperer le projet

```bash
git clone https://github.com/mouradbenabdallah/library-chatbot-ai
cd library-chatbot-ai
```

### 2. Creer un environnement virtuel

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dependances

```bash
pip install -r requirements.txt
```

### 4. Configurer PostgreSQL

Exemple local:

```bash
sudo -u postgres psql
CREATE DATABASE library_db;
CREATE USER mourad WITH PASSWORD '';
GRANT ALL PRIVILEGES ON DATABASE library_db TO mourad;
\q
```

### 5. Configurer le fichier .env

```env
DATABASE_URL=postgresql://mourad:mourad123@localhost/library_db
SECRET_KEY=dev-secret-key
```

### 6. Installer Ollama et Mistral

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull mistral
```

## Execution

Le projet utilise deux processus:

### 1. Demarrer l'API

```bash
python run.py
```

Le serveur est disponible sur `http://localhost:5000`.

### 2. Demarrer l'interface graphique

Dans un autre terminal:

```bash
python gui.py
```

L'interface parle a l'API via `http://localhost:5000/api`.

### 3. Inserer les donnees de demo

```bash
python seed.py
```

Le script ajoute 10 livres de demonstration dans la table `livres`.

## API

### Liste des livres

```bash
GET /api/livres
```

### Recuperer un livre

```bash
GET /api/livres/<id>
```

### Rechercher des livres

```bash
GET /api/livres/search?q=Hugo
```

### Ajouter un livre

```bash
POST /api/livres
Content-Type: application/json

{
  "titre": "Dune",
  "auteur": "Frank Herbert",
  "categorie": "Science-Fiction",
  "annee": 1965,
  "quantite": 3,
  "statut": "disponible"
}
```

### Modifier un livre

```bash
PUT /api/livres/<id>
Content-Type: application/json

{
  "titre": "Dune",
  "auteur": "Frank Herbert",
  "categorie": "Science-Fiction",
  "annee": 1965,
  "quantite": 4,
  "statut": "disponible"
}
```

### Supprimer un livre

```bash
DELETE /api/livres/<id>
```

### Poser une question au chatbot

```bash
POST /api/chat
Content-Type: application/json

{
  "question": "Quels livres de Victor Hugo sont disponibles ?"
}
```

## Structure

```text
app/
  __init__.py
  models/
    __init__.py
    livre.py
  routes/
    __init__.py
    chat.py
    livres.py
  services/
    __init__.py
    chatbot.py
config.py
gui.py
requirements.txt
run.py
seed.py
```

## Schema de donnees

La table `livres` doit contenir au minimum:

- `id`
- `titre`
- `auteur`
- `categorie`
- `annee`
- `quantite`
- `statut`

Types attendus:

- `id`: entier auto-increment
- `titre`: texte
- `auteur`: texte
- `categorie`: texte
- `annee`: entier
- `quantite`: entier
- `statut`: texte

## Flux de fonctionnement

### Gestion des livres

1. L'utilisateur saisit ou selectionne un livre dans l'interface.
2. L'interface envoie une requete HTTP vers l'API Flask.
3. La route `app/routes/livres.py` appelle la fonction SQL correspondante.
4. PostgreSQL execute la requete via `psycopg2`.
5. Le resultat est renvoye en JSON et affiche dans l'interface.

### Chatbot

1. L'utilisateur pose une question dans l'onglet chatbot.
2. L'interface appelle `POST /api/chat`.
3. `app/services/chatbot.py` lit les livres disponibles.
4. Le service construit un contexte texte avec les donnees reelles.
5. Le contexte est transmis a Mistral via Ollama.
6. La reponse est renvoyee a l'utilisateur.

## Details des fichiers

### `app/__init__.py`

Factory Flask qui charge la configuration et enregistre les blueprints.

### `app/models/livre.py`

Couche SQL pure qui gere les requetes sur la table `livres`.

### `app/routes/livres.py`

Routes REST pour le CRUD et la recherche des livres.

### `app/routes/chat.py`

Route qui recoit une question et renvoie la reponse du modele.

### `app/services/chatbot.py`

Service de construction du prompt et appel Ollama.

### `gui.py`

Interface desktop qui pilote l'API et affiche le catalogue.

## Depannage

- Si l'API ne demarre pas, verifie `DATABASE_URL` et PostgreSQL.
- Si le chatbot ne repond pas, verifie que Ollama tourne et que `mistral` est installe.
- Si l'interface reste vide, verifie que `run.py` est lance avant `gui.py`.
- Si tu relances `seed.py`, vide d'abord la table pour eviter les doublons.

## Remarque

Le projet est pense pour etre facile a publier sur GitHub et simple a comprendre au premier coup d'oeil. Le README presente le fonctionnement global, les commandes essentielles et les points d'entree du projet.

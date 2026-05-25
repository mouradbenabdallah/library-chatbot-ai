# Library Chatbot AI

Application desktop de gestion de bibliotheque avec API Flask, PostgreSQL, interface CustomTkinter et chatbot IA via Ollama.

## Fonctionnalites

- login local de demonstration dans `gui.py`
- CRUD complet des livres sans changer les routes existantes
- recherche par titre ou auteur
- chatbot connecte a `POST /api/chat`
- messages de statut clairs et gestion d'erreurs API plus propre
- interface CustomTkinter modernisee avec loaders legers

## Architecture

- `run.py` demarre l'API Flask sur `http://localhost:5000`
- `gui.py` lance l'interface desktop et consomme `API_BASE_URL = "http://localhost:5000/api"`
- `app/routes/livres.py` expose les routes du catalogue
- `app/routes/chat.py` expose la route du chatbot
- `app/models/livre.py` gere les requetes SQL PostgreSQL
- `app/services/chatbot.py` construit le contexte et appelle Ollama

## Installation

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Exemple de `.env` :

```env
DATABASE_URL=postgresql://postgres:1234@localhost:5433/library_db
SECRET_KEY=super-secret-key
```

Pour le chatbot, verifiez aussi que le service Ollama tourne et que le modele `mistral` est installe.

## Lancement

Terminal 1 :

```powershell
python run.py
```

Terminal 2 :

```powershell
python gui.py
```

L'interface se connecte a l'API locale uniquement apres authentification.

## Identifiants

```text
username : admin
password : admin123
```

## Routes principales

```text
GET /api/livres
POST /api/livres
PUT /api/livres/<id>
DELETE /api/livres/<id>
GET /api/livres/search?q=...
POST /api/chat
```

## Flux applicatif

1. L'utilisateur ouvre `gui.py` et voit d'abord l'ecran de login.
2. Si les identifiants sont corrects, l'application principale s'affiche.
3. La liste des livres est chargee apres connexion seulement.
4. Le catalogue appelle les routes CRUD existantes.
5. L'onglet Assistant envoie la question utilisateur a `POST /api/chat`.

## Structure

```text
app/
  __init__.py
  models/
    livre.py
  routes/
    chat.py
    livres.py
  services/
    chatbot.py
config.py
gui.py
requirements.txt
run.py
```

## Depannage

- Si l'API est arretee, l'interface affiche : `API indisponible. Lancez d'abord le backend avec : python run.py`
- Si le catalogue ne charge pas, verifiez `DATABASE_URL`, PostgreSQL et la table `livres`
- Si le chatbot echoue, verifiez Ollama et le modele `mistral`

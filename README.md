# 📚 Library Chatbot AI

Application Python de gestion de bibliothèque avec chatbot IA local (Mistral).

## Stack technique

- **Backend** : Flask + SQLAlchemy
- **Base de données** : PostgreSQL
- **Interface** : CustomTkinter
- **IA locale** : Mistral via Ollama

## Installation

### 1. Cloner le repo

```bash
git clone https://github.com/mouradbenabdallah/library-chatbot-ai
cd library-chatbot-ai
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Configurer PostgreSQL

```bash
sudo -u postgres psql
CREATE DATABASE library_db;
CREATE USER mourad WITH PASSWORD 'mourad123';
GRANT ALL PRIVILEGES ON DATABASE library_db TO mourad;
\q
```

### 4. Configurer le .env

```
DATABASE_URL=postgresql://mourad:mourad123@localhost/library_db
```

### 5. Installer Ollama + Mistral

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull mistral
```

### 6. Lancer l'application

```bash
# Terminal 1 - API Flask
python run.py

# Terminal 2 - Interface graphique
python gui.py
```

### 7. Ajouter les données de démo

```bash
python seed.py
```

## Fonctionnalités

- CRUD complet des livres
- Recherche par titre et auteur
- Chatbot IA avec Mistral en local
- Interface graphique moderne

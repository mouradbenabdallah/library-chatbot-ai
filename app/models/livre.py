import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://mourad:mourad123@localhost/library_db")
BOOK_COLUMNS = ("id", "titre", "auteur", "categorie", "annee", "quantite", "statut")


# Ouvre une connexion PostgreSQL a partir de la variable d'environnement.
def get_connection():
    return psycopg2.connect(DATABASE_URL)


# Convertit une ligne SQL en dictionnaire JSON-compatible.
def _row_to_livre(row):
    return dict(zip(BOOK_COLUMNS, row))


def _select_many(query, params=()):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()


def _select_one(query, params=()):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchone()


def _execute(query, params=()):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)


def _insert_and_return_id(query, params=()):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchone()[0]


# Renvoie tous les livres presents en base.
def get_all_livres():
    rows = _select_many("SELECT id, titre, auteur, categorie, annee, quantite, statut FROM livres ORDER BY id")
    return [_row_to_livre(row) for row in rows]


# Renvoie un livre par identifiant, ou None si aucun enregistrement ne correspond.
def get_livre_by_id(id):
    row = _select_one(
        "SELECT id, titre, auteur, categorie, annee, quantite, statut FROM livres WHERE id = %s",
        (id,),
    )
    if row:
        return _row_to_livre(row)
    return None


# Cherche dans le titre et l'auteur avec ILIKE pour une recherche insensible a la casse.
def search_livres(q):
    rows = _select_many(
        "SELECT id, titre, auteur, categorie, annee, quantite, statut FROM livres WHERE titre ILIKE %s OR auteur ILIKE %s",
        (f"%{q}%", f"%{q}%"),
    )
    return [_row_to_livre(row) for row in rows]


# Insere un livre puis recupere la ligne creee pour retourner un objet complet.
def add_livre(data):
    livre_id = _insert_and_return_id(
        "INSERT INTO livres (titre, auteur, categorie, annee, quantite, statut) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
        (
            data["titre"],
            data["auteur"],
            data["categorie"],
            data["annee"],
            data["quantite"],
            data["statut"],
        ),
    )
    return get_livre_by_id(livre_id)


# Met a jour toutes les colonnes metiers du livre.
def update_livre(id, data):
    _execute(
        "UPDATE livres SET titre=%s, auteur=%s, categorie=%s, annee=%s, quantite=%s, statut=%s WHERE id=%s",
        (
            data["titre"],
            data["auteur"],
            data["categorie"],
            data["annee"],
            data["quantite"],
            data["statut"],
            id,
        ),
    )
    return get_livre_by_id(id)


# Supprime un livre a partir de son identifiant.
def delete_livre(id):
    _execute("DELETE FROM livres WHERE id = %s", (id,))
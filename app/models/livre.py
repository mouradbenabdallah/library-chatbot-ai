import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


# Ouvre une connexion PostgreSQL a partir de la variable d'environnement.
def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


# Convertit une ligne SQL en dictionnaire JSON-compatible.
def _row_to_livre(row):
    return {
        "id": row[0],
        "titre": row[1],
        "auteur": row[2],
        "categorie": row[3],
        "annee": row[4],
        "quantite": row[5],
        "statut": row[6],
    }


# Renvoie tous les livres presents en base.
def get_all_livres():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, titre, auteur, categorie, annee, quantite, statut FROM livres")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [_row_to_livre(row) for row in rows]


# Renvoie un livre par identifiant, ou None si aucun enregistrement ne correspond.
def get_livre_by_id(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, titre, auteur, categorie, annee, quantite, statut FROM livres WHERE id = %s",
        (id,),
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return _row_to_livre(row)
    return None


# Cherche dans le titre et l'auteur avec ILIKE pour une recherche insensible a la casse.
def search_livres(q):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, titre, auteur, categorie, annee, quantite, statut FROM livres WHERE titre ILIKE %s OR auteur ILIKE %s",
        (f"%{q}%", f"%{q}%"),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [_row_to_livre(row) for row in rows]


# Insere un livre puis recupere la ligne creee pour retourner un objet complet.
def add_livre(data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
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
    id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return get_livre_by_id(id)


# Met a jour toutes les colonnes metiers du livre.
def update_livre(id, data):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
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
    conn.commit()
    cur.close()
    conn.close()
    return get_livre_by_id(id)


# Supprime un livre a partir de son identifiant.
def delete_livre(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM livres WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
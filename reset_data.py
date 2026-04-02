"""
Script pour reinitialiser completement la table livres.
Utile si tu as accidentellement supprime les donnees.

Usage: python reset_data.py
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# 10 livres de demonstration
livres = [
    {"titre": "Le Petit Prince", "auteur": "Antoine de Saint-Exupery", "categorie": "Roman", "annee": 1943, "quantite": 3, "statut": "disponible"},
    {"titre": "Les Miserables", "auteur": "Victor Hugo", "categorie": "Roman", "annee": 1862, "quantite": 2, "statut": "emprunte"},
    {"titre": "Notre-Dame de Paris", "auteur": "Victor Hugo", "categorie": "Roman", "annee": 1831, "quantite": 2, "statut": "disponible"},
    {"titre": "Orgueil et Prejuges", "auteur": "Jane Austen", "categorie": "Roman", "annee": 1813, "quantite": 1, "statut": "disponible"},
    {"titre": "1984", "auteur": "George Orwell", "categorie": "Science-Fiction", "annee": 1949, "quantite": 4, "statut": "disponible"},
    {"titre": "Le Rouge et le Noir", "auteur": "Stendhal", "categorie": "Roman", "annee": 1830, "quantite": 1, "statut": "emprunte"},
    {"titre": "Dune", "auteur": "Frank Herbert", "categorie": "Science-Fiction", "annee": 1965, "quantite": 3, "statut": "disponible"},
    {"titre": "L'Etranger", "auteur": "Albert Camus", "categorie": "Philosophie", "annee": 1942, "quantite": 2, "statut": "disponible"},
    {"titre": "Harry Potter T1", "auteur": "J.K. Rowling", "categorie": "Fantastique", "annee": 1997, "quantite": 5, "statut": "disponible"},
    {"titre": "Le Comte de Monte-Cristo", "auteur": "Alexandre Dumas", "categorie": "Aventure", "annee": 1844, "quantite": 2, "statut": "reserve"},
]

try:
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cur = conn.cursor()
    
    # Vide la table livres
    print("Suppression des donnees existantes...")
    cur.execute("DELETE FROM livres")
    
    # Insere les 10 livres de demo
    print("Insertion des 10 livres de demonstration...")
    for data in livres:
        cur.execute(
            "INSERT INTO livres (titre, auteur, categorie, annee, quantite, statut) VALUES (%s, %s, %s, %s, %s, %s)",
            (
                data["titre"],
                data["auteur"],
                data["categorie"],
                data["annee"],
                data["quantite"],
                data["statut"],
            ),
        )
    
    conn.commit()
    print("Base reinitializee avec succes!")
    print(f"{cur.rowcount} livres ajoutes.")
    
except Exception as e:
    print(f"Erreur: {e}")
finally:
    cur.close()
    conn.close()

from app import create_app, db
from app.models.livre import Livre

app = create_app()

livres = [
    {"titre": "Le Petit Prince",       "auteur": "Antoine de Saint-Exupéry", "categorie": "Roman",        "annee": 1943, "quantite": 3, "statut": "disponible"},
    {"titre": "Les Misérables",        "auteur": "Victor Hugo",               "categorie": "Roman",        "annee": 1862, "quantite": 2, "statut": "emprunté"},
    {"titre": "Notre-Dame de Paris",   "auteur": "Victor Hugo",               "categorie": "Roman",        "annee": 1831, "quantite": 2, "statut": "disponible"},
    {"titre": "Orgueil et Préjugés",   "auteur": "Jane Austen",               "categorie": "Roman",        "annee": 1813, "quantite": 1, "statut": "disponible"},
    {"titre": "1984",                  "auteur": "George Orwell",             "categorie": "Science-Fiction","annee": 1949, "quantite": 4, "statut": "disponible"},
    {"titre": "Le Rouge et le Noir",   "auteur": "Stendhal",                  "categorie": "Roman",        "annee": 1830, "quantite": 1, "statut": "emprunté"},
    {"titre": "Dune",                  "auteur": "Frank Herbert",             "categorie": "Science-Fiction","annee": 1965, "quantite": 3, "statut": "disponible"},
    {"titre": "L'Étranger",            "auteur": "Albert Camus",              "categorie": "Philosophie",  "annee": 1942, "quantite": 2, "statut": "disponible"},
    {"titre": "Harry Potter T1",       "auteur": "J.K. Rowling",              "categorie": "Fantastique",  "annee": 1997, "quantite": 5, "statut": "disponible"},
    {"titre": "Le Comte de Monte-Cristo","auteur": "Alexandre Dumas",         "categorie": "Aventure",     "annee": 1844, "quantite": 2, "statut": "réservé"},
]

with app.app_context():
    for data in livres:
        livre = Livre(**data)
        db.session.add(livre)
    db.session.commit()
    print("✅ 10 livres ajoutés avec succès !")
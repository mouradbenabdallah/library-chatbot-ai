import ollama
from app.models.livre import get_all_livres

# Construit un contexte texte a partir du contenu actuel de la base.
def get_context_from_db():
    livres = get_all_livres()
    if not livres:
        return "La bibliothèque est vide pour l'instant."
    
    context = "Voici les livres disponibles dans la bibliothèque :\n\n"
    for l in livres:
        context += f"- ID:{l['id']} | Titre: {l['titre']} | Auteur: {l['auteur']} | "
        context += f"Catégorie: {l['categorie']} | Année: {l['annee']} | "
        context += f"Quantité: {l['quantite']} | Statut: {l['statut']}\n"
    return context

# Interroge Mistral via Ollama avec un prompt centre sur les livres disponibles.
def ask_mistral(question):
    context = get_context_from_db()
    
    prompt = f"""Tu es un assistant intelligent pour une bibliothèque.
Voici les données réelles de la bibliothèque :

{context}

Question de l'utilisateur : {question}

Réponds en français de manière claire et précise en te basant uniquement sur les données ci-dessus."""

    response = ollama.chat(
        model="mistral",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['message']['content']

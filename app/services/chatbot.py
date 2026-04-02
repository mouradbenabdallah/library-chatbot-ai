import ollama
from app.models.livre import get_all_livres

# Construit un contexte texte a partir du contenu actuel de la base.
def get_context_from_db():
    livres = get_all_livres()
    if not livres:
        return "La bibliothèque est vide pour l'instant."

    lines = ["Voici les livres disponibles dans la bibliothèque :", ""]
    for livre in livres:
        lines.append(
            f"- ID:{livre['id']} | Titre: {livre['titre']} | Auteur: {livre['auteur']} | "
            f"Catégorie: {livre['categorie']} | Année: {livre['annee']} | "
            f"Quantité: {livre['quantite']} | Statut: {livre['statut']}"
        )
    return "\n".join(lines)

# Interroge Mistral via Ollama avec un prompt centre sur les livres disponibles.
def ask_mistral(question):
    context = get_context_from_db()

    prompt = f"""Tu es un assistant intelligent pour une bibliothèque.
Voici les données réelles de la bibliothèque :

{context}

Question de l'utilisateur : {question}

Réponds en français de manière claire et précise en te basant uniquement sur les données ci-dessus."""

    try:
        response = ollama.chat(
            model="mistral",
            messages=[{"role": "user", "content": prompt}]
        )
    except Exception as exc:
        raise RuntimeError(
            "Ollama indisponible. Verifiez que le service Ollama tourne et que le modele mistral est installe."
        ) from exc

    return response['message']['content']

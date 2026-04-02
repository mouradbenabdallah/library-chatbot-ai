from flask import Blueprint, request, jsonify
from app.models.livre import (
    get_all_livres,
    get_livre_by_id,
    search_livres as search_livres_model,
    add_livre as add_livre_model,
    update_livre as update_livre_model,
    delete_livre as delete_livre_model,
)

livres_bp = Blueprint('livres', __name__)
REQUIRED_FIELDS = ("titre", "auteur", "categorie", "annee", "quantite", "statut")


def _error(message, status=400):
    return jsonify({'error': message}), status


def _validated_payload(payload):
    if not payload:
        return None, "Corps JSON manquant"

    missing = [field for field in REQUIRED_FIELDS if field not in payload]
    if missing:
        return None, f"Champ manquant: {missing[0]}"

    try:
        data = {
            "titre": str(payload["titre"]).strip(),
            "auteur": str(payload["auteur"]).strip(),
            "categorie": str(payload["categorie"]).strip(),
            "annee": int(payload["annee"]),
            "quantite": int(payload["quantite"]),
            "statut": str(payload["statut"]).strip(),
        }
    except (TypeError, ValueError):
        return None, "Type de donnees invalide"

    if not data["titre"] or not data["auteur"]:
        return None, "Titre et auteur sont obligatoires"

    return data, None

# Retourne l'ensemble du catalogue.

@livres_bp.route('/livres', methods=['GET'])
def get_livres():
    try:
        return jsonify(get_all_livres())
    except Exception:
        return _error('Impossible de recuperer les livres', 500)

@livres_bp.route('/livres/<int:id>', methods=['GET'])
def get_livre(id):
    try:
        livre = get_livre_by_id(id)
        if livre:
            return jsonify(livre)
        return _error('Livre non trouve', 404)
    except Exception:
        return _error('Impossible de recuperer le livre', 500)

# Recherche des livres par titre ou auteur.
@livres_bp.route('/livres/search', methods=['GET'])
def search_livres():
    q = request.args.get('q', '')
    try:
        return jsonify(search_livres_model(q))
    except Exception:
        return _error('Impossible de rechercher les livres', 500)

# Cree un nouveau livre a partir du JSON recu.
@livres_bp.route('/livres', methods=['POST'])
def add_livre():
    payload = request.get_json(silent=True) or {}
    data, validation_error = _validated_payload(payload)
    if validation_error:
        return _error(validation_error, 400)

    try:
        return jsonify(add_livre_model(data)), 201
    except Exception:
        return _error('Impossible d ajouter le livre', 500)

# Remplace les donnees principales d'un livre existant.
@livres_bp.route('/livres/<int:id>', methods=['PUT'])
def update_livre(id):
    payload = request.get_json(silent=True) or {}
    data, validation_error = _validated_payload(payload)
    if validation_error:
        return _error(validation_error, 400)

    try:
        livre = update_livre_model(id, data)
        if not livre:
            return _error('Livre non trouve', 404)
        return jsonify(livre)
    except Exception:
        return _error('Impossible de modifier le livre', 500)

# Supprime un livre et confirme l'operation.
@livres_bp.route('/livres/<int:id>', methods=['DELETE'])
def delete_livre(id):
    try:
        delete_livre_model(id)
        return jsonify({'message': f'Livre {id} supprime'})
    except Exception:
        return _error('Impossible de supprimer le livre', 500)
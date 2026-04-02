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

# Retourne l'ensemble du catalogue.

@livres_bp.route('/livres', methods=['GET'])
def get_livres():
    return jsonify(get_all_livres())

@livres_bp.route('/livres/<int:id>', methods=['GET'])
def get_livre(id):
    livre = get_livre_by_id(id)
    if livre:
        return jsonify(livre)
    return jsonify({'error': 'Livre non trouve'}), 404

# Recherche des livres par titre ou auteur.
@livres_bp.route('/livres/search', methods=['GET'])
def search_livres():
    q = request.args.get('q', '')
    return jsonify(search_livres_model(q))

# Cree un nouveau livre a partir du JSON recu.
@livres_bp.route('/livres', methods=['POST'])
def add_livre():
    return jsonify(add_livre_model(request.get_json())), 201

# Remplace les donnees principales d'un livre existant.
@livres_bp.route('/livres/<int:id>', methods=['PUT'])
def update_livre(id):
    return jsonify(update_livre_model(id, request.get_json()))

# Supprime un livre et confirme l'operation.
@livres_bp.route('/livres/<int:id>', methods=['DELETE'])
def delete_livre(id):
    delete_livre_model(id)
    return jsonify({'message': f'Livre {id} supprime'})
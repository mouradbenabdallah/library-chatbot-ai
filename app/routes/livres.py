from flask import Blueprint, request, jsonify
from app import db
from app.models.livre import Livre

livres_bp = Blueprint('livres', __name__)

# GET tous les livres
@livres_bp.route('/livres', methods=['GET'])
def get_livres():
    livres = Livre.query.all()
    return jsonify([l.to_dict() for l in livres])

# GET un livre par ID
@livres_bp.route('/livres/<int:id>', methods=['GET'])
def get_livre(id):
    livre = Livre.query.get_or_404(id)
    return jsonify(livre.to_dict())

# GET recherche par titre ou auteur
@livres_bp.route('/livres/search', methods=['GET'])
def search_livres():
    q = request.args.get('q', '')
    livres = Livre.query.filter(
        Livre.titre.ilike(f'%{q}%') |
        Livre.auteur.ilike(f'%{q}%')
    ).all()
    return jsonify([l.to_dict() for l in livres])

# POST ajouter un livre
@livres_bp.route('/livres', methods=['POST'])
def add_livre():
    data = request.get_json()
    livre = Livre(
        titre     = data['titre'],
        auteur    = data['auteur'],
        categorie = data['categorie'],
        annee     = data['annee'],
        quantite  = data.get('quantite', 1),
        statut    = data.get('statut', 'disponible')
    )
    db.session.add(livre)
    db.session.commit()
    return jsonify(livre.to_dict()), 201

# PUT modifier un livre
@livres_bp.route('/livres/<int:id>', methods=['PUT'])
def update_livre(id):
    livre = Livre.query.get_or_404(id)
    data  = request.get_json()
    livre.titre     = data.get('titre',     livre.titre)
    livre.auteur    = data.get('auteur',    livre.auteur)
    livre.categorie = data.get('categorie', livre.categorie)
    livre.annee     = data.get('annee',     livre.annee)
    livre.quantite  = data.get('quantite',  livre.quantite)
    livre.statut    = data.get('statut',    livre.statut)
    db.session.commit()
    return jsonify(livre.to_dict())

# DELETE supprimer un livre
@livres_bp.route('/livres/<int:id>', methods=['DELETE'])
def delete_livre(id):
    livre = Livre.query.get_or_404(id)
    db.session.delete(livre)
    db.session.commit()
    return jsonify({'message': f'Livre {id} supprimé'})
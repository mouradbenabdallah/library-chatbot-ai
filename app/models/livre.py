from app import db
from datetime import datetime

class Livre(db.Model):
    __tablename__ = 'livres'

    id          = db.Column(db.Integer, primary_key=True)
    titre       = db.Column(db.String(200), nullable=False)
    auteur      = db.Column(db.String(150), nullable=False)
    categorie   = db.Column(db.String(100), nullable=False)
    annee       = db.Column(db.Integer, nullable=False)
    quantite    = db.Column(db.Integer, default=1)
    statut      = db.Column(db.String(50), default='disponible')
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id':        self.id,
            'titre':     self.titre,
            'auteur':    self.auteur,
            'categorie': self.categorie,
            'annee':     self.annee,
            'quantite':  self.quantite,
            'statut':    self.statut
        }

    def __repr__(self):
        return f'<Livre {self.titre}>'
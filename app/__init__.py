from flask import Flask
from config import Config


"""Factory Flask de l'application.

Le projet expose une API REST Flask utilisee par l'interface graphique.
La configuration est chargee depuis config.py et les routes sont regroupees
dans des blueprints pour garder le code modulaire.
"""


def create_app():
    # Cree l'application Flask et charge la configuration partagee.
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enregistre les blueprints de l'API livres et du chatbot.
    from app.routes import livres_bp, chat_bp
    app.register_blueprint(livres_bp, url_prefix='/api')
    app.register_blueprint(chat_bp,   url_prefix='/api')

    return app
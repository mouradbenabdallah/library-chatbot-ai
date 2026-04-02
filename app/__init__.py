from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        from app.models import Livre
        db.create_all()

        from app.routes import livres_bp, chat_bp
        app.register_blueprint(livres_bp, url_prefix='/api')
        app.register_blueprint(chat_bp,   url_prefix='/api')

    return app
from flask import Blueprint, request, jsonify
from app.services.chatbot import ask_mistral

chat_bp = Blueprint('chat', __name__)

# Recoit une question utilisateur et renvoie la reponse du modele Mistral.

@chat_bp.route('/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True) or {}
    question = data.get('question', '')
    if not question:
        return jsonify({'error': 'Question vide'}), 400
    try:
        reponse = ask_mistral(question)
        return jsonify({'reponse': reponse})
    except RuntimeError as exc:
        return jsonify({'error': str(exc)}), 503
    except Exception:
        return jsonify({'error': 'Impossible de contacter le chatbot'}), 500

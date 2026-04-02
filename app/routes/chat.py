from flask import Blueprint, request, jsonify
from app.services.chatbot import ask_mistral

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    data     = request.get_json()
    question = data.get('question', '')
    if not question:
        return jsonify({'error': 'Question vide'}), 400
    reponse = ask_mistral(question)
    return jsonify({'reponse': reponse})

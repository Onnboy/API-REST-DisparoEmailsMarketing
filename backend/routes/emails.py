from flask import Blueprint, request, jsonify
from backend.config import get_db_connection

emails_bp = Blueprint('emails', __name__)

@emails_bp.route('/emails', methods=['POST'])
def criar_email():
    dados = request.json

    if not dados or 'email' not in dados:
        return jsonify({"error": "O campo 'email' é obrigatório!"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Verifica se o e-mail já está cadastrado
    cursor.execute("SELECT id FROM emails WHERE email = %s", (dados['email'],))
    existe = cursor.fetchone()

    if existe:
        cursor.close()
        connection.close()
        return jsonify({"error": "O e-mail já está cadastrado!"}), 400

    cursor.execute("INSERT INTO emails (email, nome) VALUES (%s, %s)", (dados['email'], dados.get('nome')))
    connection.commit()

    cursor.close()
    connection.close()
    
    return jsonify({"message": f"Email {dados['email']} cadastrado com sucesso!"}), 201
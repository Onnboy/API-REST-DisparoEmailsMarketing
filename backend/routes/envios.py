from flask import Blueprint, request, jsonify
from backend.config import get_db_connection

envios_bp = Blueprint('envios', __name__)

@envios_bp.route('/envios', methods=['POST'])
def registrar_envio():
    dados = request.json

    if not dados or 'campanha_id' not in dados or 'email_id' not in dados:
        return jsonify({"error": "Os campos 'campanha_id' e 'email_id' são obrigatórios!"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Verifica se já existe um envio com essa campanha e email
    cursor.execute("SELECT id FROM envios WHERE campanha_id = %s AND email_id = %s", (dados['campanha_id'], dados['email_id']))
    existe = cursor.fetchone()

    if existe:
        cursor.close()
        connection.close()
        return jsonify({"error": "Este email já foi enviado para esta campanha!"}), 400

    cursor.execute("INSERT INTO envios (campanha_id, email_id, status) VALUES (%s, %s, 'pendente')",
                   (dados['campanha_id'], dados['email_id']))
    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({"message": "Envio registrado com sucesso!"}), 201

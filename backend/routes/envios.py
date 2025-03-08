from flask import Blueprint, request, jsonify
from backend.config import get_db_connection
from flasgger import swag_from

envios_bp = Blueprint('envios', __name__)

@envios_bp.route('/envios', methods=['GET'])
def listar_envios():
    """Lista todos os envios de e-mails registrados."""
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT e.id, e.campanha_id, c.titulo, e.email_id, em.email, e.status, e.data_envio
        FROM envios e
        JOIN campanhas c ON e.campanha_id = c.id
        JOIN emails em ON e.email_id = em.id
    """)
    envios = cursor.fetchall()

    cursor.close()
    connection.close()

    if not envios:
        return jsonify({"message": "Nenhum envio registrado."}), 404

    return jsonify([
        {
            "id": e[0],
            "campanha_id": e[1],
            "campanha_titulo": e[2],
            "email_id": e[3],
            "email": e[4],
            "status": e[5],
            "data_envio": str(e[6])
        } for e in envios
    ]), 200

@envios_bp.route('/envios', methods=['POST'])
@swag_from({
    "tags": ["Envios"],
    "summary": "Registrar envio de e-mail",
    "description": "Registra um envio de e-mail para uma campanha.",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "campanha_id": {"type": "integer"},
                    "email_id": {"type": "integer"}
                }
            }
        }
    ],
    "responses": {
        201: {
            "description": "Envio registrado com sucesso!",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"}
                }
            }
        },
        400: {
            "description": "Erro na requisição",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"}
                }
            }
        }
    }
})
def registrar_envio():
    """Registra um envio de e-mail vinculado a uma campanha."""
    dados = request.json

    if not dados or 'campanha_id' not in dados or 'email_id' not in dados:
        return jsonify({"error": "Os campos 'campanha_id' e 'email_id' são obrigatórios!"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM campanhas WHERE id = %s", (dados['campanha_id'],))
    campanha = cursor.fetchone()
    if not campanha:
        cursor.close()
        connection.close()
        return jsonify({"error": "Campanha não encontrada"}), 404

    cursor.execute("SELECT id FROM emails WHERE id = %s", (dados['email_id'],))
    email = cursor.fetchone()
    if not email:
        cursor.close()
        connection.close()
        return jsonify({"error": "E-mail não encontrado"}), 404

    cursor.execute("SELECT id FROM envios WHERE campanha_id = %s AND email_id = %s",
                   (dados['campanha_id'], dados['email_id']))
    if cursor.fetchone():
        cursor.close()
        connection.close()
        return jsonify({"error": "Este e-mail já foi enviado para esta campanha!"}), 409

    cursor.execute("INSERT INTO envios (campanha_id, email_id, status) VALUES (%s, %s, 'pendente')",
                   (dados['campanha_id'], dados['email_id']))
    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({"message": "Envio registrado com sucesso!"}), 201

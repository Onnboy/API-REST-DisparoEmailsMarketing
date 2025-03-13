from flask import Blueprint, request, jsonify
from backend.config import get_db_connection
from flasgger import swag_from
import logging

envios_bp = Blueprint('envios', __name__)
logging.basicConfig(level=logging.INFO)

@envios_bp.route('/envios', methods=['GET'])
@swag_from({
    "tags": ["Envios"],
    "summary": "Listar todos os envios de e-mails",
    "description": "Lista todos os envios registrados, com detalhes de campanha e destinatário.",
    "responses": {
        200: {
            "description": "Lista de envios encontrados",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "example": 1},
                        "campanha_id": {"type": "integer", "example": 2},
                        "campanha_titulo": {"type": "string", "example": "Campanha Promocional"},
                        "email_id": {"type": "integer", "example": 5},
                        "email": {"type": "string", "example": "cliente@email.com"},
                        "status": {"type": "string", "example": "pendente"},
                        "data_envio": {"type": "string", "example": "2025-03-10 10:00:00"}
                    }
                }
            }
        },
        404: {
            "description": "Nenhum envio encontrado",
            "schema": {"type": "object", "properties": {"message": {"type": "string"}}}
        }
    }
})
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
    "description": "Registra um envio de e-mail vinculado a uma campanha específica e destinatário.",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "campanha_id": {"type": "integer", "example": 1},
                    "email_id": {"type": "integer", "example": 10}
                },
                "required": ["campanha_id", "email_id"]
            }
        }
    ],
    "responses": {
        201: {
            "description": "Envio registrado com sucesso",
            "schema": {"type": "object", "properties": {"message": {"type": "string"}}}
        },
        400: {
            "description": "Campos obrigatórios ausentes",
            "schema": {"type": "object", "properties": {"error": {"type": "string"}}}
        },
        404: {
            "description": "Campanha ou e-mail não encontrados",
            "schema": {"type": "object", "properties": {"error": {"type": "string"}}}
        },
        409: {
            "description": "E-mail já enviado para essa campanha",
            "schema": {"type": "object", "properties": {"error": {"type": "string"}}}
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

@envios_bp.route('/envios/status', methods=['PUT'])
@swag_from({
    "tags": ["Envios"],
    "summary": "Atualizar status do envio",
    "description": "Atualiza o status de um e-mail enviado dentro de uma campanha específica.",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "campanha_id": {"type": "integer", "example": 1},
                    "email_id": {"type": "integer", "example": 10},
                    "status": {"type": "string", "example": "enviado"}
                },
                "required": ["campanha_id", "email_id", "status"]
            }
        }
    ],
    "responses": {
        200: {
            "description": "Status atualizado com sucesso",
            "schema": {"type": "object", "properties": {"message": {"type": "string"}}}
        },
        400: {
            "description": "Dados inválidos",
            "schema": {"type": "object", "properties": {"error": {"type": "string"}}}
        },
        404: {
            "description": "Registro não encontrado",
            "schema": {"type": "object", "properties": {"error": {"type": "string"}}}
        },
        500: {
            "description": "Erro interno",
            "schema": {"type": "object", "properties": {"error": {"type": "string"}}}
        }
    }
})
def atualizar_status_envio():
    """Atualiza o status de um envio específico baseado na campanha e no e-mail."""
    dados = request.json
    campanha_id = dados.get('campanha_id')
    email_id = dados.get('email_id')
    status = dados.get('status')

    status_permitidos = ['pendente', 'enviado', 'erro']

    if not campanha_id or not email_id or not status:
        return jsonify({"error": "Campos 'campanha_id', 'email_id' e 'status' são obrigatórios."}), 400

    if status not in status_permitidos:
        return jsonify({"error": f"Status inválido. Permitidos: {', '.join(status_permitidos)}."}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT id FROM envios WHERE campanha_id = %s AND email_id = %s
        """, (campanha_id, email_id))
        registro = cursor.fetchone()

        if not registro:
            return jsonify({"error": "Registro de envio não encontrado."}), 404

        cursor.execute("""
            UPDATE envios
            SET status = %s
            WHERE campanha_id = %s AND email_id = %s
        """, (status, campanha_id, email_id))
        connection.commit()

        return jsonify({"message": "Status atualizado com sucesso."}), 200

    except Exception as e:
        connection.rollback()
        return jsonify({"error": f"Erro ao atualizar o status: {str(e)}"}), 500

    finally:
        cursor.close()
        connection.close()
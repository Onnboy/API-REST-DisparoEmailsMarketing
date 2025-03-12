from flask import Blueprint, request, jsonify
from backend.config import get_db_connection
from flasgger import swag_from

agendar_envio_bp = Blueprint('agendar_envio', __name__)

@agendar_envio_bp.route('/envios/agendados', methods=['POST'])
@swag_from({
    "tags": ["Agendamentos"],
    "summary": "Agendar envio de campanha",
    "description": "Permite agendar o envio de uma campanha de e-mail para uma data e hora específicas.",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "campanha_id": {
                        "type": "integer",
                        "example": 1
                    },
                    "data_envio": {
                        "type": "string",
                        "example": "2025-03-10 10:00:00"
                    }
                },
                "required": ["campanha_id", "data_envio"]
            }
        }
    ],
    "responses": {
        200: {
            "description": "Envio agendado com sucesso",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "Envio agendado com sucesso!"}
                }
            }
        },
        400: {
            "description": "Erro de validação ou campanha não encontrada",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "Campanha não encontrada"}
                }
            }
        },
        500: {
            "description": "Erro interno ao tentar agendar o envio",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "Erro ao agendar envio: mensagem de erro"}
                }
            }
        }
    }
})
def agendar_envio():
    """
    Agenda o envio de uma campanha de e-mail para uma data e hora específicas.
    ---
    """
    dados = request.json

    if not dados or 'campanha_id' not in dados or 'data_envio' not in dados:
        return jsonify({"error": "Os campos 'campanha_id' e 'data_envio' são obrigatórios!"}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT id FROM campanhas WHERE id = %s", (dados['campanha_id'],))
        campanha = cursor.fetchone()

        if not campanha:
            return jsonify({"error": "Campanha não encontrada"}), 400

        cursor.execute("UPDATE campanhas SET data_envio = %s WHERE id = %s", 
                       (dados['data_envio'], dados['campanha_id']))
        connection.commit()

        return jsonify({"message": "Envio agendado com sucesso!"}), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao agendar envio: {str(e)}"}), 500

    finally:
        cursor.close()
        connection.close()

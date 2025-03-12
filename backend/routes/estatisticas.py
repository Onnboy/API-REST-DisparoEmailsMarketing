from flask import Blueprint, request, jsonify
from backend.config import get_db_connection
from flasgger import swag_from

estatisticas_bp = Blueprint('estatisticas', __name__)

@estatisticas_bp.route('/abertura', methods=['POST'])
@swag_from({
    "tags": ["Estatísticas"],
    "summary": "Registrar abertura de e-mail",
    "description": "Incrementa a taxa de abertura da campanha informada.",
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
                    }
                },
                "required": ["campanha_id"]
            }
        }
    ],
    "responses": {
        200: {
            "description": "Abertura registrada com sucesso",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "Abertura registrada com sucesso!"}
                }
            }
        },
        400: {
            "description": "Campo obrigatório não informado",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "O campo 'campanha_id' é obrigatório!"}
                }
            }
        }
    }
})
def registrar_abertura():
    dados = request.json
    campanha_id = dados.get('campanha_id')

    if not campanha_id:
        return jsonify({"error": "O campo 'campanha_id' é obrigatório!"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE campanhas 
        SET taxa_abertura = taxa_abertura + 1
        WHERE id = %s
    """, (campanha_id,))
    affected_rows = cursor.rowcount
    connection.commit()

    cursor.close()
    connection.close()

    if affected_rows == 0:
        return jsonify({"error": "Campanha não encontrada"}), 404

    return jsonify({"message": "Abertura registrada com sucesso!"}), 200


@estatisticas_bp.route('/clique', methods=['POST'])
@swag_from({
    "tags": ["Estatísticas"],
    "summary": "Registrar clique em e-mail",
    "description": "Incrementa a taxa de cliques da campanha informada.",
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
                    }
                },
                "required": ["campanha_id"]
            }
        }
    ],
    "responses": {
        200: {
            "description": "Clique registrado com sucesso",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "Clique registrado com sucesso!"}
                }
            }
        },
        400: {
            "description": "Campo obrigatório não informado",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "O campo 'campanha_id' é obrigatório!"}
                }
            }
        }
    }
})
def registrar_clique():
    dados = request.json
    campanha_id = dados.get('campanha_id')

    if not campanha_id:
        return jsonify({"error": "O campo 'campanha_id' é obrigatório!"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM campanhas WHERE id = %s", (campanha_id,))
    campanha = cursor.fetchone()

    if not campanha:
        cursor.close()
        connection.close()
        return jsonify({"error": "Campanha não encontrada"}), 404

    cursor.execute("""
        UPDATE campanhas 
        SET taxa_cliques = taxa_cliques + 1
        WHERE id = %s
    """, (campanha_id,))
    connection.commit()
    
    cursor.close()
    connection.close()

    return jsonify({"message": "Clique registrado com sucesso!"}), 200

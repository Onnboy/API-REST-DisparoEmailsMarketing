from flask import Blueprint, jsonify
from backend.config import get_db_connection
from flasgger import swag_from

campanhas_bp = Blueprint('campanhas', __name__)

@campanhas_bp.route('/campanhas', methods=['GET'])
@swag_from({
    "tags": ["Campanhas"],
    "summary": "Listar campanhas",
    "description": "Retorna todas as campanhas cadastradas no sistema.",
    "responses": {
        200: {
            "description": "Lista de campanhas",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "titulo": {"type": "string"},
                        "mensagem": {"type": "string"},
                        "data_envio": {"type": "string"},
                        "status": {"type": "string"},
                        "frequencia": {"type": "string"},
                        "email": {"type": "string"}
                    }
                }
            }
        }
    }
})
def listar_campanhas():
    """Lista todas as campanhas registradas no banco de dados."""
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, titulo, mensagem, data_envio, status, frequencia, email FROM campanhas")
    campanhas = cursor.fetchall()

    cursor.close()
    connection.close()

    if not campanhas:
        return jsonify({"message": "Nenhuma campanha encontrada."}), 404

    return jsonify([
        {
            "id": c[0],
            "titulo": c[1],
            "mensagem": c[2],
            "data_envio": c[3],
            "status": c[4],
            "frequencia": c[5],
            "email": c[6]
        } for c in campanhas
    ]), 200

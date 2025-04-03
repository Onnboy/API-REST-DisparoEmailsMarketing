from flask import Blueprint, jsonify
from backend.config import get_db_connection
from flasgger import swag_from

status_bp = Blueprint('status', __name__)

@status_bp.route('/', methods=['GET'])
@swag_from({
    "tags": ["Status"],
    "summary": "Verificar status",
    "description": "Retorna o status dos serviços do sistema.",
    "responses": {
        200: {
            "description": "Status dos serviços",
            "schema": {
                "type": "object",
                "properties": {
                    "smtp": {"type": "string", "enum": ["configured", "not_configured"]},
                    "webhook": {"type": "string", "enum": ["configured", "not_configured"]}
                }
            }
        }
    }
})
def verificar_status():
    """Verifica o status dos serviços do sistema."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Inicializar status dos serviços
        status = {
            "smtp": "not_configured",
            "webhook": "not_configured"
        }

        # Verificar integrações ativas
        cursor.execute("SELECT tipo FROM integracoes")
        integracoes = cursor.fetchall()

        # Atualizar status baseado nas integrações encontradas
        for integracao in integracoes:
            if integracao['tipo'] == 'smtp':
                status['smtp'] = "configured"
            elif integracao['tipo'] == 'webhook':
                status['webhook'] = "configured"

        cursor.close()
        connection.close()

        return jsonify(status), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao verificar status: {str(e)}"}), 500 
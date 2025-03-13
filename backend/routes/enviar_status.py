from flask import Blueprint, jsonify, request
from backend.config import get_db_connection
from flasgger import swag_from

update_status_bp = Blueprint('update_status', __name__)

@update_status_bp.route('/envios/status', methods=['PUT'])
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
    """
    Atualiza o status de um e-mail enviado dentro de uma campanha específica.

    Requer JSON no formato:
    {
        "campanha_id": 1,
        "email_id": 10,
        "status": "enviado"
    }
    """
    dados = request.json
    campanha_id = dados.get('campanha_id')
    email_id = dados.get('email_id')
    status = dados.get('status')

    status_permitidos = ["pendente", "enviado", "erro", "falhou", "lido", "clicado"]

    if not campanha_id or not email_id or not status:
        return jsonify({"error": "Campos 'campanha_id', 'email_id' e 'status' são obrigatórios."}), 400

    if status.lower() not in status_permitidos:
        return jsonify({"error": f"Status inválido. Permitidos: {', '.join(status_permitidos)}."}), 400

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 1 FROM envios
            WHERE campanha_id = %s AND email_id = %s
        """, (campanha_id, email_id))
        registro = cursor.fetchone()

        if not registro:
            return jsonify({"error": "Registro de envio não encontrado."}), 404

        cursor.execute("""
            UPDATE envios
            SET status = %s
            WHERE campanha_id = %s AND email_id = %s
        """, (status.lower(), campanha_id, email_id))

        conn.commit()
        return jsonify({"message": "Status atualizado com sucesso."}), 200

    except Exception as e:
        print(f"[ERRO] Falha ao atualizar status: {e}")
        return jsonify({"error": "Erro ao atualizar o status."}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

from flask import Blueprint, request, jsonify
from backend.config import get_db_connection
from backend.routes.campanhas import campanhas_bp
from flasgger import swag_from

@campanhas_bp.route('/emails/<int:id>', methods=['PUT'])
@swag_from({
    "tags": ["Campanhas"],
    "summary": "Atualizar e-mail vinculado à campanha",
    "description": "Atualiza o e-mail associado a uma campanha específica no banco de dados.",
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID da campanha a ser atualizada"
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "example": "novoemail@exemplo.com"
                    }
                },
                "required": ["email"]
            }
        }
    ],
    "responses": {
        200: {
            "description": "E-mail atualizado com sucesso",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "E-mail atualizado com sucesso!"}
                }
            }
        },
        400: {
            "description": "Erro de validação",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "O campo 'email' é obrigatório!"}
                }
            }
        },
        500: {
            "description": "Erro interno ao atualizar",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "Erro ao atualizar e-mail: mensagem de erro"}
                }
            }
        }
    }
})
def atualizar_email(id):
    """
    Atualiza o e-mail vinculado a uma campanha específica.
    ---
    """
    dados = request.json
    if not dados or 'email' not in dados:
        return jsonify({"error": "O campo 'email' é obrigatório!"}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("UPDATE campanhas SET email = %s WHERE id = %s", (dados['email'], id))
        connection.commit()

        return jsonify({"message": "E-mail atualizado com sucesso!"}), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao atualizar e-mail: {str(e)}"}), 500
    finally:
        cursor.close()
        connection.close()


@campanhas_bp.route('/emails/<int:id>', methods=['DELETE'])
@swag_from({
    "tags": ["Campanhas"],
    "summary": "Remover e-mail vinculado à campanha",
    "description": "Remove o e-mail associado a uma campanha específica do banco de dados.",
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID da campanha cujo e-mail será removido"
        }
    ],
    "responses": {
        200: {
            "description": "E-mail removido com sucesso",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "example": "E-mail removido com sucesso!"}
                }
            }
        },
        500: {
            "description": "Erro interno ao remover",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "Erro ao remover e-mail: mensagem de erro"}
                }
            }
        }
    }
})
def remover_email(id):
    """
    Remove o e-mail vinculado a uma campanha específica.
    ---
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM campanhas WHERE id = %s", (id,))
        connection.commit()

        return jsonify({"message": "E-mail removido com sucesso!"}), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao remover e-mail: {str(e)}"}), 500
    finally:
        cursor.close()
        connection.close()
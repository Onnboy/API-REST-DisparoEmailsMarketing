from flask import Blueprint, request, jsonify
from backend.config import get_db_connection
from backend.routes.campanhas import campanhas_bp
from flasgger import swag_from

@campanhas_bp.route('/emails/<int:id>', methods=['PUT'])
def atualizar_email(id):
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
def remover_email(id):
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
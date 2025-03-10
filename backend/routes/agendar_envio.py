from flask import Blueprint, request, jsonify
from backend.config import get_db_connection
from backend.routes.campanhas import campanhas_bp
from flasgger import swag_from

agendar_envio_bp = Blueprint('agendar_envio', __name__)

@agendar_envio_bp.route('/envios/agendados', methods=['POST'])
def agendar_envio():
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

from flask import Blueprint, request, jsonify
from backend.config import get_db_connection

estatisticas_bp = Blueprint('estatisticas', __name__)

@estatisticas_bp.route('/abertura', methods=['POST'])
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
    connection.commit()
    
    cursor.close()
    connection.close()
    return jsonify({"message": "Abertura registrada com sucesso!"}), 200

@estatisticas_bp.route('/clique', methods=['POST'])
def registrar_clique():
    dados = request.json
    campanha_id = dados.get('campanha_id')

    if not campanha_id:
        return jsonify({"error": "O campo 'campanha_id' é obrigatório!"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE campanhas 
        SET taxa_cliques = taxa_cliques + 1
        WHERE id = %s
    """, (campanha_id,))
    connection.commit()
    
    cursor.close()
    connection.close()
    return jsonify({"message": "Clique registrado com sucesso!"}), 200

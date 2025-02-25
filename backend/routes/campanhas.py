from flask import Blueprint, request, jsonify
from backend.config import get_db_connection

campanhas_bp = Blueprint('campanhas', __name__)

@campanhas_bp.route('/campanhas', methods=['GET'])
def listar_campanhas():
    return jsonify({"message": "Lista de campanhas"}), 200

@campanhas_bp.route('/campanhas', methods=['POST'])
def criar_campanha():
    dados = request.json
    
    # Validação de dados recebidos
    if not dados or 'titulo' not in dados:
        return jsonify({"error": "O campo 'titulo' é obrigatório!"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM campanhas WHERE titulo = %s", (dados['titulo'],))
    existe = cursor.fetchone()

    if existe:
        cursor.close()
        connection.close()
        return jsonify({"error": "Já existe uma campanha com este título!"}), 400

    cursor.execute("INSERT INTO campanhas (titulo, mensagem, assunto, data_envio, frequencia, email) VALUES (%s, %s, %s, %s, %s, %s)",
                   (dados['titulo'], dados.get('mensagem'), dados.get('assunto'), dados.get('data_envio'), dados.get('frequencia'), dados.get('email')))
    connection.commit()

    cursor.close()
    connection.close()
    
    return jsonify({"message": f"Campanha '{dados['titulo']}' criada com sucesso!"}), 201

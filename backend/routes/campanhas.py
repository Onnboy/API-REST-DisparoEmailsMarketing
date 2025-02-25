from flask import Blueprint, request, jsonify

campanhas_bp = Blueprint('campanhas', __name__)

@campanhas_bp.route('/campanhas', methods=['GET'])
def listar_campanhas():
    return jsonify({"message": "Lista de campanhas"}), 200

@campanhas_bp.route('/campanhas', methods=['POST'])
def criar_campanha():
    dados = request.json
    return jsonify({"message": f"Campanha {dados['titulo']} criada!"}), 201


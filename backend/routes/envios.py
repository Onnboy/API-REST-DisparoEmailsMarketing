from flask import Blueprint, request, jsonify

envios_bp = Blueprint('envios', __name__)

@envios_bp.route('/envios', methods=['POST'])
def registrar_envio():
    dados = request.json
    return jsonify({"message": "Envio registrado com sucesso!"}), 201

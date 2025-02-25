from flask import Blueprint, request, jsonify

emails_bp = Blueprint('emails', __name__)

@emails_bp.route('/emails', methods=['GET'])
def listar_emails():
    return jsonify({"message": "Lista de emails"}), 200

@emails_bp.route('/emails', methods=['POST'])
def criar_email():
    dados = request.json
    return jsonify({"message": f"Email {dados['email']} cadastrado com sucesso!"}), 201

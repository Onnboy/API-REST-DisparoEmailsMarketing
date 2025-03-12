from flask import Blueprint, request, jsonify
from backend.config import get_db_connection
from flasgger import swag_from
import re

emails_bp = Blueprint('emails', __name__)

def email_valido(email):
    """Valida se o e-mail possui um formato permitido."""
    dominio = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$'
    return re.match(dominio, email) is not None

@emails_bp.route('/emails', methods=['POST'])
@swag_from({
    "tags": ["E-mails"],
    "summary": "Cadastrar novo e-mail",
    "description": "Cadastra um novo e-mail na lista, com nome associado.",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "example": "exemplo@dominio.com"},
                    "nome": {"type": "string", "example": "João Silva"}
                },
                "required": ["email", "nome"]
            }
        }
    ],
    "responses": {
        201: {
            "description": "E-mail cadastrado com sucesso",
            "schema": {"type": "object", "properties": {"message": {"type": "string"}}}
        },
        400: {
            "description": "Erro de validação ou e-mail já cadastrado",
            "schema": {"type": "object", "properties": {"error": {"type": "string"}}}
        }
    }
})
def criar_email():
    dados = request.json

    if not dados or 'email' not in dados:
        return jsonify({"error": "O campo 'email' é obrigatório!"}), 400

    if not email_valido(dados['email']):
        return jsonify({"error": "Formato de e-mail inválido!"}), 400

    if 'nome' not in dados or not dados['nome'].strip():
        return jsonify({"error": "O campo 'nome' é obrigatório!"}), 400

    email = dados['email'].lower() 
    nome = dados.get('nome', 'Nome não fornecido')

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM emails WHERE email = %s", (email,))
    existe = cursor.fetchone()

    if existe:
        cursor.close()
        connection.close()
        return jsonify({"error": "O e-mail já está cadastrado!"}), 400

    cursor.execute("INSERT INTO emails (email, nome) VALUES (%s, %s) ON DUPLICATE KEY UPDATE nome = VALUES(nome)",
                   (email, nome))
    connection.commit()

    cursor.close()
    connection.close()
    
    return jsonify({"message": f"Email {email} cadastrado com sucesso!"}), 201

@emails_bp.route('/emails', methods=['GET'])
@swag_from({
    "tags": ["E-mails"],
    "summary": "Listar e-mails",
    "description": "Lista todos os e-mails cadastrados.",
    "responses": {
        200: {
            "description": "Lista de e-mails",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "email": {"type": "string"},
                        "nome": {"type": "string"}
                    }
                }
            }
        }
    }
})
def listar_emails():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, email, nome FROM emails")
    emails = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify([{"id": e[0], "email": e[1], "nome": e[2]} for e in emails]), 200

@emails_bp.route('/emails/<int:id>', methods=['PUT'])
@swag_from({
    "tags": ["E-mails"],
    "summary": "Atualizar e-mail ou nome",
    "description": "Atualiza o e-mail e/ou nome de um registro específico.",
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID do e-mail a ser atualizado"
        },
        {
            "name": "body",
            "in": "body",
            "schema": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "example": "novo@email.com"},
                    "nome": {"type": "string", "example": "Novo Nome"}
                }
            }
        }
    ],
    "responses": {
        200: {"description": "E-mail atualizado com sucesso"},
        400: {"description": "Dados inválidos ou formato incorreto"},
        500: {"description": "Erro interno ao atualizar"}
    }
})
def atualizar_email(id):
    dados = request.json

    if not dados:
        return jsonify({"error": "Dados inválidos, envie pelo menos um campo para atualização!"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    campos_para_atualizar = []
    valores = []

    if 'email' in dados:
        if not email_valido(dados['email']):
            return jsonify({"error": "Formato de e-mail inválido!"}), 400
        campos_para_atualizar.append("email = %s")
        valores.append(dados['email'])

    if 'nome' in dados:
        if not dados['nome'].strip():
            return jsonify({"error": "O campo 'nome' não pode estar vazio!"}), 400
        campos_para_atualizar.append("nome = %s")
        valores.append(dados['nome'])

    if not campos_para_atualizar:
        return jsonify({"error": "Nada para atualizar!"}), 400

    valores.append(id)
    query = f"UPDATE emails SET {', '.join(campos_para_atualizar)} WHERE id = %s"
    cursor.execute(query, tuple(valores))
    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({"message": "E-mail atualizado com sucesso!"}), 200

@emails_bp.route('/emails/<int:id>', methods=['DELETE'])
@swag_from({
    "tags": ["E-mails"],
    "summary": "Remover e-mail",
    "description": "Remove um e-mail do banco de dados.",
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID do e-mail a ser removido"
        }
    ],
    "responses": {
        200: {"description": "E-mail removido com sucesso"},
        404: {"description": "E-mail não encontrado"},
        500: {"description": "Erro interno ao remover"}
    }
})
def remover_email(id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM emails WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        connection.close()
        return jsonify({"error": "E-mail não encontrado!"}), 404

    cursor.execute("DELETE FROM emails WHERE id = %s", (id,))
    connection.commit()

    cursor.close()
    connection.close()

    return jsonify({"message": "E-mail removido com sucesso!"}), 200
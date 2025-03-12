from flask import Blueprint, jsonify, request
from backend.config import get_db_connection
from flasgger import swag_from

templates_bp = Blueprint('templates', __name__)

@templates_bp.route('/templates', methods=['POST'])
@swag_from({
    "tags": ["Templates"],
    "summary": "Criar template de e-mail",
    "description": "Cria um novo template de e-mail com nome e conteúdo HTML.",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string", "example": "Promoção Especial"},
                    "conteudo": {"type": "string", "example": "<h1>Olá, {{ nome }}</h1>"}
                },
                "required": ["nome", "conteudo"]
            }
        }
    ],
    "responses": {
        201: {
            "description": "Template criado com sucesso.",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "id": {"type": "integer"}
                }
            }
        },
        400: {"description": "Erro de validação."},
        500: {"description": "Erro interno."}
    }
})
def criar_template():
    dados = request.json
    nome = dados.get('nome')
    conteudo = dados.get('conteudo')

    if not nome or not conteudo:
        return jsonify({"error": "Campos 'nome' e 'conteudo' são obrigatórios."}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "INSERT INTO templates (nome, conteudo) VALUES (%s, %s)", (nome, conteudo)
        )
        connection.commit()
        template_id = cursor.lastrowid  
        return jsonify({
            "message": f"Template '{nome}' criado com sucesso!",
            "id": template_id 
        }), 201
    except Exception as e:
        return jsonify({"error": f"Erro ao criar template: {str(e)}"}), 500
    finally:
        cursor.close()
        connection.close()

@templates_bp.route('/templates', methods=['GET'])
@swag_from({
    "tags": ["Templates"],
    "summary": "Listar templates de e-mail",
    "description": "Lista todos os templates de e-mail cadastrados.",
    "responses": {
        200: {
            "description": "Lista de templates.",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "nome": {"type": "string"},
                        "conteudo": {"type": "string"}
                    }
                }
            }
        },
        500: {"description": "Erro interno."}
    }
})
def listar_templates():
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("SELECT id, nome, conteudo FROM templates")
        templates = cursor.fetchall()

        return jsonify([
            {"id": t[0], "nome": t[1], "conteudo": t[2]} for t in templates
        ]), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao listar templates: {str(e)}"}), 500
    finally:
        cursor.close()
        connection.close()

@templates_bp.route('/templates/<int:id>', methods=['PUT'])
@swag_from({
    "tags": ["Templates"],
    "summary": "Atualizar template de e-mail",
    "description": "Atualiza o nome e/ou o conteúdo de um template existente.",
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "required": True,
            "type": "integer",
            "description": "ID do template a ser atualizado."
        },
        {
            "name": "body",
            "in": "body",
            "schema": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string"},
                    "conteudo": {"type": "string"}
                }
            }
        }
    ],
    "responses": {
        200: {"description": "Template atualizado com sucesso."},
        400: {"description": "Erro de validação."},
        404: {"description": "ID não encontrado."},
        500: {"description": "Erro interno."}
    }
})
def atualizar_template(id):
    dados = request.json
    nome = dados.get('nome')
    conteudo = dados.get('conteudo')

    if not nome and not conteudo:
        return jsonify({"error": "Informe pelo menos 'nome' ou 'conteudo' para atualizar."}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    # Verificar se o ID existe
    cursor.execute("SELECT * FROM templates WHERE id = %s", (id,))
    resultado = cursor.fetchone()

    if not resultado:
        cursor.close()
        connection.close()
        return jsonify({"error": "ID não encontrado"}), 404

    try:
        campos = []
        valores = []

        if nome:
            campos.append("nome = %s")
            valores.append(nome)
        if conteudo:
            campos.append("conteudo = %s")
            valores.append(conteudo)

        valores.append(id)

        query = f"UPDATE templates SET {', '.join(campos)} WHERE id = %s"
        cursor.execute(query, tuple(valores))
        connection.commit()

        return jsonify({"message": "Template atualizado com sucesso!"}), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao atualizar template: {str(e)}"}), 500
    finally:
        cursor.close()
        connection.close()

@templates_bp.route('/templates/<int:id>', methods=['DELETE'])
@swag_from({
    "tags": ["Templates"],
    "summary": "Remover template de e-mail",
    "description": "Remove um template de e-mail do sistema.",
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "required": True,
            "type": "integer",
            "description": "ID do template a ser removido."
        }
    ],
    "responses": {
        200: {"description": "Template removido com sucesso."},
        400: {"description": "ID não encontrado."},
        500: {"description": "Erro interno."}
    }
})
def remover_template(id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM templates WHERE id = %s", (id,))
    resultado = cursor.fetchone()

    if not resultado:
        cursor.close()
        connection.close()
        return jsonify({"error": "ID não encontrado"}), 400

    try:
        cursor.execute("DELETE FROM templates WHERE id = %s", (id,))
        connection.commit()
        return jsonify({"message": "Template removido com sucesso!"}), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao remover template: {str(e)}"}), 500
    finally:
        cursor.close()
        connection.close()

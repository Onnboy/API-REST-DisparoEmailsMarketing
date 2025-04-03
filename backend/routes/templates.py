from flask import Blueprint, jsonify, request
from backend.config import get_db_connection
from flasgger import swag_from
import json

templates_bp = Blueprint('templates', __name__)

@templates_bp.route('/', methods=['GET'])
@swag_from({
    "tags": ["Templates"],
    "summary": "Listar templates",
    "description": "Retorna todos os templates cadastrados no sistema.",
    "responses": {
        200: {
            "description": "Lista de templates",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "nome": {"type": "string"},
                        "descricao": {"type": "string"},
                        "html_content": {"type": "string"},
                        "css_content": {"type": "string"},
                        "created_at": {"type": "string"},
                        "updated_at": {"type": "string"}
                    }
                }
            }
        }
    }
})
def listar_templates():
    """Lista todos os templates registrados no banco de dados."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM templates ORDER BY created_at DESC")
    templates = cursor.fetchall()

    cursor.close()
    connection.close()

    if not templates:
        return jsonify({"message": "Nenhum template encontrado."}), 404

    return jsonify(templates), 200

@templates_bp.route('/', methods=['POST'])
@swag_from({
    "tags": ["Templates"],
    "summary": "Criar template",
    "description": "Cria um novo template de email.",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string", "example": "Template Newsletter"},
                    "descricao": {"type": "string", "example": "Template para newsletter mensal"},
                    "html_content": {"type": "string", "example": "<html><body><h1>Olá {nome}!</h1></body></html>"},
                    "css_content": {"type": "string", "example": "body { font-family: Arial; }"}
                },
                "required": ["nome", "html_content"]
            }
        }
    ],
    "responses": {
        201: {
            "description": "Template criado com sucesso",
            "schema": {
                "type": "object",
                "properties": {
                    "id": {"type": "integer"},
                    "message": {"type": "string"}
                }
            }
        },
        400: {"description": "Dados inválidos"},
        500: {"description": "Erro interno"}
    }
})
def criar_template():
    """Cria um novo template de email."""
    dados = request.json
    
    # Validar campos obrigatórios
    if not dados or 'nome' not in dados or 'html_content' not in dados:
        return jsonify({
            "error": "Os campos 'nome' e 'html_content' são obrigatórios."
        }), 400
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Preparar campos
        campos = ['nome', 'html_content']
        valores = [dados['nome'], dados['html_content']]
        placeholders = ['%s', '%s']
        
        # Adicionar campos opcionais
        if 'descricao' in dados and dados['descricao'] is not None:
            campos.append('descricao')
            valores.append(dados['descricao'])
            placeholders.append('%s')
            
        if 'css_content' in dados and dados['css_content'] is not None:
            campos.append('css_content')
            valores.append(dados['css_content'])
            placeholders.append('%s')
        
        # Construir query
        query = f"""
            INSERT INTO templates ({', '.join(campos)})
            VALUES ({', '.join(placeholders)})
        """
        
        cursor.execute(query, valores)
        template_id = cursor.lastrowid
        connection.commit()
        
        return jsonify({
            "id": template_id,
            "message": "Template criado com sucesso"
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Erro ao criar template: {str(e)}"}), 500
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@templates_bp.route('/<int:id>', methods=['PUT'])
@swag_from({
    "tags": ["Templates"],
    "summary": "Atualizar template",
    "description": "Atualiza um template existente.",
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID do template"
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string"},
                    "descricao": {"type": "string"},
                    "html_content": {"type": "string"},
                    "css_content": {"type": "string"}
                }
            }
        }
    ],
    "responses": {
        200: {"description": "Template atualizado com sucesso"},
        404: {"description": "Template não encontrado"},
        500: {"description": "Erro interno"}
    }
})
def atualizar_template(id):
    """Atualiza um template existente."""
    dados = request.json
    
    if not dados:
        return jsonify({"error": "Nenhum dado fornecido para atualização"}), 400
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Verificar se o template existe
        cursor.execute("SELECT id FROM templates WHERE id = %s", (id,))
        if not cursor.fetchone():
            return jsonify({"error": "Template não encontrado"}), 404
        
        # Preparar campos para atualização
        campos = []
        valores = []
        
        if 'nome' in dados:
            campos.append("nome = %s")
            valores.append(dados['nome'])
            
        if 'descricao' in dados:
            campos.append("descricao = %s")
            valores.append(dados['descricao'])
            
        if 'html_content' in dados:
            campos.append("html_content = %s")
            valores.append(dados['html_content'])
            
        if 'css_content' in dados:
            campos.append("css_content = %s")
            valores.append(dados['css_content'])
        
        if not campos:
            return jsonify({"error": "Nenhum campo para atualizar"}), 400
        
        # Adicionar ID aos valores
        valores.append(id)
        
        # Construir query
        query = f"""
            UPDATE templates 
            SET {', '.join(campos)}
            WHERE id = %s
        """
        
        cursor.execute(query, valores)
        connection.commit()
        
        return jsonify({"message": "Template atualizado com sucesso"}), 200
        
    except Exception as e:
        return jsonify({"error": f"Erro ao atualizar template: {str(e)}"}), 500
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@templates_bp.route('/<int:id>', methods=['DELETE'])
@swag_from({
    "tags": ["Templates"],
    "summary": "Remover template",
    "description": "Remove um template do sistema.",
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID do template"
        }
    ],
    "responses": {
        200: {"description": "Template removido com sucesso"},
        404: {"description": "Template não encontrado"},
        500: {"description": "Erro interno"}
    }
})
def remover_template(id):
    """Remove um template do sistema."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Verificar se o template existe
        cursor.execute("SELECT id FROM templates WHERE id = %s", (id,))
        if not cursor.fetchone():
            return jsonify({"error": "Template não encontrado"}), 404
        
        # Remover o template
        cursor.execute("DELETE FROM templates WHERE id = %s", (id,))
        connection.commit()
        
        return jsonify({"message": "Template removido com sucesso"}), 200
        
    except Exception as e:
        return jsonify({"error": f"Erro ao remover template: {str(e)}"}), 500
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

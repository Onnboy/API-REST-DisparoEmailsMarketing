from flask import Blueprint, request, jsonify
from backend.config import get_db_connection
from flasgger import swag_from
import json

campanhas_bp = Blueprint('campanhas', __name__)

@campanhas_bp.route('/', methods=['GET'])
@swag_from({
    "tags": ["Campanhas"],
    "summary": "Listar campanhas",
    "description": "Retorna todas as campanhas cadastradas no sistema.",
    "responses": {
        200: {
            "description": "Lista de campanhas",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "titulo": {"type": "string"},
                        "descricao": {"type": "string"},
                        "template_id": {"type": "integer"},
                        "segmento_id": {"type": "integer"},
                        "status": {"type": "string"},
                        "created_at": {"type": "string"},
                        "updated_at": {"type": "string"}
                    }
                }
            }
        }
    }
})
def listar_campanhas():
    """Lista todas as campanhas registradas no banco de dados."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM campanhas ORDER BY created_at DESC")
    campanhas = cursor.fetchall()

    cursor.close()
    connection.close()

    if not campanhas:
        return jsonify({"message": "Nenhuma campanha encontrada."}), 404

    return jsonify(campanhas), 200

@campanhas_bp.route('/', methods=['POST'])
@swag_from({
    "tags": ["Campanhas"],
    "summary": "Criar campanha",
    "description": "Cria uma nova campanha de email.",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "titulo": {"type": "string", "example": "Campanha Newsletter"},
                    "descricao": {"type": "string", "example": "Campanha para newsletter mensal"},
                    "template_id": {"type": "integer", "example": 1},
                    "segmento_id": {"type": "integer", "example": 1}
                },
                "required": ["titulo", "template_id"]
            }
        }
    ],
    "responses": {
        201: {
            "description": "Campanha criada com sucesso",
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
def criar_campanha():
    """Cria uma nova campanha de email."""
    dados = request.json

    if not dados or 'titulo' not in dados or 'template_id' not in dados:
        return jsonify({
            "error": "Os campos 'titulo' e 'template_id' são obrigatórios."
        }), 400
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT id FROM templates WHERE id = %s", (dados['template_id'],))
        if not cursor.fetchone():
            return jsonify({"error": "Template não encontrado"}), 404

        if 'segmento_id' in dados and dados['segmento_id'] is not None:
            cursor.execute("SELECT id FROM segmentos WHERE id = %s", (dados['segmento_id'],))
            if not cursor.fetchone():
                return jsonify({"error": "Segmento não encontrado"}), 404

        campos = ['titulo', 'template_id']
        valores = [dados['titulo'], dados['template_id']]
        placeholders = ['%s', '%s']

        if 'descricao' in dados and dados['descricao'] is not None:
            campos.append('descricao')
            valores.append(dados['descricao'])
            placeholders.append('%s')
            
        if 'segmento_id' in dados and dados['segmento_id'] is not None:
            campos.append('segmento_id')
            valores.append(dados['segmento_id'])
            placeholders.append('%s')
        
        query = f"""
            INSERT INTO campanhas ({', '.join(campos)})
            VALUES ({', '.join(placeholders)})
        """
        
        cursor.execute(query, valores)
        campanha_id = cursor.lastrowid
        connection.commit()
        
        return jsonify({
            "id": campanha_id,
            "message": "Campanha criada com sucesso"
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Erro ao criar campanha: {str(e)}"}), 500
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@campanhas_bp.route('/<int:id>', methods=['PUT'])
@swag_from({
    "tags": ["Campanhas"],
    "summary": "Atualizar campanha",
    "description": "Atualiza uma campanha existente.",
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID da campanha"
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "titulo": {"type": "string"},
                    "descricao": {"type": "string"},
                    "template_id": {"type": "integer"},
                    "segmento_id": {"type": "integer"},
                    "status": {"type": "string"}
                }
            }
        }
    ],
    "responses": {
        200: {"description": "Campanha atualizada com sucesso"},
        404: {"description": "Campanha não encontrada"},
        500: {"description": "Erro interno"}
    }
})
def atualizar_campanha(id):
    """Atualiza uma campanha existente."""
    dados = request.json
    
    if not dados:
        return jsonify({"error": "Nenhum dado fornecido para atualização"}), 400
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT id FROM campanhas WHERE id = %s", (id,))
        if not cursor.fetchone():
            return jsonify({"error": "Campanha não encontrada"}), 404

        campos = []
        valores = []
        
        if 'titulo' in dados:
            campos.append("titulo = %s")
            valores.append(dados['titulo'])
            
        if 'descricao' in dados:
            campos.append("descricao = %s")
            valores.append(dados['descricao'])
            
        if 'template_id' in dados:
            cursor.execute("SELECT id FROM templates WHERE id = %s", (dados['template_id'],))
            if not cursor.fetchone():
                return jsonify({"error": "Template não encontrado"}), 404
            campos.append("template_id = %s")
            valores.append(dados['template_id'])
            
        if 'segmento_id' in dados:
            if dados['segmento_id'] is not None:
                cursor.execute("SELECT id FROM segmentos WHERE id = %s", (dados['segmento_id'],))
                if not cursor.fetchone():
                    return jsonify({"error": "Segmento não encontrado"}), 404
            campos.append("segmento_id = %s")
            valores.append(dados['segmento_id'])
            
        if 'status' in dados:
            campos.append("status = %s")
            valores.append(dados['status'])
        
        if not campos:
            return jsonify({"error": "Nenhum campo para atualizar"}), 400

        valores.append(id)

        query = f"""
            UPDATE campanhas 
            SET {', '.join(campos)}
            WHERE id = %s
        """
        
        cursor.execute(query, valores)
        connection.commit()
        
        return jsonify({"message": "Campanha atualizada com sucesso"}), 200
        
    except Exception as e:
        return jsonify({"error": f"Erro ao atualizar campanha: {str(e)}"}), 500
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@campanhas_bp.route('/<int:id>', methods=['DELETE'])
@swag_from({
    "tags": ["Campanhas"],
    "summary": "Remover campanha",
    "description": "Remove uma campanha do sistema.",
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID da campanha"
        }
    ],
    "responses": {
        200: {"description": "Campanha removida com sucesso"},
        404: {"description": "Campanha não encontrada"},
        500: {"description": "Erro interno"}
    }
})
def remover_campanha(id):
    """Remove uma campanha do sistema."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT id FROM campanhas WHERE id = %s", (id,))
        if not cursor.fetchone():
            return jsonify({"error": "Campanha não encontrada"}), 404

        cursor.execute("DELETE FROM campanhas WHERE id = %s", (id,))
        connection.commit()
        
        return jsonify({"message": "Campanha removida com sucesso"}), 200
        
    except Exception as e:
        return jsonify({"error": f"Erro ao remover campanha: {str(e)}"}), 500
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

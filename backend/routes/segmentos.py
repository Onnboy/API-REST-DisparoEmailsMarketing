from flask import Blueprint, request, jsonify
from backend.config import get_db_connection
from flasgger import swag_from
import json

segmentos_bp = Blueprint('segmentos', __name__)

@segmentos_bp.route('/', methods=['GET'])
@swag_from({
    "tags": ["Segmentos"],
    "summary": "Listar segmentos",
    "description": "Retorna todos os segmentos cadastrados no sistema.",
    "responses": {
        200: {
            "description": "Lista de segmentos",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "nome": {"type": "string"},
                        "descricao": {"type": "string"},
                        "criterios": {"type": "object"},
                        "total_contatos": {"type": "integer"}
                    }
                }
            }
        }
    }
})
def listar_segmentos():
    """Lista todos os segmentos registrados no banco de dados."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.*, COUNT(cs.contato_id) as total_contatos
        FROM segmentos s
        LEFT JOIN contatos_segmentos cs ON s.id = cs.segmento_id
        GROUP BY s.id
    """)
    segmentos = cursor.fetchall()

    cursor.close()
    connection.close()

    if not segmentos:
        return jsonify({"message": "Nenhum segmento encontrado."}), 404

    return jsonify(segmentos), 200

@segmentos_bp.route('/', methods=['POST'])
@swag_from({
    "tags": ["Segmentos"],
    "summary": "Criar segmento",
    "description": "Cria um novo segmento de contatos.",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string", "example": "Clientes VIP"},
                    "descricao": {"type": "string", "example": "Segmento de clientes VIP"},
                    "criterios": {"type": "object"}
                },
                "required": ["nome"]
            }
        }
    ],
    "responses": {
        201: {
            "description": "Segmento criado com sucesso",
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
def criar_segmento():
    """Cria um novo segmento de contatos."""
    dados = request.json
    
    # Validar campos obrigatórios
    if not dados or 'nome' not in dados:
        return jsonify({
            "error": "O campo 'nome' é obrigatório."
        }), 400
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Preparar campos
        campos = ['nome']
        valores = [dados['nome']]
        placeholders = ['%s']
        
        # Adicionar campos opcionais
        if 'descricao' in dados and dados['descricao'] is not None:
            campos.append('descricao')
            valores.append(dados['descricao'])
            placeholders.append('%s')
            
        if 'criterios' in dados and dados['criterios'] is not None:
            campos.append('criterios')
            valores.append(json.dumps(dados['criterios']))
            placeholders.append('%s')
        
        # Construir query
        query = f"""
            INSERT INTO segmentos ({', '.join(campos)})
            VALUES ({', '.join(placeholders)})
        """
        
        cursor.execute(query, valores)
        segmento_id = cursor.lastrowid
        connection.commit()
        
        return jsonify({
            "id": segmento_id,
            "message": "Segmento criado com sucesso"
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Erro ao criar segmento: {str(e)}"}), 500
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@segmentos_bp.route('/<int:id>', methods=['PUT'])
@swag_from({
    "tags": ["Segmentos"],
    "summary": "Atualizar segmento",
    "description": "Atualiza um segmento existente.",
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID do segmento"
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
                    "criterios": {"type": "object"}
                }
            }
        }
    ],
    "responses": {
        200: {"description": "Segmento atualizado com sucesso"},
        404: {"description": "Segmento não encontrado"},
        500: {"description": "Erro interno"}
    }
})
def atualizar_segmento(id):
    """Atualiza um segmento existente."""
    dados = request.json
    
    if not dados:
        return jsonify({"error": "Nenhum dado fornecido para atualização"}), 400
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Verificar se o segmento existe
        cursor.execute("SELECT id FROM segmentos WHERE id = %s", (id,))
        if not cursor.fetchone():
            return jsonify({"error": "Segmento não encontrado"}), 404
        
        # Preparar campos para atualização
        campos = []
        valores = []
        
        if 'nome' in dados:
            campos.append("nome = %s")
            valores.append(dados['nome'])
            
        if 'descricao' in dados:
            campos.append("descricao = %s")
            valores.append(dados['descricao'])
            
        if 'criterios' in dados:
            campos.append("criterios = %s")
            valores.append(json.dumps(dados['criterios']))
        
        if not campos:
            return jsonify({"error": "Nenhum campo para atualizar"}), 400
        
        # Adicionar ID aos valores
        valores.append(id)
        
        # Construir query
        query = f"""
            UPDATE segmentos 
            SET {', '.join(campos)}
            WHERE id = %s
        """
        
        cursor.execute(query, valores)
        connection.commit()
        
        return jsonify({"message": "Segmento atualizado com sucesso"}), 200
        
    except Exception as e:
        return jsonify({"error": f"Erro ao atualizar segmento: {str(e)}"}), 500
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@segmentos_bp.route('/<int:id>', methods=['DELETE'])
@swag_from({
    "tags": ["Segmentos"],
    "summary": "Remover segmento",
    "description": "Remove um segmento do sistema.",
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID do segmento"
        }
    ],
    "responses": {
        200: {"description": "Segmento removido com sucesso"},
        404: {"description": "Segmento não encontrado"},
        500: {"description": "Erro interno"}
    }
})
def remover_segmento(id):
    """Remove um segmento do sistema."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Verificar se o segmento existe
        cursor.execute("SELECT id FROM segmentos WHERE id = %s", (id,))
        if not cursor.fetchone():
            return jsonify({"error": "Segmento não encontrado"}), 404
        
        # Remover associações com contatos
        cursor.execute("DELETE FROM contatos_segmentos WHERE segmento_id = %s", (id,))
        
        # Remover o segmento
        cursor.execute("DELETE FROM segmentos WHERE id = %s", (id,))
        connection.commit()
        
        return jsonify({"message": "Segmento removido com sucesso"}), 200
        
    except Exception as e:
        return jsonify({"error": f"Erro ao remover segmento: {str(e)}"}), 500
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@segmentos_bp.route('/<int:id>/contatos', methods=['GET'])
@swag_from({
    "tags": ["Segmentos"],
    "summary": "Listar contatos do segmento",
    "description": "Retorna todos os contatos associados a um segmento.",
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID do segmento"
        }
    ],
    "responses": {
        200: {
            "description": "Lista de contatos do segmento",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "email": {"type": "string"},
                        "nome": {"type": "string"},
                        "cargo": {"type": "string"},
                        "empresa": {"type": "string"},
                        "telefone": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "grupo": {"type": "string"}
                    }
                }
            }
        },
        404: {"description": "Segmento não encontrado"}
    }
})
def listar_contatos_segmento(id):
    """Lista todos os contatos associados a um segmento."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Verificar se o segmento existe
    cursor.execute("SELECT id FROM segmentos WHERE id = %s", (id,))
    if not cursor.fetchone():
        cursor.close()
        connection.close()
        return jsonify({"error": "Segmento não encontrado"}), 404

    # Buscar contatos do segmento
    cursor.execute("""
        SELECT c.* 
        FROM contatos c
        JOIN contatos_segmentos cs ON c.id = cs.contato_id
        WHERE cs.segmento_id = %s
    """, (id,))
    contatos = cursor.fetchall()

    cursor.close()
    connection.close()

    if not contatos:
        return jsonify({"message": "Nenhum contato encontrado neste segmento."}), 404

    return jsonify(contatos), 200 
from flask import Blueprint, request, jsonify
from backend.config import get_db_connection
from flasgger import swag_from
import json

segmentacao_bp = Blueprint('segmentacao', __name__)

@segmentacao_bp.route('/segmentos', methods=['POST'])
@swag_from({
    "tags": ["Segmentação"],
    "summary": "Criar segmento",
    "description": "Cria um novo segmento de contatos com nome e critérios de filtro.",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string", "example": "Clientes Ativos"},
                    "criterios": {
                        "type": "object",
                        "example": {"cargo": "Diretor", "empresa": "Tech Solutions"}
                    }
                },
                "required": ["nome", "criterios"]
            }
        }
    ],
    "responses": {
        201: {
            "description": "Segmento criado com sucesso",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                    "id": {"type": "integer"},
                    "total_contatos": {"type": "integer"}
                }
            }
        },
        400: {"description": "Erro de validação"},
        500: {"description": "Erro interno"}
    }
})
def criar_segmento():
    dados = request.get_json()
    
    if not dados or 'nome' not in dados or 'criterios' not in dados:
        return jsonify({'error': 'Nome e critérios são obrigatórios'}), 400
        
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Insere o segmento
        cursor.execute(
            'INSERT INTO segmentos (nome, criterios, usuario_id) VALUES (%s, %s, %s)',
            (dados['nome'], json.dumps(dados['criterios']), dados.get('usuario_id', 1))
        )
        
        segmento_id = cursor.lastrowid
        
        # Busca contatos que atendem aos critérios
        query = 'SELECT id FROM contatos WHERE 1=1'
        params = []
        
        # Adiciona cada critério à query
        for campo, valor in dados['criterios'].items():
            if campo in ['id', 'email', 'nome', 'cargo', 'empresa', 'telefone', 'grupo', 'status']:
                query += f' AND {campo} = %s'
                params.append(valor)
            elif campo == 'tags':
                if isinstance(valor, list):
                    # Se for uma lista de tags, procura por todas
                    for tag in valor:
                        query += ' AND tags LIKE %s'
                        params.append(f'%{tag}%')
                else:
                    # Se for uma única tag
                    query += ' AND tags LIKE %s'
                    params.append(f'%{valor}%')
        
        cursor.execute(query, params)
        contatos = cursor.fetchall()
        
        # Adiciona contatos ao segmento
        for contato in contatos:
            cursor.execute(
                'INSERT INTO contatos_segmentos (contato_id, segmento_id) VALUES (%s, %s)',
                (contato[0], segmento_id)
            )
        
        connection.commit()
        
        return jsonify({
            'message': 'Segmento criado com sucesso',
            'id': segmento_id,
            'total_contatos': len(contatos)
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@segmentacao_bp.route('/segmentos/<int:segmento_id>/contatos', methods=['GET'])
@swag_from({
    "tags": ["Segmentação"],
    "summary": "Listar contatos do segmento",
    "description": "Lista todos os contatos que se enquadram nas condições do segmento.",
    "parameters": [
        {
            "name": "segmento_id",
            "in": "path",
            "required": True,
            "type": "integer",
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
                        "nome": {"type": "string"},
                        "email": {"type": "string"},
                        "cargo": {"type": "string"},
                        "empresa": {"type": "string"},
                        "telefone": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "grupo": {"type": "string"},
                        "status": {"type": "string"},
                        "created_at": {"type": "string", "format": "date-time"}
                    }
                }
            }
        },
        404: {"description": "Segmento não encontrado"},
        500: {"description": "Erro interno"}
    }
})
def listar_contatos_segmento(segmento_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Busca o segmento
        cursor.execute('SELECT * FROM segmentos WHERE id = %s', (segmento_id,))
        segmento = cursor.fetchone()
        
        if not segmento:
            return jsonify({'error': 'Segmento não encontrado'}), 404
            
        # Constrói a query baseada nos critérios
        criterios = json.loads(segmento['criterios'])
        
        query = 'SELECT * FROM contatos WHERE 1=1'
        params = []
        
        # Adiciona cada critério à query
        for campo, valor in criterios.items():
            if campo in ['id', 'email', 'nome', 'cargo', 'empresa', 'telefone', 'grupo', 'status']:
                query += f' AND {campo} = %s'
                params.append(valor)
            elif campo == 'tags':
                if isinstance(valor, list):
                    # Se for uma lista de tags, procura por todas
                    for tag in valor:
                        query += ' AND tags LIKE %s'
                        params.append(f'%{tag}%')
                else:
                    # Se for uma única tag
                    query += ' AND tags LIKE %s'
                    params.append(f'%{valor}%')
        
        cursor.execute(query, params)
        contatos = cursor.fetchall()
        
        # Converte as tags de JSON string para lista
        for contato in contatos:
            if contato['tags']:
                contato['tags'] = json.loads(contato['tags'])
        
        return jsonify(contatos), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@segmentacao_bp.route('/segmentos', methods=['GET'])
@swag_from({
    "tags": ["Segmentação"],
    "summary": "Listar segmentos",
    "description": "Lista todos os segmentos cadastrados.",
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
                        "criterios": {"type": "object"},
                        "usuario_id": {"type": "integer"},
                        "created_at": {"type": "string", "format": "date-time"}
                    }
                }
            }
        },
        500: {"description": "Erro interno"}
    }
})
def listar_segmentos():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM segmentos ORDER BY created_at DESC')
        segmentos = cursor.fetchall()
        
        return jsonify(segmentos), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@segmentacao_bp.route('/segmentos/criterios', methods=['GET'])
@swag_from({
    "tags": ["Segmentação"],
    "summary": "Listar critérios disponíveis",
    "description": "Lista todos os critérios disponíveis para segmentação de contatos.",
    "responses": {
        200: {
            "description": "Lista de critérios disponíveis",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "nome": {"type": "string"},
                        "tipo": {"type": "string"},
                        "descricao": {"type": "string"},
                        "valores": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    }
                }
            }
        }
    }
})
def listar_criterios_disponiveis():
    """Lista os critérios disponíveis para segmentação."""
    criterios = [
        {
            'nome': 'grupo',
            'tipo': 'string',
            'descricao': 'Grupo do contato',
            'valores': ['grupo1', 'grupo2', 'grupo3']
        },
        {
            'nome': 'tags',
            'tipo': 'string',
            'descricao': 'Tags do contato (busca parcial)'
        },
        {
            'nome': 'status',
            'tipo': 'string',
            'descricao': 'Status do contato',
            'valores': ['ativo', 'inativo', 'bounced', 'unsubscribed']
        }
    ]
    return jsonify(criterios), 200

@segmentacao_bp.route('/segmentos/<int:segmento_id>', methods=['PUT'])
@swag_from({
    "tags": ["Segmentação"],
    "summary": "Atualizar segmento",
    "description": "Atualiza um segmento existente.",
    "parameters": [
        {
            "name": "segmento_id",
            "in": "path",
            "required": True,
            "type": "integer",
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
                    "criterios": {"type": "object"}
                }
            }
        }
    ],
    "responses": {
        200: {
            "description": "Segmento atualizado com sucesso",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"}
                }
            }
        },
        404: {"description": "Segmento não encontrado"},
        500: {"description": "Erro interno"}
    }
})
def atualizar_segmento(segmento_id):
    dados = request.get_json()
    
    if not dados:
        return jsonify({'error': 'Dados não fornecidos'}), 400
        
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Verifica se o segmento existe
        cursor.execute('SELECT id FROM segmentos WHERE id = %s', (segmento_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Segmento não encontrado'}), 404
            
        # Atualiza o segmento
        update_fields = []
        values = []
        
        if 'nome' in dados:
            update_fields.append('nome = %s')
            values.append(dados['nome'])
            
        if 'criterios' in dados:
            update_fields.append('criterios = %s')
            values.append(json.dumps(dados['criterios']))
            
        if not update_fields:
            return jsonify({'error': 'Nenhum campo para atualizar'}), 400
            
        values.append(segmento_id)
        
        query = f"UPDATE segmentos SET {', '.join(update_fields)} WHERE id = %s"
        cursor.execute(query, values)
        
        connection.commit()
        
        return jsonify({'message': 'Segmento atualizado com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@segmentacao_bp.route('/segmentos/<int:segmento_id>', methods=['DELETE'])
@swag_from({
    "tags": ["Segmentação"],
    "summary": "Remover segmento",
    "description": "Remove um segmento existente.",
    "parameters": [
        {
            "name": "segmento_id",
            "in": "path",
            "required": True,
            "type": "integer",
            "description": "ID do segmento"
        }
    ],
    "responses": {
        200: {
            "description": "Segmento removido com sucesso",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"}
                }
            }
        },
        404: {"description": "Segmento não encontrado"},
        500: {"description": "Erro interno"}
    }
})
def remover_segmento(segmento_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Verifica se o segmento existe
        cursor.execute('SELECT id FROM segmentos WHERE id = %s', (segmento_id,))
        if not cursor.fetchone():
            return jsonify({'error': 'Segmento não encontrado'}), 404
            
        # Remove o segmento
        cursor.execute('DELETE FROM segmentos WHERE id = %s', (segmento_id,))
        connection.commit()
        
        return jsonify({'message': 'Segmento removido com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close() 
from flask import Blueprint, request, jsonify
from backend.config import get_db_connection
from flasgger import swag_from
import json
from datetime import datetime

agendamentos_bp = Blueprint('agendamentos', __name__)

@agendamentos_bp.route('/', methods=['GET'])
@swag_from({
    "tags": ["Agendamentos"],
    "summary": "Listar agendamentos",
    "description": "Retorna todos os agendamentos cadastrados no sistema.",
    "responses": {
        200: {
            "description": "Lista de agendamentos",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "template_id": {"type": "integer"},
                        "segmento_id": {"type": "integer"},
                        "assunto": {"type": "string"},
                        "data_envio": {"type": "string"},
                        "dados_padrao": {"type": "object"},
                        "status": {"type": "string"},
                        "created_at": {"type": "string"},
                        "updated_at": {"type": "string"}
                    }
                }
            }
        }
    }
})
def listar_agendamentos():
    """Lista todos os agendamentos registrados no banco de dados."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM agendamentos ORDER BY data_envio ASC")
        agendamentos = cursor.fetchall()

        if not agendamentos:
            return jsonify({"message": "Nenhum agendamento encontrado."}), 404

        return jsonify(agendamentos)
    except Exception as e:
        return jsonify({"error": f"Erro ao listar agendamentos: {str(e)}"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@agendamentos_bp.route('/', methods=['POST'])
@swag_from({
    "tags": ["Agendamentos"],
    "summary": "Criar agendamento",
    "description": "Cria um novo agendamento de envio de email.",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "template_id": {"type": "integer", "example": 1},
                    "segmento_id": {"type": "integer", "example": 1},
                    "assunto": {"type": "string", "example": "Newsletter Mensal"},
                    "data_envio": {"type": "string", "format": "date-time", "example": "2024-03-20T10:00:00"},
                    "dados_padrao": {"type": "object", "example": {"nome": "Cliente"}}
                },
                "required": ["template_id", "segmento_id", "assunto", "data_envio"]
            }
        }
    ],
    "responses": {
        201: {
            "description": "Agendamento criado com sucesso",
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
def criar_agendamento():
    """Cria um novo agendamento de envio de email."""
    try:
        data = request.get_json()
        
        # Validação dos campos obrigatórios
        required_fields = ['template_id', 'segmento_id', 'assunto', 'data_envio']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo '{field}' é obrigatório"}), 400
        
        # Validação da data de envio
        try:
            data_envio = datetime.fromisoformat(data['data_envio'].replace('Z', '+00:00'))
            if data_envio < datetime.now():
                return jsonify({"error": "Data de envio não pode ser no passado"}), 400
        except ValueError:
            return jsonify({"error": "Formato de data inválido. Use ISO 8601 (YYYY-MM-DDTHH:MM:SS)"}), 400
        
        # Validação dos dados padrão
        dados_padrao = data.get('dados_padrao', {})
        if not isinstance(dados_padrao, dict):
            return jsonify({"error": "Dados padrão devem ser um objeto JSON"}), 400
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("""
            INSERT INTO agendamentos (template_id, segmento_id, assunto, data_envio, dados_padrao)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            data['template_id'],
            data['segmento_id'],
            data['assunto'],
            data_envio,
            json.dumps(dados_padrao)
        ))
        
        agendamento_id = cursor.lastrowid
        connection.commit()
        
        return jsonify({
            "id": agendamento_id,
            "message": "Agendamento criado com sucesso"
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Erro ao criar agendamento: {str(e)}"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@agendamentos_bp.route('/<int:id>', methods=['PUT'])
@swag_from({
    "tags": ["Agendamentos"],
    "summary": "Atualizar agendamento",
    "description": "Atualiza um agendamento existente.",
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID do agendamento"
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "template_id": {"type": "integer"},
                    "segmento_id": {"type": "integer"},
                    "assunto": {"type": "string"},
                    "data_envio": {"type": "string", "format": "date-time"},
                    "dados_padrao": {"type": "object"},
                    "status": {"type": "string"}
                }
            }
        }
    ],
    "responses": {
        200: {"description": "Agendamento atualizado com sucesso"},
        404: {"description": "Agendamento não encontrado"},
        500: {"description": "Erro interno"}
    }
})
def atualizar_agendamento(id):
    """Atualiza um agendamento existente."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Nenhum dado fornecido para atualização"}), 400
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Verificar se o agendamento existe
        cursor.execute("SELECT * FROM agendamentos WHERE id = %s", (id,))
        agendamento = cursor.fetchone()
        
        if not agendamento:
            return jsonify({"error": "Agendamento não encontrado"}), 404
        
        # Construir query de atualização
        update_fields = []
        params = []
        
        if 'template_id' in data:
            update_fields.append("template_id = %s")
            params.append(data['template_id'])
        
        if 'segmento_id' in data:
            update_fields.append("segmento_id = %s")
            params.append(data['segmento_id'])
        
        if 'assunto' in data:
            update_fields.append("assunto = %s")
            params.append(data['assunto'])
        
        if 'data_envio' in data:
            try:
                data_envio = datetime.fromisoformat(data['data_envio'].replace('Z', '+00:00'))
                if data_envio < datetime.now():
                    return jsonify({"error": "Data de envio não pode ser no passado"}), 400
                update_fields.append("data_envio = %s")
                params.append(data_envio)
            except ValueError:
                return jsonify({"error": "Formato de data inválido. Use ISO 8601 (YYYY-MM-DDTHH:MM:SS)"}), 400
        
        if 'dados_padrao' in data:
            if not isinstance(data['dados_padrao'], dict):
                return jsonify({"error": "Dados padrão devem ser um objeto JSON"}), 400
            update_fields.append("dados_padrao = %s")
            params.append(json.dumps(data['dados_padrao']))
        
        if 'status' in data:
            if data['status'] not in ['pendente', 'enviado', 'erro']:
                return jsonify({"error": "Status inválido. Use 'pendente', 'enviado' ou 'erro'"}), 400
            update_fields.append("status = %s")
            params.append(data['status'])
        
        if not update_fields:
            return jsonify({"error": "Nenhum campo válido para atualização"}), 400
        
        # Adicionar data de atualização
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        
        # Adicionar ID aos parâmetros
        params.append(id)
        
        # Executar atualização
        query = f"UPDATE agendamentos SET {', '.join(update_fields)} WHERE id = %s"
        cursor.execute(query, params)
        connection.commit()
        
        return jsonify({"message": "Agendamento atualizado com sucesso"})
        
    except Exception as e:
        return jsonify({"error": f"Erro ao atualizar agendamento: {str(e)}"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@agendamentos_bp.route('/<int:id>', methods=['DELETE'])
@swag_from({
    "tags": ["Agendamentos"],
    "summary": "Remover agendamento",
    "description": "Remove um agendamento do sistema.",
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID do agendamento"
        }
    ],
    "responses": {
        200: {"description": "Agendamento removido com sucesso"},
        404: {"description": "Agendamento não encontrado"},
        500: {"description": "Erro interno"}
    }
})
def remover_agendamento(id):
    """Remove um agendamento do sistema."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("DELETE FROM agendamentos WHERE id = %s", (id,))
        connection.commit()
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Agendamento não encontrado"}), 404
        
        return jsonify({"message": "Agendamento removido com sucesso"})
        
    except Exception as e:
        return jsonify({"error": f"Erro ao remover agendamento: {str(e)}"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@agendamentos_bp.route('/<int:agendamento_id>/', methods=['GET'])
def obter_agendamento(agendamento_id):
    """Obtém um agendamento específico."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Buscar agendamento
        cursor.execute("""
            SELECT 
                a.*,
                t.nome as template_nome,
                s.nome as segmento_nome
            FROM agendamentos a
            LEFT JOIN templates t ON a.template_id = t.id
            LEFT JOIN segmentos s ON a.segmento_id = s.id
            WHERE a.id = %s
        """, (agendamento_id,))
        
        agendamento = cursor.fetchone()
        
        if not agendamento:
            return jsonify({"error": "Agendamento não encontrado"}), 404
            
        return jsonify(agendamento)
    except Exception as e:
        return jsonify({"error": f"Erro ao obter agendamento: {str(e)}"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close() 
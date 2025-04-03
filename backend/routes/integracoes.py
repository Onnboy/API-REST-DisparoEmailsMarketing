from flask import Blueprint, request, jsonify
from backend.database import get_db_connection
from backend.services.email_service import get_smtp_config, update_smtp_config
import json
from flasgger import swag_from
import requests
from backend.services.integracoes_service import atualizar_integracao, buscar_integracao, deletar_integracao, testar_integracao

integracoes_bp = Blueprint('integracoes', __name__)

@integracoes_bp.route('/', methods=['GET'])
@swag_from({
    "tags": ["Integrações"],
    "summary": "Listar integrações",
    "description": "Retorna a lista de todas as integrações.",
    "parameters": [
        {
            "name": "tipo",
            "in": "query",
            "type": "string",
            "required": False,
            "description": "Filtrar por tipo (smtp, api, webhook)"
        },
        {
            "name": "status",
            "in": "query",
            "type": "string",
            "required": False,
            "description": "Filtrar por status (ativo, inativo)"
        }
    ],
    "responses": {
        200: {"description": "Lista de integrações"},
        500: {"description": "Erro interno"}
    }
})
def listar_integracoes():
    """Lista todas as integrações configuradas."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM integracoes ORDER BY created_at DESC")
        integracoes = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(integracoes)
    except Exception as e:
        return jsonify({"error": f"Erro ao listar integrações: {str(e)}"}), 500

@integracoes_bp.route('/', methods=['POST'])
@swag_from({
    "tags": ["Integrações"],
    "summary": "Criar integração",
    "description": "Cria uma nova integração.",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "tipo": {"type": "string", "enum": ["smtp", "webhook"]},
                    "configuracao": {"type": "object"}
                },
                "required": ["tipo", "configuracao"]
            }
        }
    ],
    "responses": {
        201: {"description": "Integração criada com sucesso"},
        400: {"description": "Dados inválidos"},
        500: {"description": "Erro interno"}
    }
})
def criar_integracao():
    """Cria uma nova integração."""
    try:
        data = request.get_json()
        
        # Validação dos campos obrigatórios
        if not data or 'tipo' not in data or 'configuracao' not in data:
            return jsonify({"error": "Campos 'tipo' e 'configuracao' são obrigatórios"}), 400
        
        # Validação do tipo de integração
        if data['tipo'] not in ['smtp', 'webhook']:
            return jsonify({"error": "Tipo de integração inválido. Use 'smtp' ou 'webhook'"}), 400
        
        # Validação da configuração
        if not isinstance(data['configuracao'], dict):
            return jsonify({"error": "Configuração deve ser um objeto JSON"}), 400
        
        # Validações específicas por tipo
        if data['tipo'] == 'smtp':
            required_fields = ['host', 'port', 'username', 'password']
            for field in required_fields:
                if field not in data['configuracao']:
                    return jsonify({"error": f"Campo '{field}' é obrigatório para integração SMTP"}), 400
        elif data['tipo'] == 'webhook':
            if 'url' not in data['configuracao']:
                return jsonify({"error": "Campo 'url' é obrigatório para integração Webhook"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verifica se já existe uma integração do mesmo tipo
        cursor.execute("SELECT id FROM integracoes WHERE tipo = %s", (data['tipo'],))
        existing = cursor.fetchone()
        
        if existing:
            # Atualiza a integração existente
            cursor.execute("""
                UPDATE integracoes 
                SET configuracao = %s, updated_at = CURRENT_TIMESTAMP 
                WHERE tipo = %s
            """, (json.dumps(data['configuracao']), data['tipo']))
            integracao_id = existing[0]
        else:
            # Cria nova integração
            cursor.execute("""
                INSERT INTO integracoes (tipo, configuracao) 
                VALUES (%s, %s)
            """, (data['tipo'], json.dumps(data['configuracao'])))
            integracao_id = cursor.lastrowid
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            "id": integracao_id,
            "tipo": data['tipo'],
            "configuracao": data['configuracao']
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Erro ao criar integração: {str(e)}"}), 500

@integracoes_bp.route('/<int:id>', methods=['GET'])
@swag_from({
    "tags": ["Integrações"],
    "summary": "Buscar integração",
    "description": "Retorna os detalhes de uma integração específica.",
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID da integração"
        }
    ],
    "responses": {
        200: {"description": "Detalhes da integração"},
        404: {"description": "Integração não encontrada"}
    }
})
def obter_integracao(id):
    """Obtém os detalhes de uma integração específica."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM integracoes WHERE id = %s", (id,))
        integracao = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not integracao:
            return jsonify({"error": "Integração não encontrada"}), 404
            
        return jsonify(integracao)
    except Exception as e:
        return jsonify({"error": f"Erro ao obter integração: {str(e)}"}), 500

@integracoes_bp.route('/<int:id>', methods=['DELETE'])
@swag_from({
    "tags": ["Integrações"],
    "summary": "Remover integração",
    "description": "Remove uma integração específica.",
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID da integração"
        }
    ],
    "responses": {
        204: {"description": "Integração removida com sucesso"},
        404: {"description": "Integração não encontrada"}
    }
})
def remover_integracao(id):
    """Remove uma integração específica."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM integracoes WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Integração não encontrada"}), 404
            
        return '', 204
    except Exception as e:
        return jsonify({"error": f"Erro ao remover integração: {str(e)}"}), 500

@integracoes_bp.route('/integracoes', methods=['GET'])
@swag_from({
    "tags": ["Integrações"],
    "summary": "Listar integrações",
    "description": "Retorna a lista de todas as integrações.",
    "parameters": [
        {
            "name": "tipo",
            "in": "query",
            "type": "string",
            "required": False,
            "description": "Filtrar por tipo (smtp, api, webhook)"
        },
        {
            "name": "status",
            "in": "query",
            "type": "string",
            "required": False,
            "description": "Filtrar por status (ativo, inativo)"
        }
    ],
    "responses": {
        200: {"description": "Lista de integrações"},
        500: {"description": "Erro interno"}
    }
})
def listar():
    tipo = request.args.get('tipo')
    status = request.args.get('status')
    
    integracoes = listar_integracoes(tipo, status)
    if integracoes is not None:
        return jsonify(integracoes), 200
    else:
        return jsonify({"error": "Erro ao listar integrações"}), 500

@integracoes_bp.route('/integracoes/<int:id>', methods=['GET'])
@swag_from({
    "tags": ["Integrações"],
    "summary": "Buscar integração",
    "description": "Retorna os detalhes de uma integração específica.",
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID da integração"
        }
    ],
    "responses": {
        200: {"description": "Detalhes da integração"},
        404: {"description": "Integração não encontrada"}
    }
})
def buscar(id):
    integracao = buscar_integracao(id)
    if integracao:
        return jsonify(integracao), 200
    else:
        return jsonify({"error": "Integração não encontrada"}), 404

@integracoes_bp.route('/integracoes/<int:id>', methods=['PUT'])
@swag_from({
    "tags": ["Integrações"],
    "summary": "Atualizar integração",
    "description": "Atualiza uma integração existente.",
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID da integração"
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "nome": {"type": "string"},
                    "tipo": {"type": "string", "enum": ["smtp", "api", "webhook"]},
                    "configuracoes": {"type": "object"},
                    "status": {"type": "string", "enum": ["ativo", "inativo"]}
                }
            }
        }
    ],
    "responses": {
        200: {"description": "Integração atualizada com sucesso"},
        404: {"description": "Integração não encontrada"}
    }
})
def atualizar(id):
    dados = request.json
    if not dados:
        return jsonify({"error": "Dados não fornecidos"}), 400
        
    # Verificar se integração existe
    if not buscar_integracao(id):
        return jsonify({"error": "Integração não encontrada"}), 404
        
    # Validar tipo se fornecido
    if 'tipo' in dados:
        tipos_validos = ['smtp', 'crm', 'analytics']
        if dados['tipo'] not in tipos_validos:
            return jsonify({"error": f"Tipo deve ser um dos seguintes: {', '.join(tipos_validos)}"}), 400
            
    # Validar status se fornecido
    if 'status' in dados:
        status_validos = ['ativo', 'inativo']
        if dados['status'] not in status_validos:
            return jsonify({"error": f"Status deve ser um dos seguintes: {', '.join(status_validos)}"}), 400
            
    # Atualizar integração
    sucesso = atualizar_integracao(
        id,
        nome=dados.get('nome'),
        tipo=dados.get('tipo'),
        configuracoes=dados.get('configuracoes'),
        status=dados.get('status')
    )
    
    if sucesso:
        return jsonify({"message": "Integração atualizada com sucesso"}), 200
    else:
        return jsonify({"error": "Erro ao atualizar integração"}), 500

@integracoes_bp.route('/integracoes/<int:id>', methods=['DELETE'])
@swag_from({
    "tags": ["Integrações"],
    "summary": "Deletar integração",
    "description": "Remove uma integração existente.",
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID da integração"
        }
    ],
    "responses": {
        200: {"description": "Integração removida com sucesso"},
        404: {"description": "Integração não encontrada"}
    }
})
def deletar(id):
    # Verificar se integração existe
    if not buscar_integracao(id):
        return jsonify({"error": "Integração não encontrada"}), 404
        
    # Deletar integração
    if deletar_integracao(id):
        return jsonify({"message": "Integração removida com sucesso"}), 200
    else:
        return jsonify({"error": "Erro ao remover integração"}), 500

@integracoes_bp.route('/integracoes/<int:id>/testar', methods=['POST'])
@swag_from({
    "tags": ["Integrações"],
    "summary": "Testar integração",
    "description": "Testa a conexão com uma integração específica.",
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID da integração"
        }
    ],
    "responses": {
        200: {"description": "Teste realizado com sucesso"},
        404: {"description": "Integração não encontrada"}
    }
})
def testar(id):
    # Verificar se integração existe
    if not buscar_integracao(id):
        return jsonify({"error": "Integração não encontrada"}), 404
        
    # Testar integração
    sucesso, mensagem = testar_integracao(id)
    
    return jsonify({
        "sucesso": sucesso,
        "mensagem": mensagem
    }), 200 if sucesso else 400

@integracoes_bp.route('/integracoes/webhook', methods=['POST'])
@swag_from({
    "tags": ["Integrações"],
    "summary": "Webhook para receber dados externos",
    "description": "Endpoint para receber dados de sistemas externos como CRM, automação, etc.",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "schema": {
                "type": "object",
                "properties": {
                    "tipo": {"type": "string", "enum": ["crm", "automacao", "analytics"]},
                    "acao": {"type": "string"},
                    "dados": {"type": "object"}
                }
            },
            "required": True
        }
    ],
    "responses": {
        200: {"description": "Dados processados com sucesso"},
        400: {"description": "Dados inválidos"}
    }
})
def webhook():
    try:
        dados = request.get_json()
        
        if not dados or 'tipo' not in dados or 'acao' not in dados:
            return jsonify({"error": "Dados inválidos"}), 400
            
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Buscar integração do tipo correspondente
        cursor.execute("""
            SELECT id FROM integracoes 
            WHERE tipo = %s AND status = 'ativo'
            LIMIT 1
        """, (dados['tipo'],))
        
        integracao = cursor.fetchone()
        if not integracao:
            return jsonify({"error": f"Nenhuma integração ativa encontrada para o tipo {dados['tipo']}"}), 404
            
        integracao_id = integracao[0]
        
        # Registrar webhook
        cursor.execute("""
            INSERT INTO webhook_logs (integracao_id, tipo, acao, endpoint, payload, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            integracao_id,
            dados['tipo'],
            dados['acao'],
            request.path,
            json.dumps(dados.get('dados')),
            'recebido'
        ))
        
        # Processar dados conforme o tipo
        if dados['tipo'] == 'crm':
            processar_dados_crm(dados, cursor)
        elif dados['tipo'] == 'automacao':
            processar_dados_automacao(dados, cursor)
        elif dados['tipo'] == 'analytics':
            processar_dados_analytics(dados, cursor)
            
        connection.commit()
        return jsonify({"message": "Dados processados com sucesso"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@integracoes_bp.route('/integracoes/exportar/<tipo>', methods=['GET'])
@swag_from({
    "tags": ["Integrações"],
    "summary": "Exportar dados para sistemas externos",
    "description": "Endpoint para exportar dados para CRM, sistemas de automação, etc.",
    "parameters": [
        {
            "name": "tipo",
            "in": "path",
            "type": "string",
            "enum": ["crm", "automacao", "analytics"],
            "required": True
        },
        {
            "name": "data_inicio",
            "in": "query",
            "type": "string",
            "format": "date",
            "required": False
        },
        {
            "name": "data_fim",
            "in": "query",
            "type": "string",
            "format": "date",
            "required": False
        }
    ],
    "responses": {
        200: {"description": "Dados exportados com sucesso"}
    }
})
def exportar_dados(tipo):
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        if tipo == 'crm':
            dados = exportar_dados_crm(cursor, data_inicio, data_fim)
        elif tipo == 'automacao':
            dados = exportar_dados_automacao(cursor, data_inicio, data_fim)
        elif tipo == 'analytics':
            dados = exportar_dados_analytics(cursor, data_inicio, data_fim)
        else:
            return jsonify({"error": "Tipo de exportação inválido"}), 400
            
        return jsonify(dados), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def processar_dados_crm(dados, cursor):
    """Processa dados recebidos do CRM"""
    acao = dados['acao']
    if acao == 'atualizar_contato':
        cursor.execute("""
            UPDATE emails 
            SET nome = %s, categoria = %s
            WHERE email = %s
        """, (
            dados['dados']['nome'],
            dados['dados'].get('categoria'),
            dados['dados']['email']
        ))
    elif acao == 'adicionar_contato':
        cursor.execute("""
            INSERT INTO emails (email, nome, categoria)
            VALUES (%s, %s, %s)
        """, (
            dados['dados']['email'],
            dados['dados']['nome'],
            dados['dados'].get('categoria')
        ))

def processar_dados_automacao(dados, cursor):
    """Processa dados recebidos do sistema de automação"""
    acao = dados['acao']
    if acao == 'agendar_campanha':
        cursor.execute("""
            INSERT INTO campanhas (titulo, mensagem, data_envio, status)
            VALUES (%s, %s, %s, 'pendente')
        """, (
            dados['dados']['titulo'],
            dados['dados']['mensagem'],
            dados['dados']['data_envio']
        ))
    elif acao == 'cancelar_campanha':
        cursor.execute("""
            UPDATE campanhas 
            SET status = 'cancelado'
            WHERE id = %s
        """, (dados['dados']['campanha_id'],))

def processar_dados_analytics(dados, cursor):
    """Processa dados recebidos do sistema de analytics"""
    acao = dados['acao']
    if acao == 'registrar_conversao':
        cursor.execute("""
            INSERT INTO interacoes (envio_id, email_id, tipo, detalhes)
            VALUES (%s, %s, 'conversao', %s)
        """, (
            dados['dados']['envio_id'],
            dados['dados']['email_id'],
            json.dumps(dados['dados'].get('detalhes'))
        ))

def exportar_dados_crm(cursor, data_inicio=None, data_fim=None):
    """Exporta dados para CRM"""
    query = """
        SELECT 
            e.id,
            e.email,
            e.nome,
            e.data_cadastro,
            COUNT(DISTINCT c.id) as total_campanhas,
            COUNT(DISTINCT i.id) as total_interacoes
        FROM emails e
        LEFT JOIN envios en ON e.id = en.email_id
        LEFT JOIN campanhas c ON en.campanha_id = c.id
        LEFT JOIN interacoes i ON en.id = i.envio_id
    """
    params = []
    
    if data_inicio:
        query += " WHERE e.data_cadastro >= %s"
        params.append(data_inicio)
        if data_fim:
            query += " AND e.data_cadastro <= %s"
            params.append(data_fim)
    elif data_fim:
        query += " WHERE e.data_cadastro <= %s"
        params.append(data_fim)
        
    query += " GROUP BY e.id, e.email, e.nome, e.data_cadastro"
    
    cursor.execute(query, params)
    return cursor.fetchall()

def exportar_dados_automacao(cursor, data_inicio=None, data_fim=None):
    """Exporta dados para sistema de automação"""
    query = """
        SELECT 
            c.id,
            c.titulo,
            c.data_envio,
            c.status,
            COUNT(DISTINCT e.id) as total_envios,
            COUNT(DISTINCT CASE WHEN i.tipo = 'abertura' THEN i.id END) as total_aberturas,
            COUNT(DISTINCT CASE WHEN i.tipo = 'clique' THEN i.id END) as total_cliques
        FROM campanhas c
        LEFT JOIN envios e ON c.id = e.campanha_id
        LEFT JOIN interacoes i ON e.id = i.envio_id
    """
    params = []
    
    if data_inicio:
        query += " WHERE c.data_envio >= %s"
        params.append(data_inicio)
        if data_fim:
            query += " AND c.data_envio <= %s"
            params.append(data_fim)
    elif data_fim:
        query += " WHERE c.data_envio <= %s"
        params.append(data_fim)
        
    query += " GROUP BY c.id, c.titulo, c.data_envio, c.status"
    
    cursor.execute(query, params)
    return cursor.fetchall()

def exportar_dados_analytics(cursor, data_inicio=None, data_fim=None):
    """Exporta dados para sistema de analytics"""
    query = """
        SELECT 
            DATE(i.data_interacao) as data,
            i.tipo,
            COUNT(*) as total,
            COUNT(DISTINCT i.email_id) as usuarios_unicos
        FROM interacoes i
    """
    params = []
    
    if data_inicio:
        query += " WHERE i.data_interacao >= %s"
        params.append(data_inicio)
        if data_fim:
            query += " AND i.data_interacao <= %s"
            params.append(data_fim)
    elif data_fim:
        query += " WHERE i.data_interacao <= %s"
        params.append(data_fim)
        
    query += " GROUP BY DATE(i.data_interacao), i.tipo"
    
    cursor.execute(query, params)
    return cursor.fetchall() 
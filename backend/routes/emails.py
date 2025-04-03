from flask import Blueprint, request, jsonify
from backend.config import get_db_connection
from flasgger import swag_from
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
import os
from dotenv import load_dotenv
from backend.services.email_service import send_email
import traceback

load_dotenv()

emails_bp = Blueprint('emails', __name__)

def email_valido(email):
    """Valida se o e-mail possui um formato permitido."""
    dominio = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$'
    return re.match(dominio, email) is not None

@emails_bp.route('/', methods=['GET'])
@swag_from({
    "tags": ["Emails"],
    "summary": "Listar contatos",
    "description": "Retorna todos os contatos cadastrados no sistema.",
    "responses": {
        200: {
            "description": "Lista de contatos",
            "schema": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "email": {"type": "string"},
                        "nome": {"type": "string"},
                        "status": {"type": "string"},
                        "created_at": {"type": "string"},
                        "updated_at": {"type": "string"}
                    }
                }
            }
        }
    }
})
def listar_emails():
    """Lista todos os contatos registrados no banco de dados."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM contatos ORDER BY created_at DESC")
    contatos = cursor.fetchall()

    cursor.close()
    connection.close()

    if not contatos:
        return jsonify({"message": "Nenhum contato encontrado."}), 404

    return jsonify(contatos), 200

@emails_bp.route('/', methods=['POST'])
@swag_from({
    "tags": ["Emails"],
    "summary": "Adicionar contato",
    "description": "Adiciona um novo contato ao sistema.",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "example": "contato@exemplo.com"},
                    "nome": {"type": "string", "example": "João Silva"}
                },
                "required": ["email"]
            }
        }
    ],
    "responses": {
        201: {
            "description": "Contato adicionado com sucesso",
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
def adicionar_email():
    """Adiciona um novo contato ao sistema."""
    dados = request.json
    
    # Validar campos obrigatórios
    if not dados or 'email' not in dados:
        return jsonify({
            "error": "O campo 'email' é obrigatório."
        }), 400
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Verificar se o email já existe
        cursor.execute("SELECT id FROM contatos WHERE email = %s", (dados['email'],))
        if cursor.fetchone():
            return jsonify({"error": "Email já cadastrado"}), 400
        
        # Preparar campos
        campos = ['email']
        valores = [dados['email']]
        placeholders = ['%s']
        
        # Adicionar campos opcionais
        if 'nome' in dados and dados['nome'] is not None:
            campos.append('nome')
            valores.append(dados['nome'])
            placeholders.append('%s')
        
        # Construir query
        query = f"""
            INSERT INTO contatos ({', '.join(campos)})
            VALUES ({', '.join(placeholders)})
        """
        
        cursor.execute(query, valores)
        contato_id = cursor.lastrowid
        connection.commit()
        
        return jsonify({
            "id": contato_id,
            "message": "Contato adicionado com sucesso"
        }), 201
        
    except Exception as e:
        return jsonify({"error": f"Erro ao adicionar contato: {str(e)}"}), 500
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@emails_bp.route('/<int:id>', methods=['PUT'])
@swag_from({
    "tags": ["Emails"],
    "summary": "Atualizar contato",
    "description": "Atualiza um contato existente.",
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID do contato"
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "email": {"type": "string"},
                    "nome": {"type": "string"},
                    "status": {"type": "string"}
                }
            }
        }
    ],
    "responses": {
        200: {"description": "Contato atualizado com sucesso"},
        404: {"description": "Contato não encontrado"},
        500: {"description": "Erro interno"}
    }
})
def atualizar_email(id):
    """Atualiza um contato existente."""
    dados = request.json
    
    if not dados:
        return jsonify({"error": "Nenhum dado fornecido para atualização"}), 400
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Verificar se o contato existe
        cursor.execute("SELECT id FROM contatos WHERE id = %s", (id,))
        if not cursor.fetchone():
            return jsonify({"error": "Contato não encontrado"}), 404
        
        # Preparar campos para atualização
        campos = []
        valores = []
        
        if 'email' in dados:
            # Verificar se o novo email já existe
            cursor.execute("SELECT id FROM contatos WHERE email = %s AND id != %s", (dados['email'], id))
            if cursor.fetchone():
                return jsonify({"error": "Email já cadastrado"}), 400
            campos.append("email = %s")
            valores.append(dados['email'])
            
        if 'nome' in dados:
            campos.append("nome = %s")
            valores.append(dados['nome'])
            
        if 'status' in dados:
            campos.append("status = %s")
            valores.append(dados['status'])
        
        if not campos:
            return jsonify({"error": "Nenhum campo para atualizar"}), 400
        
        # Adicionar ID aos valores
        valores.append(id)
        
        # Construir query
        query = f"""
            UPDATE contatos 
            SET {', '.join(campos)}
            WHERE id = %s
        """
        
        cursor.execute(query, valores)
        connection.commit()
        
        return jsonify({"message": "Contato atualizado com sucesso"}), 200
        
    except Exception as e:
        return jsonify({"error": f"Erro ao atualizar contato: {str(e)}"}), 500
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@emails_bp.route('/<int:id>', methods=['DELETE'])
@swag_from({
    "tags": ["Emails"],
    "summary": "Remover contato",
    "description": "Remove um contato do sistema.",
    "parameters": [
        {
            "name": "id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID do contato"
        }
    ],
    "responses": {
        200: {"description": "Contato removido com sucesso"},
        404: {"description": "Contato não encontrado"},
        500: {"description": "Erro interno"}
    }
})
def remover_email(id):
    """Remove um contato do sistema."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Verificar se o contato existe
        cursor.execute("SELECT id FROM contatos WHERE id = %s", (id,))
        if not cursor.fetchone():
            return jsonify({"error": "Contato não encontrado"}), 404
        
        # Remover o contato
        cursor.execute("DELETE FROM contatos WHERE id = %s", (id,))
        connection.commit()
        
        return jsonify({"message": "Contato removido com sucesso"}), 200
        
    except Exception as e:
        return jsonify({"error": f"Erro ao remover contato: {str(e)}"}), 500
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@emails_bp.route('/enviar', methods=['POST'])
@swag_from({
    "tags": ["E-mails"],
    "summary": "Enviar email",
    "description": "Envia um email para um contato ou segmento específico.",
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
                    "assunto": {"type": "string", "example": "Newsletter"},
                    "dados_padrao": {"type": "object"}
                },
                "required": ["template_id", "segmento_id", "assunto"]
            }
        }
    ],
    "responses": {
        200: {"description": "Email enviado com sucesso"},
        400: {"description": "Dados inválidos"},
        404: {"description": "Template ou segmento não encontrado"}
    }
})
def enviar_email():
    dados = request.json

    if not dados or 'template_id' not in dados or 'segmento_id' not in dados or 'assunto' not in dados:
        return jsonify({"error": "Template ID, segmento ID e assunto são obrigatórios"}), 400
            
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Buscar template
        cursor.execute("SELECT * FROM templates WHERE id = %s", (dados['template_id'],))
        template = cursor.fetchone()
        if not template:
            return jsonify({"error": "Template não encontrado"}), 404
            
        # Buscar contatos do segmento
        cursor.execute("""
            SELECT c.* FROM contatos c
            JOIN contatos_segmentos cs ON c.id = cs.contato_id
            WHERE cs.segmento_id = %s AND c.status = 'ativo'
        """, (dados['segmento_id'],))
        contatos = cursor.fetchall()
        
        if not contatos:
            return jsonify({"error": "Nenhum contato ativo encontrado no segmento"}), 404
            
        # Criar registro de envio
        cursor.execute("""
            INSERT INTO envios (template_id, segmento_id, status)
            VALUES (%s, %s, 'em_progresso')
        """, (dados['template_id'], dados['segmento_id']))
        envio_id = cursor.lastrowid
        connection.commit()
        
        # Preparar conteúdo do email
        conteudo = template['html_content']
        if dados.get('dados_padrao'):
            for chave, valor in dados['dados_padrao'].items():
                conteudo = conteudo.replace(f"{{{chave}}}", str(valor))
                
        # Enviar para cada contato
        contatos_enviados = []
        for contato in contatos:
            # Personalizar conteúdo
            conteudo_personalizado = conteudo
            conteudo_personalizado = conteudo_personalizado.replace("{nome}", contato['nome'])
            if contato.get('cargo'):
                conteudo_personalizado = conteudo_personalizado.replace("{cargo}", contato['cargo'])
            if contato.get('empresa'):
                conteudo_personalizado = conteudo_personalizado.replace("{empresa}", contato['empresa'])
                
            # Enviar email
            sucesso = send_email(
                to_email=contato['email'],
                subject=dados['assunto'],
                html_content=conteudo_personalizado,
                envio_id=envio_id,
                contato_id=contato['id']
            )
            
            if sucesso:
                contatos_enviados.append({
                    'nome': contato['nome'],
                    'email': contato['email']
                })
                
        # Atualizar status do envio
        status = 'concluido' if len(contatos_enviados) > 0 else 'erro'
        cursor.execute("""
            UPDATE envios SET status = %s WHERE id = %s
        """, (status, envio_id))
        connection.commit()
        
        return jsonify({
            "message": f"Emails enviados com sucesso para {len(contatos_enviados)} contatos",
            "contatos": contatos_enviados
        }), 200
        
    except Exception as e:
        print(f"Erro ao enviar email: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Erro ao enviar email: {str(e)}"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
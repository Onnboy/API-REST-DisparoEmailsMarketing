from flask import Blueprint, request, jsonify, send_file, Response, redirect
from backend.config import get_db_connection
from flasgger import swag_from
import json
from datetime import datetime
import base64
import hashlib
import hmac
import os
from backend.tasks import registrar_evento_tracking_sync

tracking_bp = Blueprint('tracking', __name__)

def verificar_envio_existe(envio_id):
    """Verifica se um envio existe no banco de dados"""
    try:
        print(f"Verificando envio com ID: {envio_id}")
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "SELECT id FROM envios WHERE id = %s"
        print(f"Executando query: {query} com parâmetro: {envio_id}")
        cursor.execute(query, (envio_id,))
        resultado = cursor.fetchone()
        print(f"Resultado da consulta: {resultado}")
        cursor.close()
        connection.close()
        return resultado is not None
    except Exception as e:
        print(f"Erro ao verificar envio: {str(e)}")
        return False

def gerar_token_tracking(envio_id, email_id, tipo):
    """Gera um token seguro para tracking"""
    chave = os.environ.get('SECRET_KEY', 'chave-secreta-padrao')
    dados = f"{envio_id}:{email_id}:{tipo}:{datetime.now().strftime('%Y%m%d')}"
    assinatura = hmac.new(chave.encode(), dados.encode(), hashlib.sha256).hexdigest()
    token = base64.urlsafe_b64encode(f"{dados}:{assinatura}".encode()).decode()
    return token

def validar_token_tracking(token):
    """Valida e extrai informações do token de tracking"""
    try:
        chave = os.environ.get('SECRET_KEY', 'chave-secreta-padrao')
        dados_token = base64.urlsafe_b64decode(token.encode()).decode()
        dados, assinatura = dados_token.rsplit(':', 1)
        
        # Verificar assinatura
        assinatura_esperada = hmac.new(chave.encode(), dados.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(assinatura, assinatura_esperada):
            return None
            
        envio_id, email_id, tipo, data = dados.split(':')
        return {
            'envio_id': int(envio_id),
            'email_id': int(email_id),
            'tipo': tipo,
            'data': data
        }
    except Exception:
        return None

@tracking_bp.route('/pixel/<int:envio_id>')
@swag_from({
    "tags": ["Tracking"],
    "summary": "Registra abertura de email usando envio_id",
    "description": "Endpoint para pixel de rastreamento que registra quando um email é aberto",
    "parameters": [
        {
            "name": "envio_id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID do envio"
        }
    ],
    "responses": {
        200: {"description": "Pixel de tracking"},
        404: {"description": "Envio não encontrado"}
    }
})
def pixel_tracking(envio_id):
    try:
        print(f"Recebida requisição para tracking de pixel com envio_id: {envio_id}")
        # Verificar se o envio existe
        if not verificar_envio_existe(envio_id):
            print("Envio não encontrado")
            return Response(status=404)
            
        print("Envio encontrado, registrando evento de tracking")
        # Registrar evento de tracking
        success = registrar_evento_tracking_sync(
            envio_id=envio_id,
            tipo_evento='abertura',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        if not success:
            print("Erro ao registrar evento de tracking")
            return Response(status=500)
        
        print("Evento registrado com sucesso, retornando pixel")
        # Retornar pixel transparente 1x1
        pixel_gif = b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        return Response(pixel_gif, mimetype='image/gif')
        
    except Exception as e:
        print(f"Erro no tracking de pixel: {str(e)}")
        return Response(status=500)

@tracking_bp.route('/click/<int:envio_id>/<path:url>')
@swag_from({
    "tags": ["Tracking"],
    "summary": "Registra clique em link usando envio_id",
    "description": "Endpoint para rastrear cliques em links do email",
    "parameters": [
        {
            "name": "envio_id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID do envio"
        },
        {
            "name": "url",
            "in": "path",
            "type": "string",
            "required": True,
            "description": "URL original do link"
        }
    ],
    "responses": {
        302: {"description": "Redirecionamento para URL original"},
        404: {"description": "Envio não encontrado"}
    }
})
def click_tracking(envio_id, url):
    try:
        # Verificar se o envio existe
        if not verificar_envio_existe(envio_id):
            return Response(status=404)
            
        # Registrar evento de tracking
        success = registrar_evento_tracking_sync(
            envio_id=envio_id,
            tipo_evento='clique',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            url=url
        )
        
        if not success:
            return Response(status=500)
        
        # Redirecionar para URL original
        return redirect(url)
        
    except Exception as e:
        print(f"Erro no tracking de clique: {str(e)}")
        return Response(status=500)

@tracking_bp.route('/resposta/<token>', methods=['POST'])
@swag_from({
    "tags": ["Tracking"],
    "summary": "Registra resposta ao email",
    "description": "Endpoint para registrar respostas aos emails enviados",
    "parameters": [
        {
            "name": "token",
            "in": "path",
            "type": "string",
            "required": True,
            "description": "Token de tracking"
        }
    ],
    "responses": {
        200: {"description": "Resposta registrada"}
    }
})
def tracking_resposta(token):
    try:
        dados = validar_token_tracking(token)
        if not dados or dados['tipo'] != 'resposta':
            return jsonify({"error": "Token inválido"}), 404
            
        # Registrar evento de tracking
        success = registrar_evento_tracking_sync(
            envio_id=dados['envio_id'],
            tipo_evento='resposta',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        
        if not success:
            return jsonify({"error": "Erro ao registrar resposta"}), 500
        
        return jsonify({"message": "Resposta registrada com sucesso"}), 200
        
    except Exception as e:
        print(f"Erro no tracking de resposta: {str(e)}")
        return jsonify({"error": "Erro interno"}), 500 
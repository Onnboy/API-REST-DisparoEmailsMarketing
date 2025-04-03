import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import json
import traceback
from backend.services.integracoes_service import listar_integracoes
from backend.config import get_db_connection
import os
from dotenv import load_dotenv
from urllib.parse import urlencode, quote_plus
from backend.utils import gerar_token_tracking
from backend.database import get_db_connection
import re

load_dotenv()

def registrar_metrica(envio_id, contato_id, status, detalhes=None):
    """
    Registra uma métrica de envio no banco de dados.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = """
            INSERT INTO metricas_envio (envio_id, contato_id, status, detalhes)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (envio_id, contato_id, status, json.dumps(detalhes) if detalhes else None))
        connection.commit()
        
        return True
    except Exception as e:
        print(f"Erro ao registrar métrica: {str(e)}")
        traceback.print_exc()
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def adicionar_tracking(html_content, envio_id, email_id, base_url):
    """
    Adiciona elementos de tracking no conteúdo HTML do email usando regex.
    """
    try:
        # Adicionar pixel de tracking antes do </body>
        token_abertura = gerar_token_tracking(envio_id, email_id, 'abertura')
        pixel = f'<img src="{base_url}/tracking/pixel/{token_abertura}" width="1" height="1" style="display:none;">'
        html_content = re.sub(r'</body>', f'{pixel}</body>', html_content, flags=re.IGNORECASE)
        
        # Adicionar tracking em todos os links
        def replace_link(match):
            url_original = match.group(1)
            token_clique = gerar_token_tracking(envio_id, email_id, 'clique')
            params = urlencode({'url': url_original}, quote_via=quote_plus)
            return f'href="{base_url}/tracking/click/{token_clique}?{params}"'
            
        html_content = re.sub(r'href="([^"]+)"', replace_link, html_content)
            
        return html_content
    except Exception as e:
        print(f"Erro ao adicionar tracking: {str(e)}")
        traceback.print_exc()
        return html_content

def send_email(to_email, subject, html_content, envio_id=None, contato_id=None):
    """
    Envia um email usando a primeira integração ativa disponível.
    """
    try:
        # Buscar integrações ativas
        integracoes = listar_integracoes(status='ativo')
        if not integracoes:
            print("Nenhuma integração ativa encontrada")
            if envio_id and contato_id:
                registrar_metrica(envio_id, contato_id, 'erro', {'erro': 'Nenhuma integração ativa'})
            return False
            
        # Adicionar tracking se tiver envio_id e contato_id
        if envio_id and contato_id:
            base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
            html_content = adicionar_tracking(html_content, envio_id, contato_id, base_url)
            
        # Tentar cada integração até conseguir enviar
        for integracao in integracoes:
            tipo = integracao['tipo']
            config = integracao['configuracoes']
            
            try:
                if tipo == 'smtp':
                    sucesso = send_via_smtp(to_email, subject, html_content, config)
                elif tipo == 'api':
                    sucesso = send_via_api(to_email, subject, html_content, config)
                else:
                    print(f"Tipo de integração não suportado para envio: {tipo}")
                    continue
                    
                if sucesso and envio_id and contato_id:
                    registrar_metrica(envio_id, contato_id, 'enviado')
                return sucesso
                
            except Exception as e:
                print(f"Erro ao enviar email usando integração {integracao['nome']}: {str(e)}")
                traceback.print_exc()
                if envio_id and contato_id:
                    registrar_metrica(envio_id, contato_id, 'erro', {'erro': str(e)})
                continue
                
        print("Nenhuma integração disponível conseguiu enviar o email")
        if envio_id and contato_id:
            registrar_metrica(envio_id, contato_id, 'erro', {'erro': 'Nenhuma integração disponível'})
        return False
        
    except Exception as e:
        print(f"Erro ao enviar email: {str(e)}")
        traceback.print_exc()
        if envio_id and contato_id:
            registrar_metrica(envio_id, contato_id, 'erro', {'erro': str(e)})
        return False

def send_via_smtp(to_email, subject, html_content, config):
    """
    Envia email usando SMTP.
    """
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = config['username']
        msg['To'] = to_email
        
        # Adicionar conteúdo HTML
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Conectar ao servidor SMTP
        server = smtplib.SMTP(config['host'], config['port'])
        server.starttls()
        server.login(config['username'], config['password'])
        
        # Enviar email
        server.send_message(msg)
        server.quit()
        
        print(f"Email enviado com sucesso via SMTP para {to_email}")
        return True
        
    except Exception as e:
        print(f"Erro ao enviar email via SMTP: {str(e)}")
        traceback.print_exc()
        return False

def send_via_api(to_email, subject, html_content, config):
    """
    Envia email usando API (ex: SendGrid, Mailgun, etc).
    """
    try:
        headers = config.get('headers', {}).copy()
        if config.get('api_key'):
            # Ajustar formato do header de autorização
            if 'brevo.com' in config.get('url', ''):
                headers['api-key'] = config['api_key']
            else:
                headers['Authorization'] = f"Bearer {config['api_key']}"
            
        # Preparar payload conforme especificação da API
        if 'payload_template' in config:
            # Usar template específico da API
            template = config['payload_template']
            # Escapar caracteres especiais no conteúdo HTML
            html_content = html_content.replace('"', '\\"').replace('\n', '\\n')
            # Substituir variáveis no template
            payload_str = template % (
                to_email,
                to_email.split('@')[0].title(),  # Nome do destinatário
                subject,
                html_content
            )
            # Converter string para JSON
            payload = json.loads(payload_str)
        else:
            # Usar formato padrão
            payload = {
                'to': to_email,
                'subject': subject,
                'html': html_content
            }
            
        # Enviar requisição
        response = requests.post(
            config['url'],
            json=payload,
            headers=headers,
            timeout=10
        )
        
        # Verificar resposta
        response.raise_for_status()
        
        print(f"Email enviado com sucesso via API para {to_email}")
        return True
        
    except Exception as e:
        print(f"Erro ao enviar email via API: {str(e)}")
        traceback.print_exc()
        return False

def get_smtp_config():
    """Obtém a configuração SMTP do banco de dados."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM integracoes WHERE tipo = 'smtp' LIMIT 1")
        integracao = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not integracao:
            return None
            
        config = json.loads(integracao['configuracao'])
        config['id'] = integracao['id']
        return config
    except Exception as e:
        print(f"Erro ao obter configuração SMTP: {str(e)}")
        return None

def update_smtp_config(config_data):
    """Atualiza a configuração SMTP no banco de dados."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verifica se já existe uma configuração
        cursor.execute("SELECT id FROM integracoes WHERE tipo = 'smtp' LIMIT 1")
        existing = cursor.fetchone()
        
        if existing:
            # Atualiza a configuração existente
            cursor.execute("""
                UPDATE integracoes 
                SET configuracao = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (
                json.dumps(config_data),
                existing[0]
            ))
        else:
            # Cria nova configuração
            cursor.execute("""
                INSERT INTO integracoes (tipo, configuracao)
                VALUES ('smtp', %s)
            """, (json.dumps(config_data),))
        
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Erro ao atualizar configuração SMTP: {str(e)}")
        return False
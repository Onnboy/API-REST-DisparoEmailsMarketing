from backend.celery_app import celery_app
from backend.services.email_service import send_email
from backend.services.agendamento_service import processar_agendamentos
from backend.config import get_db_connection
import json
from datetime import datetime
import traceback

def registrar_evento_tracking_sync(envio_id, tipo_evento, ip_address=None, user_agent=None, url=None):
    """Versão síncrona da função para registrar eventos de tracking"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        dados_adicionais = {
            'ip_address': ip_address,
            'user_agent': user_agent
        }
        if url:
            dados_adicionais['url'] = url
        
        cursor.execute(
            """
            INSERT INTO eventos_tracking 
            (envio_id, tipo_evento, dados_adicionais, data_evento) 
            VALUES (%s, %s, %s, NOW())
            """,
            (envio_id, tipo_evento, json.dumps(dados_adicionais))
        )
        
        connection.commit()
        return True
    except Exception as e:
        print(f"Erro ao registrar evento de tracking: {str(e)}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@celery_app.task(bind=True, max_retries=3)
def enviar_email_task(self, destinatario, assunto, mensagem, template_id, segmento_id, contato_id):
    """Tarefa para enviar um email individual"""
    try:
        success = send_email(destinatario, assunto, mensagem)
        
        # Registrar envio no banco
        connection = get_db_connection()
        cursor = connection.cursor()
        
        if success:
            cursor.execute(
                "INSERT INTO envios (contato_id, template_id, segmento_id, status, data_envio) VALUES (%s, %s, %s, 'enviado', NOW())",
                (contato_id, template_id, segmento_id)
            )
        else:
            cursor.execute(
                "INSERT INTO envios (contato_id, template_id, segmento_id, status, erro, data_envio) VALUES (%s, %s, %s, 'erro', 'Falha no envio', NOW())",
                (contato_id, template_id, segmento_id)
            )
        
        connection.commit()
        return success
    except Exception as e:
        # Em caso de erro, tenta novamente
        self.retry(exc=e, countdown=300)  # 5 minutos
        raise

@celery_app.task
def processar_agendamentos_task():
    """Tarefa para processar agendamentos pendentes"""
    try:
        processar_agendamentos()
    except Exception as e:
        print(f"Erro ao processar agendamentos: {str(e)}")
        print(traceback.format_exc())
        raise

@celery_app.task
def registrar_evento_tracking(envio_id, tipo_evento, dados_adicionais=None):
    """Tarefa para registrar eventos de tracking (abertura, clique)"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute(
            """
            INSERT INTO eventos_tracking 
            (envio_id, tipo_evento, dados_adicionais, data_evento) 
            VALUES (%s, %s, %s, NOW())
            """,
            (envio_id, tipo_evento, json.dumps(dados_adicionais) if dados_adicionais else None)
        )
        
        connection.commit()
    except Exception as e:
        print(f"Erro ao registrar evento de tracking: {str(e)}")
        raise
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close() 
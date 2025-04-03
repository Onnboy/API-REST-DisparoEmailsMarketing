from backend.config import get_db_connection
from backend.services.email_service import send_email
import json
from datetime import datetime
import time
import traceback

def processar_agendamentos():
    """
    Processa os agendamentos pendentes, enviando os emails agendados
    quando chegar o momento do envio.
    """
    print("\n=== INICIANDO PROCESSAMENTO DE AGENDAMENTOS ===")
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Buscar agendamentos pendentes
        query = """
            SELECT 
                a.*,
                t.html_content as template_html,
                s.criterios as segmento_criterios
            FROM agendamentos a
            JOIN templates t ON a.template_id = t.id
            JOIN segmentos s ON a.segmento_id = s.id
            WHERE a.status = 'agendado'
            AND a.data_envio <= NOW()
        """
        
        cursor.execute(query)
        agendamentos = cursor.fetchall()
        
        print(f"Encontrados {len(agendamentos)} agendamentos para processar")
        
        for agendamento in agendamentos:
            print(f"\nProcessando agendamento {agendamento['id']}")
            
            try:
                # Buscar contatos do segmento
                criterios = json.loads(agendamento['segmento_criterios'])
                query = 'SELECT * FROM contatos WHERE 1=1'
                params = []
                
                for campo, valor in criterios.items():
                    if campo in ['id', 'status']:
                        query += f' AND {campo} = %s'
                        params.append(valor)
                    elif campo in ['email', 'nome', 'cargo', 'empresa', 'telefone', 'grupo']:
                        query += f' AND LOWER({campo}) LIKE LOWER(%s)'
                        params.append(f'%{valor}%')
                    elif campo == 'tags':
                        if isinstance(valor, list):
                            for tag in valor:
                                query += ' AND tags LIKE %s'
                                params.append(f'%{tag}%')
                        else:
                            query += ' AND tags LIKE %s'
                            params.append(f'%{valor}%')
                
                cursor.execute(query, params)
                contatos = cursor.fetchall()
                
                print(f"Encontrados {len(contatos)} contatos para envio")
                
                # Enviar emails
                dados_padrao = json.loads(agendamento['dados_padrao']) if agendamento['dados_padrao'] else {}
                emails_enviados = []
                
                for contato in contatos:
                    # Combinar dados padrão com dados do contato
                    dados_template = dados_padrao.copy()
                    dados_template.update({
                        'nome': contato['nome'],
                        'email': contato['email'],
                        'cargo': contato['cargo'],
                        'empresa': contato['empresa']
                    })
                    
                    # Substituir campos dinâmicos
                    mensagem = agendamento['template_html']
                    for campo, valor in dados_template.items():
                        if valor is not None:
                            mensagem = mensagem.replace(f"{{{{ {campo} }}}}", str(valor))
                    
                    # Enviar email
                    if send_email(contato['email'], agendamento['assunto'], mensagem):
                        emails_enviados.append(contato)
                        # Registrar envio
                        cursor.execute(
                            "INSERT INTO envios (contato_id, template_id, segmento_id, status) VALUES (%s, %s, %s, 'enviado')",
                            (contato['id'], agendamento['template_id'], agendamento['segmento_id'])
                        )
                    else:
                        # Registrar falha
                        cursor.execute(
                            "INSERT INTO envios (contato_id, template_id, segmento_id, status) VALUES (%s, %s, %s, 'erro')",
                            (contato['id'], agendamento['template_id'], agendamento['segmento_id'])
                        )
                
                # Atualizar status do agendamento
                cursor.execute(
                    "UPDATE agendamentos SET status = 'enviado' WHERE id = %s",
                    (agendamento['id'],)
                )
                connection.commit()
                
                print(f"Agendamento {agendamento['id']} processado com sucesso")
                print(f"Emails enviados: {len(emails_enviados)} de {len(contatos)}")
                
            except Exception as e:
                print(f"Erro ao processar agendamento {agendamento['id']}: {str(e)}")
                traceback.print_exc()
                
                # Marcar agendamento como erro
                cursor.execute(
                    "UPDATE agendamentos SET status = 'erro' WHERE id = %s",
                    (agendamento['id'],)
                )
                connection.commit()
                
        print("\n=== PROCESSAMENTO DE AGENDAMENTOS CONCLUÍDO ===")
        
    except Exception as e:
        print(f"\nErro no processamento de agendamentos: {str(e)}")
        traceback.print_exc()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def iniciar_processamento_agendamentos(intervalo=60):
    """
    Inicia o processamento de agendamentos em um loop infinito.
    :param intervalo: Intervalo em segundos entre cada verificação
    """
    while True:
        processar_agendamentos()
        time.sleep(intervalo) 
from backend.config import get_db_connection
import json

def criar_integracao(nome, tipo, configuracoes):
    """
    Cria uma nova integração.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = """
            INSERT INTO integracoes (nome, tipo, configuracoes)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (nome, tipo, json.dumps(configuracoes)))
        connection.commit()
        
        return cursor.lastrowid
    except Exception as e:
        print(f"Erro ao criar integração: {str(e)}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def atualizar_integracao(id, nome=None, tipo=None, configuracoes=None, status=None):
    """
    Atualiza uma integração existente.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        updates = []
        params = []
        
        if nome is not None:
            updates.append("nome = %s")
            params.append(nome)
        if tipo is not None:
            updates.append("tipo = %s")
            params.append(tipo)
        if configuracoes is not None:
            updates.append("configuracoes = %s")
            params.append(json.dumps(configuracoes))
        if status is not None:
            updates.append("status = %s")
            params.append(status)
            
        if not updates:
            return False
            
        query = f"UPDATE integracoes SET {', '.join(updates)} WHERE id = %s"
        params.append(id)
        
        cursor.execute(query, params)
        connection.commit()
        
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao atualizar integração: {str(e)}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def buscar_integracao(id):
    """
    Busca uma integração pelo ID.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM integracoes WHERE id = %s", (id,))
        integracao = cursor.fetchone()
        
        if integracao and isinstance(integracao['configuracoes'], str):
            integracao['configuracoes'] = json.loads(integracao['configuracoes'])
            
        return integracao
    except Exception as e:
        print(f"Erro ao buscar integração: {str(e)}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def listar_integracoes(tipo=None, status=None):
    """
    Lista todas as integrações, com opção de filtrar por tipo e status.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        query = "SELECT * FROM integracoes WHERE 1=1"
        params = []
        
        if tipo:
            query += " AND tipo = %s"
            params.append(tipo)
        if status:
            query += " AND status = %s"
            params.append(status)
            
        cursor.execute(query, params)
        integracoes = cursor.fetchall()
        
        # Converter configurações de JSON para dict
        for integracao in integracoes:
            if isinstance(integracao['configuracoes'], str):
                integracao['configuracoes'] = json.loads(integracao['configuracoes'])
                
        return integracoes
    except Exception as e:
        print(f"Erro ao listar integrações: {str(e)}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def deletar_integracao(id):
    """
    Deleta uma integração.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("DELETE FROM integracoes WHERE id = %s", (id,))
        connection.commit()
        
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Erro ao deletar integração: {str(e)}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def testar_integracao(id):
    """
    Testa a conexão de uma integração.
    """
    try:
        integracao = buscar_integracao(id)
        if not integracao:
            return False, "Integração não encontrada"
            
        tipo = integracao['tipo']
        config = integracao['configuracoes']
        
        if tipo == 'smtp':
            # Testar conexão SMTP
            import smtplib
            try:
                server = smtplib.SMTP(config['host'], config['port'])
                server.starttls()
                server.login(config['username'], config['password'])
                server.quit()
                return True, "Conexão SMTP estabelecida com sucesso"
            except Exception as e:
                return False, f"Erro na conexão SMTP: {str(e)}"
                
        elif tipo == 'api':
            # Testar conexão API
            import requests
            try:
                headers = config.get('headers', {}).copy()
                if config.get('api_key'):
                    # Ajustar formato do header de autorização
                    if 'brevo.com' in config.get('url', ''):
                        headers['api-key'] = config['api_key']
                    else:
                        headers['Authorization'] = f"Bearer {config['api_key']}"
                    
                response = requests.get(
                    config['test_url'],
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
                return True, "Conexão API estabelecida com sucesso"
            except Exception as e:
                return False, f"Erro na conexão API: {str(e)}"
                
        elif tipo == 'webhook':
            # Testar webhook
            import requests
            try:
                response = requests.post(
                    config['url'],
                    json={"test": True},
                    headers=config.get('headers', {}),
                    timeout=10
                )
                response.raise_for_status()
                return True, "Webhook testado com sucesso"
            except Exception as e:
                return False, f"Erro no teste do webhook: {str(e)}"
                
        return False, "Tipo de integração não suportado"
    except Exception as e:
        return False, f"Erro ao testar integração: {str(e)}" 
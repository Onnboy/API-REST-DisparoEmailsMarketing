from backend.config import get_db_connection
import json
from datetime import datetime, timedelta

def registrar_metrica(envio_id, contato_id, status, detalhes=None):
    """
    Registra uma nova métrica de envio.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute(
            "INSERT INTO metricas_envio (envio_id, contato_id, status, detalhes) VALUES (%s, %s, %s, %s)",
            (envio_id, contato_id, status, json.dumps(detalhes) if detalhes else None)
        )
        connection.commit()
        
        return True
    except Exception as e:
        print(f"Erro ao registrar métrica: {str(e)}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def obter_metricas_periodo(data_inicio=None, data_fim=None):
    """
    Obtém métricas de envio para um período específico.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Se não especificado, usa últimos 30 dias
        if not data_inicio:
            data_inicio = datetime.now() - timedelta(days=30)
        if not data_fim:
            data_fim = datetime.now()
            
        query = """
            SELECT 
                COUNT(DISTINCT e.id) as total_envios,
                COUNT(DISTINCT CASE WHEN e.status = 'enviado' THEN e.id END) as envios_sucesso,
                COUNT(DISTINCT CASE WHEN e.status = 'erro' THEN e.id END) as envios_erro,
                COUNT(DISTINCT CASE WHEN m.status = 'entregue' THEN m.envio_id END) as total_entregues,
                COUNT(DISTINCT CASE WHEN m.status = 'aberto' THEN m.envio_id END) as total_abertos,
                COUNT(DISTINCT CASE WHEN m.status = 'clicado' THEN m.envio_id END) as total_clicados,
                COUNT(DISTINCT CASE WHEN m.status = 'respondido' THEN m.envio_id END) as total_respondidos
            FROM envios e
            LEFT JOIN metricas_envio m ON e.id = m.envio_id
            WHERE e.created_at BETWEEN %s AND %s
        """
        
        cursor.execute(query, (data_inicio, data_fim))
        metricas = cursor.fetchone()
        
        # Calcular taxas
        total_envios = metricas['total_envios'] or 1  # Evitar divisão por zero
        metricas.update({
            'taxa_entrega': round((metricas['total_entregues'] / total_envios) * 100, 2),
            'taxa_abertura': round((metricas['total_abertos'] / total_envios) * 100, 2),
            'taxa_cliques': round((metricas['total_clicados'] / total_envios) * 100, 2),
            'taxa_respostas': round((metricas['total_respondidos'] / total_envios) * 100, 2),
            'taxa_erro': round((metricas['envios_erro'] / total_envios) * 100, 2)
        })
        
        return metricas
    except Exception as e:
        print(f"Erro ao obter métricas: {str(e)}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def obter_metricas_segmento(segmento_id, periodo=30):
    """
    Obtém métricas de envio para um segmento específico.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        data_inicio = datetime.now() - timedelta(days=periodo)
        
        query = """
            SELECT 
                s.nome as segmento,
                COUNT(DISTINCT e.id) as total_envios,
                COUNT(DISTINCT CASE WHEN e.status = 'enviado' THEN e.id END) as envios_sucesso,
                COUNT(DISTINCT CASE WHEN m.status = 'entregue' THEN m.envio_id END) as total_entregues,
                COUNT(DISTINCT CASE WHEN m.status = 'aberto' THEN m.envio_id END) as total_abertos,
                COUNT(DISTINCT CASE WHEN m.status = 'clicado' THEN m.envio_id END) as total_clicados
            FROM segmentos s
            LEFT JOIN envios e ON s.id = e.segmento_id
            LEFT JOIN metricas_envio m ON e.id = m.envio_id
            WHERE s.id = %s
            AND e.created_at >= %s
            GROUP BY s.id, s.nome
        """
        
        cursor.execute(query, (segmento_id, data_inicio))
        metricas = cursor.fetchone()
        
        if metricas:
            total_envios = metricas['total_envios'] or 1
            metricas.update({
                'taxa_entrega': round((metricas['total_entregues'] / total_envios) * 100, 2),
                'taxa_abertura': round((metricas['total_abertos'] / total_envios) * 100, 2),
                'taxa_cliques': round((metricas['total_clicados'] / total_envios) * 100, 2)
            })
        
        return metricas
    except Exception as e:
        print(f"Erro ao obter métricas do segmento: {str(e)}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def obter_metricas_contato(contato_id):
    """
    Obtém métricas de envio para um contato específico.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Métricas gerais
        query = """
            SELECT 
                c.nome, c.email,
                COUNT(DISTINCT e.id) as total_recebidos,
                COUNT(DISTINCT CASE WHEN m.status = 'aberto' THEN m.envio_id END) as total_abertos,
                COUNT(DISTINCT CASE WHEN m.status = 'clicado' THEN m.envio_id END) as total_clicados,
                COUNT(DISTINCT CASE WHEN m.status = 'respondido' THEN m.envio_id END) as total_respondidos
            FROM contatos c
            LEFT JOIN envios e ON c.id = e.contato_id
            LEFT JOIN metricas_envio m ON e.id = m.envio_id
            WHERE c.id = %s
            GROUP BY c.id, c.nome, c.email
        """
        
        cursor.execute(query, (contato_id,))
        metricas = cursor.fetchone()
        
        if metricas:
            total_recebidos = metricas['total_recebidos'] or 1
            metricas.update({
                'taxa_abertura': round((metricas['total_abertos'] / total_recebidos) * 100, 2),
                'taxa_cliques': round((metricas['total_clicados'] / total_recebidos) * 100, 2),
                'taxa_respostas': round((metricas['total_respondidos'] / total_recebidos) * 100, 2)
            })
            
            # Histórico de interações
            query = """
                SELECT 
                    e.created_at as data_envio,
                    t.nome as template,
                    s.nome as segmento,
                    m.status,
                    m.data_evento,
                    m.detalhes
                FROM envios e
                JOIN templates t ON e.template_id = t.id
                JOIN segmentos s ON e.segmento_id = s.id
                LEFT JOIN metricas_envio m ON e.id = m.envio_id
                WHERE e.contato_id = %s
                ORDER BY e.created_at DESC, m.data_evento DESC
            """
            
            cursor.execute(query, (contato_id,))
            metricas['historico'] = cursor.fetchall()
        
        return metricas
    except Exception as e:
        print(f"Erro ao obter métricas do contato: {str(e)}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

def gerar_relatorio_csv(data_inicio=None, data_fim=None):
    """
    Gera um relatório CSV com métricas detalhadas de envio.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        if not data_inicio:
            data_inicio = datetime.now() - timedelta(days=30)
        if not data_fim:
            data_fim = datetime.now()
            
        query = """
            SELECT 
                e.created_at as data_envio,
                c.nome as contato,
                c.email,
                t.nome as template,
                s.nome as segmento,
                e.status as status_envio,
                GROUP_CONCAT(
                    CONCAT(m.status, ':', DATE_FORMAT(m.data_evento, '%Y-%m-%d %H:%i:%s'))
                    ORDER BY m.data_evento
                    SEPARATOR '|'
                ) as eventos
            FROM envios e
            JOIN contatos c ON e.contato_id = c.id
            JOIN templates t ON e.template_id = t.id
            JOIN segmentos s ON e.segmento_id = s.id
            LEFT JOIN metricas_envio m ON e.id = m.envio_id
            WHERE e.created_at BETWEEN %s AND %s
            GROUP BY e.id, e.created_at, c.nome, c.email, t.nome, s.nome, e.status
            ORDER BY e.created_at DESC
        """
        
        cursor.execute(query, (data_inicio, data_fim))
        resultados = cursor.fetchall()
        
        # Preparar dados CSV
        linhas = []
        cabecalho = ['Data Envio', 'Contato', 'Email', 'Template', 'Segmento', 
                     'Status Envio', 'Entregue', 'Aberto', 'Clicado', 'Respondido']
        
        for r in resultados:
            eventos = dict(e.split(':') for e in r['eventos'].split('|')) if r['eventos'] else {}
            linha = [
                r['data_envio'].strftime('%Y-%m-%d %H:%M:%S'),
                r['contato'],
                r['email'],
                r['template'],
                r['segmento'],
                r['status_envio'],
                eventos.get('entregue', ''),
                eventos.get('aberto', ''),
                eventos.get('clicado', ''),
                eventos.get('respondido', '')
            ]
            linhas.append(linha)
            
        return cabecalho, linhas
    except Exception as e:
        print(f"Erro ao gerar relatório CSV: {str(e)}")
        return None, None
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close() 
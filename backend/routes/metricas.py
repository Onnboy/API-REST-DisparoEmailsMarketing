from flask import Blueprint, request, jsonify, send_file
from backend.config import get_db_connection
from flasgger import swag_from
import json
import csv
import io
from datetime import datetime, timedelta

metricas_bp = Blueprint('metricas', __name__)

@metricas_bp.route('/envios/', methods=['GET'])
@swag_from({
    "tags": ["Métricas"],
    "summary": "Métricas de envios",
    "description": "Retorna métricas detalhadas dos envios de email.",
    "parameters": [
        {
            "name": "data_inicio",
            "in": "query",
            "type": "string",
            "format": "date",
            "required": False,
            "description": "Data inicial para filtrar (YYYY-MM-DD)"
        },
        {
            "name": "data_fim",
            "in": "query",
            "type": "string",
            "format": "date",
            "required": False,
            "description": "Data final para filtrar (YYYY-MM-DD)"
        },
        {
            "name": "formato",
            "in": "query",
            "type": "string",
            "enum": ["json", "csv"],
            "required": False,
            "description": "Formato do relatório (padrão: json)"
        }
    ],
    "responses": {
        200: {"description": "Métricas de envio"},
        400: {"description": "Parâmetros inválidos"}
    }
})
def metricas_envios():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Obter parâmetros da query
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        formato = request.args.get('formato', 'json')
        
        # Construir query base
        query = """
            SELECT 
                COUNT(*) as total_envios,
                SUM(CASE WHEN status = 'enviado' THEN 1 ELSE 0 END) as envios_sucesso,
                SUM(CASE WHEN status = 'erro' THEN 1 ELSE 0 END) as envios_erro,
                AVG(CASE WHEN status = 'enviado' THEN TIMESTAMPDIFF(SECOND, created_at, updated_at) ELSE NULL END) as tempo_medio_envio
            FROM agendamentos
            WHERE 1=1
        """
        params = []
        
        if data_inicio:
            query += " AND created_at >= %s"
            params.append(data_inicio)
        
        if data_fim:
            query += " AND created_at <= %s"
            params.append(data_fim)
        
        cursor.execute(query, params)
        metricas = cursor.fetchone()
        
        # Formatar resultados
        resultado = {
            "total_envios": metricas['total_envios'] or 0,
            "envios_sucesso": metricas['envios_sucesso'] or 0,
            "envios_erro": metricas['envios_erro'] or 0,
            "tempo_medio_envio": float(metricas['tempo_medio_envio']) if metricas['tempo_medio_envio'] else 0,
            "periodo": {
                "inicio": data_inicio,
                "fim": data_fim
            }
        }
        
        if formato == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Métrica', 'Valor'])
            for key, value in resultado.items():
                if key != 'periodo':
                    writer.writerow([key, value])
            
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'metricas_envios_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            )
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({"error": f"Erro ao obter métricas: {str(e)}"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@metricas_bp.route('/taxa-abertura', methods=['GET'])
@swag_from({
    "tags": ["Métricas"],
    "summary": "Taxa de abertura",
    "description": "Retorna a taxa de abertura dos emails enviados.",
    "parameters": [
        {
            "name": "data_inicio",
            "in": "query",
            "type": "string",
            "format": "date",
            "required": False,
            "description": "Data inicial para filtrar (YYYY-MM-DD)"
        },
        {
            "name": "data_fim",
            "in": "query",
            "type": "string",
            "format": "date",
            "required": False,
            "description": "Data final para filtrar (YYYY-MM-DD)"
        }
    ],
    "responses": {
        200: {"description": "Taxa de abertura"},
        400: {"description": "Parâmetros inválidos"}
    }
})
def taxa_abertura():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Obter parâmetros da query
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        # Construir query base
        query = """
            SELECT 
                COUNT(*) as total_envios,
                SUM(CASE WHEN aberto = true THEN 1 ELSE 0 END) as total_abertos
            FROM agendamentos
            WHERE status = 'enviado'
        """
        params = []
        
        if data_inicio:
            query += " AND data_criacao >= %s"
            params.append(data_inicio)
        
        if data_fim:
            query += " AND data_criacao <= %s"
            params.append(data_fim)
        
        cursor.execute(query, params)
        resultado = cursor.fetchone()
        
        total_envios = resultado['total_envios'] or 0
        total_abertos = resultado['total_abertos'] or 0
        
        taxa = (total_abertos / total_envios * 100) if total_envios > 0 else 0
        
        return jsonify({
            "taxa_abertura": round(taxa, 2),
            "total_envios": total_envios,
            "total_abertos": total_abertos,
            "periodo": {
                "inicio": data_inicio,
                "fim": data_fim
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"Erro ao obter taxa de abertura: {str(e)}"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@metricas_bp.route('/segmentos', methods=['GET'])
@swag_from({
    "tags": ["Métricas"],
    "summary": "Métricas por segmento",
    "description": "Retorna métricas agrupadas por segmento.",
    "parameters": [
        {
            "name": "periodo",
            "in": "query",
            "type": "string",
            "enum": ["7d", "30d", "90d"],
            "required": False,
            "description": "Período de análise (7d = 7 dias, 30d = 30 dias, 90d = 90 dias)"
        }
    ],
    "responses": {
        200: {"description": "Métricas por segmento"}
    }
})
def metricas_segmentos():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Processar período
        periodo = request.args.get('periodo', '30d')
        dias = int(periodo.replace('d', ''))
        data_inicio = datetime.now() - timedelta(days=dias)
        
        query = """
            SELECT 
                s.id as segmento_id,
                s.nome as segmento_nome,
                COUNT(DISTINCT e.id) as total_envios,
                COUNT(DISTINCT m.contato_id) as total_contatos,
                SUM(CASE WHEN m.status = 'entregue' THEN 1 ELSE 0 END) as entregues,
                SUM(CASE WHEN m.status = 'aberto' THEN 1 ELSE 0 END) as abertos,
                SUM(CASE WHEN m.status = 'clicado' THEN 1 ELSE 0 END) as clicados,
                SUM(CASE WHEN m.status = 'respondido' THEN 1 ELSE 0 END) as respondidos
            FROM segmentos s
            LEFT JOIN envios e ON s.id = e.segmento_id
            LEFT JOIN metricas_envio m ON e.id = m.envio_id
            WHERE e.created_at >= %s
            GROUP BY s.id, s.nome
        """
        
        cursor.execute(query, (data_inicio,))
        resultados = cursor.fetchall()
        
        # Calcular taxas
        for resultado in resultados:
            total = resultado['total_contatos'] or 1
            resultado['taxa_entrega'] = round((resultado['entregues'] / total) * 100, 2)
            resultado['taxa_abertura'] = round((resultado['abertos'] / total) * 100, 2)
            resultado['taxa_clique'] = round((resultado['clicados'] / total) * 100, 2)
            resultado['taxa_resposta'] = round((resultado['respondidos'] / total) * 100, 2)
        
        return jsonify(resultados), 200
        
    except Exception as e:
        return jsonify({"error": f"Erro ao gerar métricas por segmento: {str(e)}"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@metricas_bp.route('/contatos/<int:contato_id>', methods=['GET'])
@swag_from({
    "tags": ["Métricas"],
    "summary": "Métricas por contato",
    "description": "Retorna métricas detalhadas de um contato específico.",
    "parameters": [
        {
            "name": "contato_id",
            "in": "path",
            "type": "integer",
            "required": True,
            "description": "ID do contato"
        }
    ],
    "responses": {
        200: {"description": "Métricas do contato"},
        404: {"description": "Contato não encontrado"}
    }
})
def metricas_contato(contato_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Verificar se contato existe
        cursor.execute("SELECT * FROM contatos WHERE id = %s", (contato_id,))
        contato = cursor.fetchone()
        
        if not contato:
            return jsonify({"error": "Contato não encontrado"}), 404
            
        # Buscar métricas do contato
        query = """
            SELECT 
                e.id as envio_id,
                e.created_at as data_envio,
                m.status,
                m.data_evento,
                t.nome as template_nome,
                s.nome as segmento_nome
            FROM envios e
            LEFT JOIN metricas_envio m ON e.id = m.envio_id
            LEFT JOIN templates t ON e.template_id = t.id
            LEFT JOIN segmentos s ON e.segmento_id = s.id
            WHERE m.contato_id = %s
            ORDER BY e.created_at DESC
        """
        
        cursor.execute(query, (contato_id,))
        historico = cursor.fetchall()
        
        # Processar datas
        for evento in historico:
            evento['data_envio'] = evento['data_envio'].isoformat()
            evento['data_evento'] = evento['data_evento'].isoformat()
        
        # Calcular estatísticas
        total_envios = len(historico)
        aberturas = sum(1 for e in historico if e['status'] == 'aberto')
        cliques = sum(1 for e in historico if e['status'] == 'clicado')
        respostas = sum(1 for e in historico if e['status'] == 'respondido')
        
        metricas = {
            "contato": contato,
            "estatisticas": {
                "total_envios": total_envios,
                "taxa_abertura": round((aberturas / total_envios) * 100, 2) if total_envios > 0 else 0,
                "taxa_clique": round((cliques / total_envios) * 100, 2) if total_envios > 0 else 0,
                "taxa_resposta": round((respostas / total_envios) * 100, 2) if total_envios > 0 else 0
            },
            "historico": historico
        }
        
        return jsonify(metricas), 200
        
    except Exception as e:
        return jsonify({"error": f"Erro ao buscar métricas do contato: {str(e)}"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@metricas_bp.route('/', methods=['GET'])
def obter_metricas():
    """Obtém métricas gerais do sistema."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Total de contatos
        cursor.execute("SELECT COUNT(*) as total FROM contatos")
        total_contatos = cursor.fetchone()['total']
        
        # Total de contatos por status
        cursor.execute("""
            SELECT status, COUNT(*) as total 
            FROM contatos 
            GROUP BY status
        """)
        contatos_por_status = {row['status']: row['total'] for row in cursor.fetchall()}
        
        # Total de templates
        cursor.execute("SELECT COUNT(*) as total FROM templates")
        total_templates = cursor.fetchone()['total']
        
        # Total de segmentos
        cursor.execute("SELECT COUNT(*) as total FROM segmentos")
        total_segmentos = cursor.fetchone()['total']
        
        # Total de campanhas por status
        cursor.execute("""
            SELECT status, COUNT(*) as total 
            FROM campanhas 
            GROUP BY status
        """)
        campanhas_por_status = {row['status']: row['total'] for row in cursor.fetchall()}
        
        # Total de agendamentos por status
        cursor.execute("""
            SELECT status, COUNT(*) as total 
            FROM agendamentos 
            GROUP BY status
        """)
        agendamentos_por_status = {row['status']: row['total'] for row in cursor.fetchall()}
        
        # Taxa de sucesso de envios
        cursor.execute("""
            SELECT 
                COUNT(CASE WHEN status = 'sucesso' THEN 1 END) * 100.0 / COUNT(*) as taxa_sucesso,
                COUNT(*) as total_envios,
                COUNT(CASE WHEN status = 'sucesso' THEN 1 END) as envios_sucesso,
                COUNT(CASE WHEN status = 'erro' THEN 1 END) as envios_erro
            FROM logs_envio
        """)
        metricas_envio = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "contatos": {
                "total": total_contatos,
                "por_status": contatos_por_status
            },
            "templates": {
                "total": total_templates
            },
            "segmentos": {
                "total": total_segmentos
            },
            "campanhas": {
                "por_status": campanhas_por_status
            },
            "agendamentos": {
                "por_status": agendamentos_por_status
            },
            "envios": {
                "total": metricas_envio['total_envios'],
                "sucesso": metricas_envio['envios_sucesso'],
                "erro": metricas_envio['envios_erro'],
                "taxa_sucesso": float(metricas_envio['taxa_sucesso'] or 0)
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"Erro ao obter métricas: {str(e)}"}), 500

@metricas_bp.route('/tracking', methods=['GET'])
def metricas_tracking():
    """Retorna métricas de tracking de emails."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Obter período da consulta (padrão: últimos 30 dias)
        data_inicio = request.args.get('inicio')
        data_fim = request.args.get('fim')
        
        if not data_inicio:
            data_inicio = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not data_fim:
            data_fim = datetime.now().strftime('%Y-%m-%d')
            
        # Consultar métricas de tracking
        query = """
            SELECT 
                COUNT(DISTINCT CASE WHEN tipo_evento = 'abertura' THEN envio_id END) as total_aberturas,
                COUNT(DISTINCT CASE WHEN tipo_evento = 'clique' THEN envio_id END) as total_cliques,
                COUNT(DISTINCT envio_id) as total_eventos,
                (SELECT COUNT(*) FROM envios WHERE status = 'enviado' AND DATE(data_envio) BETWEEN %s AND %s) as total_envios
            FROM eventos_tracking
            WHERE DATE(data_evento) BETWEEN %s AND %s
        """
        
        cursor.execute(query, (data_inicio, data_fim, data_inicio, data_fim))
        metricas = cursor.fetchone()
        
        # Calcular taxas
        total_envios = metricas['total_envios'] or 1  # Evitar divisão por zero
        taxa_abertura = (metricas['total_aberturas'] / total_envios) * 100
        taxa_clique = (metricas['total_cliques'] / total_envios) * 100
        
        # Buscar eventos por hora do dia
        query_horarios = """
            SELECT 
                HOUR(data_evento) as hora,
                COUNT(*) as total
            FROM eventos_tracking
            WHERE DATE(data_evento) BETWEEN %s AND %s
            GROUP BY HOUR(data_evento)
            ORDER BY hora
        """
        
        cursor.execute(query_horarios, (data_inicio, data_fim))
        eventos_por_hora = cursor.fetchall()
        
        return jsonify({
            "periodo": {
                "inicio": data_inicio,
                "fim": data_fim
            },
            "metricas": {
                "total_envios": metricas['total_envios'],
                "total_aberturas": metricas['total_aberturas'],
                "total_cliques": metricas['total_cliques'],
                "taxa_abertura": round(taxa_abertura, 2),
                "taxa_clique": round(taxa_clique, 2)
            },
            "eventos_por_hora": eventos_por_hora
        })
        
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close() 

@metricas_bp.route('/tracking/', methods=['GET'])
@swag_from({
    "tags": ["Métricas"],
    "summary": "Obtém métricas de tracking",
    "description": "Retorna estatísticas sobre eventos de tracking (aberturas, cliques, etc)",
    "responses": {
        200: {
            "description": "Métricas de tracking",
            "schema": {
                "type": "object",
                "properties": {
                    "total_eventos": {"type": "integer"},
                    "eventos_por_tipo": {
                        "type": "object",
                        "properties": {
                            "abertura": {"type": "integer"},
                            "clique": {"type": "integer"},
                            "resposta": {"type": "integer"}
                        }
                    },
                    "periodo": {
                        "type": "object",
                        "properties": {
                            "inicio": {"type": "string", "format": "date-time"},
                            "fim": {"type": "string", "format": "date-time"}
                        }
                    }
                }
            }
        }
    }
})
def metricas_tracking_detalhado():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Obter total de eventos e contagem por tipo
        cursor.execute("""
            SELECT 
                COUNT(*) as total_eventos,
                SUM(CASE WHEN tipo_evento = 'abertura' THEN 1 ELSE 0 END) as aberturas,
                SUM(CASE WHEN tipo_evento = 'clique' THEN 1 ELSE 0 END) as cliques,
                SUM(CASE WHEN tipo_evento = 'resposta' THEN 1 ELSE 0 END) as respostas
            FROM eventos_tracking
        """)
        
        result = cursor.fetchone()
        
        # Obter período
        cursor.execute("""
            SELECT 
                MIN(data_evento) as inicio,
                MAX(data_evento) as fim
            FROM eventos_tracking
        """)
        
        periodo = cursor.fetchone()
        
        metricas = {
            "total_eventos": result[0],
            "eventos_por_tipo": {
                "abertura": result[1] or 0,
                "clique": result[2] or 0,
                "resposta": result[3] or 0
            },
            "periodo": {
                "inicio": periodo[0].isoformat() if periodo[0] else None,
                "fim": periodo[1].isoformat() if periodo[1] else None
            }
        }
        
        return jsonify(metricas), 200
        
    except Exception as e:
        print(f"Erro ao obter métricas de tracking: {str(e)}")
        return jsonify({"error": "Erro ao obter métricas"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
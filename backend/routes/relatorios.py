from flask import Blueprint, request, jsonify, send_file
from backend.config import get_db_connection
from flasgger import swag_from
from datetime import datetime, timedelta
import csv
import io
import json

relatorios_bp = Blueprint('relatorios', __name__)

@relatorios_bp.route('/relatorios', methods=['GET'])
@swag_from({
    "tags": ["Relatórios"],
    "summary": "Exportar relatório",
    "description": "Exporta um relatório com métricas de envio em formato CSV.",
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
        200: {"description": "Relatório CSV"},
        400: {"description": "Parâmetros inválidos"}
    }
})
def exportar_relatorio():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Processar parâmetros
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        # Construir query base
        query = """
            SELECT 
                e.created_at as data_envio,
                t.nome as template,
                s.nome as segmento,
                e.status as status_envio,
                COUNT(DISTINCT m.contato_id) as total_contatos,
                SUM(CASE WHEN m.status = 'entregue' THEN 1 ELSE 0 END) as entregues,
                SUM(CASE WHEN m.status = 'aberto' THEN 1 ELSE 0 END) as abertos,
                SUM(CASE WHEN m.status = 'clicado' THEN 1 ELSE 0 END) as clicados,
                SUM(CASE WHEN m.status = 'respondido' THEN 1 ELSE 0 END) as respondidos
            FROM envios e
            JOIN templates t ON e.template_id = t.id
            JOIN segmentos s ON e.segmento_id = s.id
            LEFT JOIN metricas_envio m ON e.id = m.envio_id
        """
        params = []
        
        # Adicionar filtros de data
        if data_inicio:
            query += " WHERE e.created_at >= %s"
            params.append(data_inicio)
            if data_fim:
                query += " AND e.created_at <= %s"
                params.append(data_fim + " 23:59:59")
        elif data_fim:
            query += " WHERE e.created_at <= %s"
            params.append(data_fim + " 23:59:59")
            
        query += " GROUP BY e.id, e.created_at, t.nome, s.nome, e.status"
        query += " ORDER BY e.created_at DESC"
        
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        
        # Preparar dados CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Cabeçalho
        writer.writerow([
            'Data Envio',
            'Template',
            'Segmento',
            'Status Envio',
            'Total Contatos',
            'Entregues',
            'Abertos',
            'Clicados',
            'Respondidos'
        ])
        
        # Dados
        for r in resultados:
            writer.writerow([
                r['data_envio'].strftime('%Y-%m-%d %H:%M:%S'),
                r['template'],
                r['segmento'],
                r['status_envio'],
                r['total_contatos'],
                r['entregues'],
                r['abertos'],
                r['clicados'],
                r['respondidos']
            ])
        
        # Preparar resposta
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'relatorio_envios_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )
        
    except Exception as e:
        return jsonify({"error": f"Erro ao gerar relatório: {str(e)}"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

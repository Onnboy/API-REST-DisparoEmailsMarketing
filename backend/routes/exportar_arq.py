import os
import io
import csv
from flask import Response, Blueprint, request, jsonify, send_file
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfgen import canvas
from backend.config import get_db_connection
from flasgger import swag_from
from datetime import datetime, timedelta

exportar_bp = Blueprint('exportar', __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RELATORIOS_DIR = os.path.join(BASE_DIR, "relatorios")

os.makedirs(RELATORIOS_DIR, exist_ok=True)

def gerar_pdf(resultados):
    """Gera um relatório em PDF com os dados fornecidos."""
    pdf_path = os.path.join(RELATORIOS_DIR, f"relatorio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    
    # Configurar o documento
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    
    # Preparar estilos
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Lista de elementos do PDF
    elements = []
    
    # Título
    elements.append(Paragraph("Relatório de Email Marketing", title_style))
    elements.append(Spacer(1, 20))
    
    # Data do relatório
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", normal_style))
    elements.append(Spacer(1, 20))
    
    # Resumo
    if resultados:
        total_envios = sum(r['total_envios'] for r in resultados)
        total_entregues = sum(r['entregues'] for r in resultados)
        total_abertos = sum(r['abertos'] for r in resultados)
        total_clicados = sum(r['clicados'] for r in resultados)
        total_respondidos = sum(r['respondidos'] for r in resultados)
        
        taxa_entrega = (total_entregues / total_envios * 100) if total_envios > 0 else 0
        taxa_abertura = (total_abertos / total_envios * 100) if total_envios > 0 else 0
        taxa_cliques = (total_clicados / total_envios * 100) if total_envios > 0 else 0
        taxa_resposta = (total_respondidos / total_envios * 100) if total_envios > 0 else 0
        
        elements.append(Paragraph("Resumo Geral", subtitle_style))
        elements.append(Spacer(1, 10))
        
        resumo_data = [
            ["Métrica", "Total", "Taxa"],
            ["Envios", total_envios, "100%"],
            ["Entregues", total_entregues, f"{taxa_entrega:.1f}%"],
            ["Abertos", total_abertos, f"{taxa_abertura:.1f}%"],
            ["Clicados", total_clicados, f"{taxa_cliques:.1f}%"],
            ["Respondidos", total_respondidos, f"{taxa_resposta:.1f}%"]
        ]
        
        resumo_table = Table(resumo_data, colWidths=[200, 100, 100])
        resumo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
        ]))
        elements.append(resumo_table)
        elements.append(Spacer(1, 30))
        
        # Gráfico de métricas
        elements.append(Paragraph("Gráfico de Métricas", subtitle_style))
        elements.append(Spacer(1, 10))
        
        # Detalhes por envio
        elements.append(Paragraph("Detalhes por Envio", subtitle_style))
        elements.append(Spacer(1, 10))
        
        # Cabeçalho da tabela de detalhes
        detalhes_data = [
            ["Data", "Template", "Segmento", "Status", "Envios", "Entregues", "Abertos", "Cliques", "Respostas"]
        ]
        
        # Dados da tabela de detalhes
        for r in resultados:
            detalhes_data.append([
                r['created_at'].strftime('%d/%m/%Y\n%H:%M'),
                r['template_nome'],
                r['segmento_nome'],
                r['status'],
                str(r['total_envios']),
                str(r['entregues']),
                str(r['abertos']),
                str(r['clicados']),
                str(r['respondidos'])
            ])
        
        detalhes_table = Table(detalhes_data, colWidths=[70, 80, 80, 60, 50, 50, 50, 50, 50])
        detalhes_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BOX', (0, 0), (-1, -1), 2, colors.black),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        elements.append(detalhes_table)
        
        # Adicionar seção de análise de horários
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("Análise de Horários", subtitle_style))
        elements.append(Spacer(1, 10))
        
        # Adicionar seção de segmentação
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("Análise por Segmento", subtitle_style))
        elements.append(Spacer(1, 10))
        
        # Adicionar seção de dispositivos
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("Análise por Dispositivo", subtitle_style))
        elements.append(Spacer(1, 10))
        
        # Adicionar seção de recomendações
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("Recomendações", subtitle_style))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph("Com base nas métricas analisadas, recomendamos:", normal_style))
        elements.append(Spacer(1, 5))
        
        if taxa_abertura < 20:
            elements.append(Paragraph("• Melhorar as linhas de assunto para aumentar a taxa de abertura", normal_style))
        if taxa_cliques < 10:
            elements.append(Paragraph("• Otimizar os calls-to-action para aumentar a taxa de cliques", normal_style))
        if taxa_entrega < 95:
            elements.append(Paragraph("• Verificar a qualidade da lista de emails para melhorar a taxa de entrega", normal_style))
    
    # Gerar o PDF
    doc.build(elements)
    return pdf_path

@exportar_bp.route('/export', methods=['GET'])
@swag_from({
    "tags": ["Relatórios"],
    "summary": "Exportar relatório",
    "description": "Exporta um relatório com métricas de envio em formato CSV ou PDF.",
    "parameters": [
        {
            "name": "formato",
            "in": "query",
            "type": "string",
            "required": False,
            "description": "Formato do relatório (csv ou pdf). Padrão é csv."
        },
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
        200: {"description": "Relatório gerado com sucesso"},
        400: {"description": "Parâmetros inválidos"},
        500: {"description": "Erro ao gerar relatório"}
    }
})
def exportar_relatorio():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Processar parâmetros
        formato = request.args.get('formato', 'csv').lower()
        if formato not in ['csv', 'pdf']:
            return jsonify({"error": "Formato inválido. Use 'csv' ou 'pdf'."}), 400
            
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        # Construir query base
        query = """
            SELECT 
                e.created_at,
                t.nome as template_nome,
                s.nome as segmento_nome,
                e.status,
                COUNT(DISTINCT e.id) as total_envios,
                SUM(CASE WHEN me.status = 'delivered' THEN 1 ELSE 0 END) as entregues,
                SUM(CASE WHEN me.status = 'opened' THEN 1 ELSE 0 END) as abertos,
                SUM(CASE WHEN me.status = 'clicked' THEN 1 ELSE 0 END) as clicados,
                SUM(CASE WHEN me.status = 'responded' THEN 1 ELSE 0 END) as respondidos
            FROM envios e
            LEFT JOIN templates t ON e.template_id = t.id
            LEFT JOIN segmentos s ON e.segmento_id = s.id
            LEFT JOIN metricas_envio me ON e.id = me.envio_id
        """
        
        params = []
        where_clauses = []
        
        if data_inicio:
            where_clauses.append("e.created_at >= %s")
            params.append(data_inicio)
        
        if data_fim:
            where_clauses.append("e.created_at <= %s")
            params.append(data_fim)
        
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        
        query += """
            GROUP BY e.created_at, t.nome, s.nome, e.status
            ORDER BY e.created_at DESC
        """
        
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        
        if formato == 'pdf':
            pdf_path = gerar_pdf(resultados)
            return send_file(
                pdf_path,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=os.path.basename(pdf_path)
            )
        else:  # CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_path = os.path.join(RELATORIOS_DIR, f'relatorio_{timestamp}.csv')
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Escrever cabeçalho
                writer.writerow([
                    'Data de Envio',
                    'Template',
                    'Segmento',
                    'Status',
                    'Total de Envios',
                    'Entregues',
                    'Taxa de Entrega (%)',
                    'Abertos',
                    'Taxa de Abertura (%)',
                    'Clicados',
                    'Taxa de Cliques (%)',
                    'Respondidos',
                    'Taxa de Resposta (%)'
                ])
                
                # Escrever dados
                for row in resultados:
                    total_envios = row['total_envios'] or 1
                    taxa_entrega = (row['entregues'] / total_envios) * 100 if row['entregues'] else 0
                    taxa_abertura = (row['abertos'] / total_envios) * 100 if row['abertos'] else 0
                    taxa_cliques = (row['clicados'] / total_envios) * 100 if row['clicados'] else 0
                    taxa_resposta = (row['respondidos'] / total_envios) * 100 if row['respondidos'] else 0
                    
                    writer.writerow([
                        row['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
                        row['template_nome'],
                        row['segmento_nome'],
                        row['status'],
                        row['total_envios'],
                        row['entregues'],
                        f"{taxa_entrega:.1f}",
                        row['abertos'],
                        f"{taxa_abertura:.1f}",
                        row['clicados'],
                        f"{taxa_cliques:.1f}",
                        row['respondidos'],
                        f"{taxa_resposta:.1f}"
                    ])
            
            return send_file(
                csv_path,
                mimetype='text/csv',
                as_attachment=True,
                download_name=os.path.basename(csv_path)
            )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        cursor.close()
        connection.close()

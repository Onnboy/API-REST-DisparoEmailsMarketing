import io
import csv
from flask import Response, Blueprint, request, jsonify
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from backend.config import get_db_connection

exportar_bp = Blueprint('exportar', __name__)

def gerar_pdf():
    """Gera um relatório em PDF a partir dos dados das campanhas."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT id, titulo, taxa_entrega, taxa_abertura, taxa_cliques FROM campanhas")
    campanhas = cursor.fetchall()

    y_position = height - 50  
    c.setFont("Helvetica-Bold", 16)
    c.drawString(150, y_position, "Relatório de Campanhas de E-mail Marketing")
    y_position -= 30

    c.setFont("Helvetica", 12)
    for campanha in campanhas:
        c.drawString(50, y_position, f"ID: {campanha[0]}")
        c.drawString(150, y_position, f"Título: {campanha[1]}")
        c.drawString(350, y_position, f"Entrega: {campanha[2]}%")
        y_position -= 20
        c.drawString(150, y_position, f"Abertura: {campanha[3]}%")
        c.drawString(350, y_position, f"Cliques: {campanha[4]}%")
        y_position -= 30  

        if y_position < 50:  
            c.showPage()
            y_position = height - 50  

    c.save()
    buffer.seek(0)
    return buffer

@exportar_bp.route('/relatorios/export', methods=['GET'])
def exportar_relatorio():
    """Exporta o relatório de campanhas em CSV ou PDF."""
    formato = request.args.get('formato', 'csv')

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, titulo, taxa_entrega, taxa_abertura, taxa_cliques FROM campanhas")
    campanhas = cursor.fetchall()
    cursor.close()
    connection.close()

    if formato == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "titulo", "taxa_entrega", "taxa_abertura", "taxa_cliques"])
        writer.writerows(campanhas)
        response = Response(output.getvalue(), content_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=relatorio.csv"
        return response

    elif formato == 'pdf':
        pdf = gerar_pdf()
        response = Response(pdf, content_type='application/pdf')
        response.headers["Content-Disposition"] = "attachment; filename=relatorio.pdf"
        return response

    else:
        return jsonify({"error": "Formato inválido. Use 'csv' ou 'pdf'."}), 400

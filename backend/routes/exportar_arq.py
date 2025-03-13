import os
import io
import csv
from flask import Response, Blueprint, request, jsonify, send_file
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from backend.config import get_db_connection
from flasgger import swag_from

exportar_bp = Blueprint('exportar', __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RELATORIOS_DIR = os.path.join(BASE_DIR, "relatorios")

os.makedirs(RELATORIOS_DIR, exist_ok=True)

def gerar_pdf():
    """Gera um relatório em PDF na pasta correta e retorna o caminho do arquivo."""
    pdf_path = os.path.join(RELATORIOS_DIR, "relatorio.pdf")
    
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
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

    finally:
        cursor.close()
        connection.close()

    c.save()
    print(f"📄 PDF gerado em: {pdf_path}")
    return pdf_path


@exportar_bp.route('/relatorios/export', methods=['GET'])
@swag_from({
    "tags": ["Relatórios"],
    "summary": "Exportar relatório de campanhas",
    "description": "Exporta o relatório de campanhas em formato CSV ou PDF.",
    "parameters": [
        {
            "name": "formato",
            "in": "query",
            "type": "string",
            "required": False,
            "description": "Formato do relatório (csv ou pdf). Padrão é 'csv'.",
            "example": "csv"
        }
    ],
    "responses": {
        200: {
            "description": "Arquivo gerado com sucesso (CSV ou PDF).",
            "content": {
                "application/pdf": {
                    "schema": {"type": "string", "format": "binary"}
                },
                "text/csv": {
                    "schema": {"type": "string", "format": "binary"}
                }
            }
        },
        400: {
            "description": "Formato inválido.",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {"type": "string", "example": "Formato inválido. Use 'csv' ou 'pdf'."}
                }
            }
        }
    }
})
def exportar_relatorio():
    """Exporta o relatório de campanhas em CSV ou PDF, permitindo download."""
    formato = request.args.get('formato', 'csv')

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT id, titulo, taxa_entrega, taxa_abertura, taxa_cliques FROM campanhas")
    campanhas = cursor.fetchall()
    cursor.close()
    connection.close()

    if formato == 'csv':
        csv_path = os.path.join(RELATORIOS_DIR, "relatorio.csv")
        print(f"📄 Gerando CSV em: {csv_path}")

        with open(csv_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(["id", "titulo", "taxa_entrega", "taxa_abertura", "taxa_cliques"])
            writer.writerows(campanhas)

        print("✅ CSV gerado com sucesso!")
        return send_file(csv_path, as_attachment=True)

    elif formato == 'pdf':
        pdf_path = gerar_pdf()
        return send_file(pdf_path, as_attachment=True)


    else:
        return jsonify({"error": "Formato inválido. Use 'csv' ou 'pdf'."}), 400

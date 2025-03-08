from flask import Blueprint, request, jsonify
from backend.config import get_db_connection
from flasgger import swag_from

relatorios_bp = Blueprint('relatorios', __name__)

@relatorios_bp.route('/relatorios', methods=['GET'])
@swag_from({
    "tags": ["Relatórios"],
    "summary": "Obter relatório de campanhas",
    "description": "Retorna as estatísticas das campanhas, incluindo taxa de entrega, abertura e cliques.",
    "responses": {
        200: {
            "description": "Relatório gerado com sucesso",
            "schema": {
                "type": "object",
                "properties": {
                    "relatorio": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "titulo": {"type": "string"},
                                "status": {"type": "string"},
                                "taxa_entrega": {"type": "float"},
                                "taxa_abertura": {"type": "float"},
                                "taxa_cliques": {"type": "float"}
                            }
                        }
                    }
                }
            }
        },
        500: {
            "description": "Erro ao gerar relatório",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"}
                }
            }
        }
    }
})
def obter_relatorio():
    """Obtém estatísticas das campanhas registradas."""
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT id, titulo, status, 
                   COALESCE(taxa_entrega, 0), 
                   COALESCE(taxa_abertura, 0), 
                   COALESCE(taxa_cliques, 0) 
            FROM campanhas
        """)
        campanhas = cursor.fetchall()

        resultados = [
            {
                "id": c[0],
                "titulo": c[1],
                "status": c[2],
                "taxa_entrega": c[3],
                "taxa_abertura": c[4],
                "taxa_cliques": c[5]
            } 
            for c in campanhas
        ]

        return jsonify({"relatorio": resultados}), 200
    except Exception as e:
        return jsonify({"error": f"Erro ao obter relatório: {str(e)}"}), 500
    finally:
        cursor.close()
        connection.close()

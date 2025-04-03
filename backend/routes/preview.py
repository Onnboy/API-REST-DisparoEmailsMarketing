from flask import Blueprint, request, jsonify, render_template_string
from backend.config import get_db_connection
from flasgger import swag_from
import json

preview_bp = Blueprint('preview', __name__)

@preview_bp.route('/preview/template/<int:template_id>', methods=['POST'])
@swag_from({
    "tags": ["Preview"],
    "summary": "Visualizar prévia do template",
    "description": "Gera uma prévia do template com dados de teste",
    "parameters": [
        {
            "name": "template_id",
            "in": "path",
            "required": True,
            "type": "integer",
            "description": "ID do template"
        },
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "dados_teste": {
                        "type": "object",
                        "example": {
                            "nome": "João Silva",
                            "email": "joao@exemplo.com",
                            "empresa": "Empresa Teste",
                            "cargo": "Gerente"
                        }
                    }
                }
            }
        }
    ],
    "responses": {
        200: {
            "description": "Preview do email gerado com sucesso",
            "schema": {
                "type": "object",
                "properties": {
                    "preview_html": {"type": "string"},
                    "variaveis_utilizadas": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        },
        404: {"description": "Template não encontrado"},
        500: {"description": "Erro interno"}
    }
})
def preview_template(template_id):
    dados = request.get_json()
    dados_teste = dados.get('dados_teste', {})
    
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        # Busca o template
        cursor.execute('SELECT * FROM templates WHERE id = %s', (template_id,))
        template = cursor.fetchone()
        
        if not template:
            return jsonify({'error': 'Template não encontrado'}), 404
            
        # Extrai todas as variáveis do template usando regex
        import re
        variaveis = re.findall(r'\{\{\s*(\w+)\s*\}\}', template['html_content'])
        
        # Gera dados de teste padrão para variáveis não fornecidas
        dados_completos = {
            'nome': 'Nome Teste',
            'email': 'email@teste.com',
            'empresa': 'Empresa Teste',
            'cargo': 'Cargo Teste',
            'data': '01/01/2024'
        }
        dados_completos.update(dados_teste)
        
        # Renderiza o template com os dados
        html_content = template['html_content']
        for var in variaveis:
            valor = dados_completos.get(var, f'[{var}]')
            html_content = html_content.replace(f'{{{{ {var} }}}}', str(valor))
        
        return jsonify({
            'preview_html': html_content,
            'variaveis_utilizadas': list(set(variaveis))
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@preview_bp.route('/preview/html', methods=['POST'])
@swag_from({
    "tags": ["Preview"],
    "summary": "Visualizar prévia de HTML personalizado",
    "description": "Gera uma prévia de um HTML personalizado com dados de teste",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "html_content": {
                        "type": "string",
                        "example": "<h1>Olá {{ nome }}!</h1><p>Bem-vindo à {{ empresa }}!</p>"
                    },
                    "dados_teste": {
                        "type": "object",
                        "example": {
                            "nome": "João Silva",
                            "empresa": "Empresa Teste"
                        }
                    }
                },
                "required": ["html_content"]
            }
        }
    ],
    "responses": {
        200: {
            "description": "Preview do email gerado com sucesso",
            "schema": {
                "type": "object",
                "properties": {
                    "preview_html": {"type": "string"},
                    "variaveis_utilizadas": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                }
            }
        },
        400: {"description": "Dados inválidos"},
        500: {"description": "Erro interno"}
    }
})
def preview_html():
    dados = request.get_json()
    
    if not dados or 'html_content' not in dados:
        return jsonify({'error': 'HTML content é obrigatório'}), 400
        
    html_content = dados['html_content']
    dados_teste = dados.get('dados_teste', {})
    
    try:
        # Extrai todas as variáveis do template usando regex
        import re
        variaveis = re.findall(r'\{\{\s*(\w+)\s*\}\}', html_content)
        
        # Gera dados de teste padrão para variáveis não fornecidas
        dados_completos = {
            'nome': 'Nome Teste',
            'email': 'email@teste.com',
            'empresa': 'Empresa Teste',
            'cargo': 'Cargo Teste',
            'data': '01/01/2024'
        }
        dados_completos.update(dados_teste)
        
        # Renderiza o template com os dados
        for var in variaveis:
            valor = dados_completos.get(var, f'[{var}]')
            html_content = html_content.replace(f'{{{{ {var} }}}}', str(valor))
        
        return jsonify({
            'preview_html': html_content,
            'variaveis_utilizadas': list(set(variaveis))
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 
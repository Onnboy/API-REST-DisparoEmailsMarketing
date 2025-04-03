import requests
import json

def test_criar_template():
    """Testa a criação de um template."""
    
    # Dados do template
    template_data = {
        "nome": "Template de Teste",
        "descricao": "Template para testar a API",
        "html_content": "<html><body><h1>Olá {nome}!</h1><p>Este é um teste.</p></body></html>",
        "css_content": "body { font-family: Arial; }"
    }
    
    # Fazer a requisição POST
    response = requests.post(
        'http://localhost:5000/api/templates',
        json=template_data
    )
    
    # Imprimir resultado
    print(f"\nStatus: {response.status_code}")
    print(f"Resposta: {response.text}")
    
    # Verificar se deu certo
    if response.status_code == 201:
        print("✓ Template criado com sucesso!")
        template_id = response.json()['id']
        
        # Tentar buscar o template criado
        get_response = requests.get(f'http://localhost:5000/api/templates')
        print(f"\nBuscando templates...")
        print(f"Status: {get_response.status_code}")
        print(f"Resposta: {get_response.text}")
    else:
        print(f"✗ Erro ao criar template: {response.text}")

if __name__ == '__main__':
    test_criar_template() 
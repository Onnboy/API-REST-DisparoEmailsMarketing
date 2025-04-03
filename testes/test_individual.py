import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://localhost:5000/api'

def test_criar_integracao():
    """Testa a criação de uma integração SMTP."""
    integracao_data = {
        "tipo": "smtp",
        "configuracao": {
            "host": "smtp.gmail.com",
            "port": 587,
            "username": "teste@gmail.com",
            "password": "senha123",
            "use_tls": True
        }
    }
    
    response = requests.post(f'{BASE_URL}/integracoes', json=integracao_data)
    print("\nTestando criação de integração SMTP...")
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.text}")
    return response.status_code == 201

def test_criar_template():
    """Testa a criação de um template."""
    template_data = {
        "nome": "Template de Teste",
        "descricao": "Template para testar a API",
        "html_content": "<html><body><h1>Olá {nome}!</h1><p>Este é um teste.</p></body></html>",
        "css_content": "body { font-family: Arial; }"
    }
    
    response = requests.post(f'{BASE_URL}/templates', json=template_data)
    print("\nTestando criação de template...")
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.text}")
    return response.status_code == 201

def test_criar_contato():
    """Testa a criação de um contato."""
    contato_data = {
        "email": "teste@exemplo.com",
        "nome": "Usuário Teste"
    }
    
    response = requests.post(f'{BASE_URL}/contatos', json=contato_data)
    print("\nTestando criação de contato...")
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.text}")
    return response.status_code == 201

def test_criar_segmento():
    """Testa a criação de um segmento."""
    segmento_data = {
        "nome": "Segmento Teste",
        "descricao": "Segmento para testar a API",
        "criterios": {
            "status": "ativo"
        }
    }
    
    response = requests.post(f'{BASE_URL}/segmentos', json=segmento_data)
    print("\nTestando criação de segmento...")
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.text}")
    return response.status_code == 201

def test_criar_agendamento():
    """Testa a criação de um agendamento."""
    # Primeiro precisamos ter certeza que temos um template e um segmento
    template_response = requests.get(f'{BASE_URL}/templates')
    segmento_response = requests.get(f'{BASE_URL}/segmentos')
    
    if template_response.status_code != 200 or segmento_response.status_code != 200:
        print("Erro: Necessário ter template e segmento cadastrados")
        return False
    
    template_id = template_response.json()[0]['id']
    segmento_id = segmento_response.json()[0]['id']
    
    # Data de envio para amanhã
    amanha = datetime.now() + timedelta(days=1)
    data_envio = amanha.strftime("%Y-%m-%d %H:%M:%S")
    
    agendamento_data = {
        "template_id": template_id,
        "segmento_id": segmento_id,
        "assunto": "Teste de Agendamento",
        "data_envio": data_envio,
        "dados_padrao": {
            "nome": "Usuário"
        }
    }
    
    response = requests.post(f'{BASE_URL}/agendamentos', json=agendamento_data)
    print("\nTestando criação de agendamento...")
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.text}")
    return response.status_code == 201

def executar_testes():
    """Executa todos os testes em sequência."""
    print("Iniciando testes individuais...")
    
    # Lista de testes a serem executados
    testes = [
        ("Integração", test_criar_integracao),
        ("Template", test_criar_template),
        ("Contato", test_criar_contato),
        ("Segmento", test_criar_segmento),
        ("Agendamento", test_criar_agendamento)
    ]
    
    # Executar cada teste
    resultados = []
    for nome, teste in testes:
        print(f"\n{'='*50}")
        print(f"Executando teste de {nome}")
        print('='*50)
        try:
            sucesso = teste()
            resultados.append((nome, sucesso))
        except Exception as e:
            print(f"Erro ao executar teste: {str(e)}")
            resultados.append((nome, False))
    
    # Exibir resumo
    print("\n\nResumo dos testes:")
    print('='*50)
    for nome, sucesso in resultados:
        status = "✓" if sucesso else "✗"
        print(f"{status} {nome}")
    print('='*50)

if __name__ == '__main__':
    executar_testes() 
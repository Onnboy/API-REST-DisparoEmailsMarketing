import requests
import json
from datetime import datetime, timedelta
import time

BASE_URL = 'http://localhost:5001/api'

def test_sequencia():
    """Executa os testes em uma sequência lógica de dependências."""
    print("Iniciando testes em sequência...")
    
    # 1. Primeiro, criar uma integração SMTP
    print("\n1. Criando integração SMTP...")
    integracao_data = {
        "tipo": "smtp",
        "configuracao": {
            "host": "smtp.gmail.com",
            "port": 587,
            "username": "teste@gmail.com",
            "password": "senha123"
        }
    }
    response = requests.post(f'{BASE_URL}/integracoes/', json=integracao_data)
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.text}")
    if response.status_code != 201:
        print("❌ Falha ao criar integração")
        return
    
    # 2. Criar um template com pixel de tracking
    print("\n2. Criando template...")
    template_data = {
        "nome": "Template de Teste",
        "descricao": "Template para testar a API",
        "html_content": """
            <html>
            <body>
                <h1>Olá {nome}!</h1>
                <p>Este é um teste.</p>
                <p><a href="http://localhost:5001/api/tracking/click/{envio_id}/https://www.example.com">Clique aqui</a></p>
                <img src="http://localhost:5001/api/tracking/pixel/{envio_id}" alt="" width="1" height="1" />
            </body>
            </html>
        """,
        "css_content": "body { font-family: Arial; }"
    }
    response = requests.post(f'{BASE_URL}/templates/', json=template_data)
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.text}")
    if response.status_code != 201:
        print("❌ Falha ao criar template")
        return
    template_id = response.json()['id']
    
    # 3. Criar alguns contatos
    print("\n3. Criando contatos...")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    contatos = [
        {"email": f"teste1_{timestamp}@exemplo.com", "nome": "Usuário 1"},
        {"email": f"teste2_{timestamp}@exemplo.com", "nome": "Usuário 2"}
    ]
    for contato in contatos:
        response = requests.post(f'{BASE_URL}/contatos/', json=contato)
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text}")
        if response.status_code != 201:
            print("❌ Falha ao criar contato")
            return
    
    # 4. Criar um segmento
    print("\n4. Criando segmento...")
    segmento_data = {
        "nome": "Segmento Teste",
        "descricao": "Segmento para testar a API",
        "criterios": {
            "status": "ativo"
        }
    }
    response = requests.post(f'{BASE_URL}/segmentos/', json=segmento_data)
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.text}")
    if response.status_code != 201:
        print("❌ Falha ao criar segmento")
        return
    segmento_id = response.json()['id']
    
    # 5. Criar um agendamento
    print("\n5. Criando agendamento...")
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
    response = requests.post(f'{BASE_URL}/agendamentos/', json=agendamento_data)
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.text}")
    if response.status_code != 201:
        print("❌ Falha ao criar agendamento")
        return
    agendamento_id = response.json()['id']
    
    # 6. Verificar status do agendamento
    print("\n6. Verificando status do agendamento...")
    response = requests.get(f'{BASE_URL}/agendamentos/{agendamento_id}/')
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.text}")
    
    # 7. Verificar métricas de envio
    print("\n7. Verificando métricas de envio...")
    response = requests.get(f'{BASE_URL}/metricas/envios/')
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.text}")
    
    # 8. Testar endpoints de tracking
    print("\n8. Testando endpoints de tracking...")
    
    # Verificar se existem envios antes de testar tracking
    response = requests.get(f'{BASE_URL}/envios/')
    envios = response.json()
    print(f"Envios encontrados: {envios}")
    
    if envios and len(envios) > 0:
        envio_id = envios[0]['id']  # Pega o primeiro envio
        print(f"Usando envio_id: {envio_id}")
        # Simular abertura de email
        tracking_response = requests.get(f'{BASE_URL}/tracking/pixel/{envio_id}', allow_redirects=False)
        print(f"Status do tracking de abertura: {tracking_response.status_code}")
        if tracking_response.status_code == 200:
            print("✅ Tracking de pixel funcionando corretamente")
        else:
            print("❌ Erro no tracking de pixel")
        
        # Simular clique em link
        tracking_response = requests.get(f'{BASE_URL}/tracking/click/{envio_id}/https%3A%2F%2Fwww.example.com/', allow_redirects=False)
        print(f"Status do tracking de clique: {tracking_response.status_code}")
    else:
        print("Nenhum envio encontrado para testar tracking")
    
    # 9. Verificar eventos de tracking
    print("\n9. Verificando eventos de tracking...")
    response = requests.get(f'{BASE_URL}/metricas/tracking/')
    print(f"Status: {response.status_code}")
    print(f"Resposta: {response.text}")

if __name__ == '__main__':
    test_sequencia() 
import requests
import json
from datetime import datetime, timedelta
import time
import subprocess
import sys
import os

# Configuração
BASE_URL = 'http://localhost:5000'
HEADERS = {'Content-Type': 'application/json'}

def limpar_dados():
    """Limpa todos os dados existentes."""
    print("\nLimpando dados existentes...")
    
    # Limpar logs de envio
    response = requests.get(f'{BASE_URL}/logs/')
    if response.status_code == 200:
        logs = response.json()
        for log in logs:
            requests.delete(f'{BASE_URL}/logs/{log["id"]}/')
    
    # Limpar agendamentos
    response = requests.get(f'{BASE_URL}/agendamentos/')
    if response.status_code == 200:
        agendamentos = response.json()
        for agendamento in agendamentos:
            requests.delete(f'{BASE_URL}/agendamentos/{agendamento["id"]}/')
    
    # Limpar campanhas
    response = requests.get(f'{BASE_URL}/campanhas/')
    if response.status_code == 200:
        campanhas = response.json()
        for campanha in campanhas:
            requests.delete(f'{BASE_URL}/campanhas/{campanha["id"]}/')
    
    # Limpar contatos
    response = requests.get(f'{BASE_URL}/emails/')
    if response.status_code == 200:
        contatos = response.json()
        for contato in contatos:
            requests.delete(f'{BASE_URL}/emails/{contato["id"]}/')
    
    # Limpar segmentos
    response = requests.get(f'{BASE_URL}/segmentos/')
    if response.status_code == 200:
        segmentos = response.json()
        for segmento in segmentos:
            requests.delete(f'{BASE_URL}/segmentos/{segmento["id"]}/')
    
    # Limpar templates
    response = requests.get(f'{BASE_URL}/templates/')
    if response.status_code == 200:
        templates = response.json()
        for template in templates:
            requests.delete(f'{BASE_URL}/templates/{template["id"]}/')
    
    print("Dados limpos.\n")

def test_fluxo_completo():
    """Testa o fluxo completo do sistema."""
    print("\n=== Iniciando teste de fluxo completo ===\n")
    
    # Limpar dados existentes
    limpar_dados()
    
    # 1. Configurar integrações (SMTP e Webhook)
    print("1. Configurando integrações...")
    
    # Configurar SMTP
    smtp_data = {
        "tipo": "smtp",
        "configuracao": {
            "host": "smtp.gmail.com",
            "port": 587,
            "username": "seu-email@gmail.com",
            "password": "sua-senha",
            "use_tls": True
        }
    }
    response = requests.post(f'{BASE_URL}/integracoes/', json=smtp_data)
    print(f"Status SMTP: {response.status_code}")
    if response.status_code != 201:
        raise Exception(f"Erro ao configurar SMTP: {response.text}")
    
    # Configurar Webhook
    webhook_data = {
        "tipo": "webhook",
        "configuracao": {
            "url": "https://seu-webhook.com/notificacoes",
            "eventos": ["email_enviado", "email_erro"]
        }
    }
    response = requests.post(f'{BASE_URL}/integracoes/', json=webhook_data)
    print(f"Status Webhook: {response.status_code}")
    if response.status_code != 201:
        raise Exception(f"Erro ao configurar Webhook: {response.text}")
    
    # 2. Criar template
    print("\n2. Criando template...")
    template_data = {
        "nome": "Template de Boas-vindas",
        "html_content": """
            <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; }
                        .header { background-color: #f8f9fa; padding: 20px; }
                        .content { padding: 20px; }
                        .footer { background-color: #f8f9fa; padding: 20px; text-align: center; }
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>Bem-vindo(a), {nome}!</h1>
                    </div>
                    <div class="content">
                        <p>Olá {nome},</p>
                        <p>Estamos muito felizes em ter você conosco!</p>
                        <p>Seu cadastro foi realizado com sucesso.</p>
                        <p>Atenciosamente,<br>Equipe</p>
                    </div>
                    <div class="footer">
                        <p>Este é um email automático, por favor não responda.</p>
                    </div>
                </body>
            </html>
        """
    }
    response = requests.post(f'{BASE_URL}/templates/', json=template_data)
    print(f"Status: {response.status_code}")
    if response.status_code != 201:
        raise Exception(f"Erro ao criar template: {response.text}")
    template_id = response.json()['id']
    print(f"Template criado com ID: {template_id}")
    
    # 3. Adicionar contatos
    print("\n3. Adicionando contatos...")
    contatos = [
        {"email": "teste1@exemplo.com", "nome": "Teste 1"},
        {"email": "teste2@exemplo.com", "nome": "Teste 2"},
        {"email": "teste3@exemplo.com", "nome": "Teste 3"}
    ]
    for contato in contatos:
        response = requests.post(f'{BASE_URL}/emails/', json=contato)
        print(f"Status para {contato['email']}: {response.status_code}")
        if response.status_code != 201:
            raise Exception(f"Erro ao adicionar contato: {response.text}")
    print("Contatos adicionados com sucesso")
    
    # 4. Criar segmento
    print("\n4. Criando segmento...")
    segmento_data = {
        "nome": "Novos Usuários",
        "descricao": "Usuários que se cadastraram recentemente",
        "criterios": {
            "status": "ativo",
            "data_cadastro": "ultimos_30_dias"
        }
    }
    response = requests.post(f'{BASE_URL}/segmentos/', json=segmento_data)
    print(f"Status: {response.status_code}")
    if response.status_code != 201:
        raise Exception(f"Erro ao criar segmento: {response.text}")
    segmento_id = response.json()['id']
    print(f"Segmento criado com ID: {segmento_id}")
    
    # 5. Criar campanha
    print("\n5. Criando campanha...")
    campanha_data = {
        "titulo": "Campanha de Boas-vindas",
        "descricao": "Envio de email de boas-vindas para novos usuários",
        "template_id": template_id,
        "segmento_id": segmento_id
    }
    response = requests.post(f'{BASE_URL}/campanhas/', json=campanha_data)
    print(f"Status: {response.status_code}")
    if response.status_code != 201:
        raise Exception(f"Erro ao criar campanha: {response.text}")
    campanha_id = response.json()['id']
    print(f"Campanha criada com ID: {campanha_id}")
    
    # 6. Criar agendamento
    print("\n6. Criando agendamento...")
    data_envio = (datetime.now() + timedelta(days=1)).isoformat()
    agendamento_data = {
        "template_id": template_id,
        "segmento_id": segmento_id,
        "assunto": "Bem-vindo(a) ao nosso sistema!",
        "data_envio": data_envio,
        "dados_padrao": {
            "nome": "Usuário"
        }
    }
    response = requests.post(f'{BASE_URL}/agendamentos/', json=agendamento_data)
    print(f"Status: {response.status_code}")
    if response.status_code != 201:
        raise Exception(f"Erro ao criar agendamento: {response.text}")
    agendamento_id = response.json()['id']
    print(f"Agendamento criado com ID: {agendamento_id}")
    
    # 7. Verificar métricas
    print("\n7. Verificando métricas...")
    response = requests.get(f'{BASE_URL}/metricas/')
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        raise Exception(f"Erro ao obter métricas: {response.text}")
    metricas = response.json()
    print(f"Métricas: {json.dumps(metricas, indent=2)}")
    
    # 8. Verificar relatórios
    print("\n8. Verificando relatórios...")
    response = requests.get(f'{BASE_URL}/relatorios/')
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        raise Exception(f"Erro ao obter relatórios: {response.text}")
    relatorios = response.json()
    print(f"Relatórios: {json.dumps(relatorios, indent=2)}")
    
    # 9. Verificar status do sistema
    print("\n9. Verificando status do sistema...")
    response = requests.get(f'{BASE_URL}/status/')
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        raise Exception(f"Erro ao verificar status: {response.text}")
    status = response.json()
    print(f"Status do sistema: {json.dumps(status, indent=2)}")
    
    print("\n=== Teste de fluxo completo finalizado com sucesso ===\n")

if __name__ == "__main__":
    test_fluxo_completo() 
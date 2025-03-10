import requests
import random
import time

BASE_URL = "http://127.0.0.1:5000"

def testar_criacao_email():
    print("\n🔹 Testando criação de e-mail...")
    dados = {"email": f"teste{random.randint(1000,9999)}@gmail.com", "nome": "Usuário Teste"}
    try:
        resposta = requests.post(f"{BASE_URL}/emails", json=dados)
        exibir_resposta(resposta, sucesso_msg="E-mail criado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar e-mail: {e}")
    time.sleep(1)

def exibir_resposta(resposta, sucesso_msg="", erro_msg="❌ Ocorreu um erro"):
    try:
        if resposta.ok:
            print(f"✅ {sucesso_msg}" if sucesso_msg else resposta.json())
        else:
            print(f"{erro_msg}: {resposta.status_code} - {resposta.text}")
    except requests.exceptions.JSONDecodeError:
        print(f"{erro_msg}: Resposta não é um JSON válido. Status: {resposta.status_code}")


def testar_listagem_emails():
    print("\n🔹 Testando listagem de e-mails...")

    try:
        resposta = requests.get(f"{BASE_URL}/emails")
        if resposta.status_code == 200:
            emails = resposta.json()
            print(emails)
            return emails
        else:
            print(f"❌ Erro ao listar e-mails: {resposta.status_code}")
            return []
    except Exception as e:
        print(f"❌ Erro ao listar e-mails: {e}")
        return []

def testar_atualizacao_email():
    print("\n🔹 Testando atualização de e-mail...")

    emails = testar_listagem_emails()
    if not emails:
        print("❌ Nenhum e-mail encontrado. Teste cancelado.")
        return

    email_id = emails[0]["id"]
    dados = {"email": f"novo{random.randint(1000,9999)}@email.com"}

    try:
        resposta = requests.put(f"{BASE_URL}/emails/{email_id}", json=dados)
        print(resposta.json())
    except Exception as e:
        print(f"❌ Erro ao atualizar e-mail: {e}")

    time.sleep(1)

def testar_remocao_email():
    print("\n🔹 Testando remoção de e-mail...")

    emails = testar_listagem_emails()
    if not emails:
        print("❌ Nenhum e-mail encontrado. Teste cancelado.")
        return

    email_id = emails[0]["id"]
    
    try:
        resposta = requests.delete(f"{BASE_URL}/emails/{email_id}")
        print(resposta.json())
    except Exception as e:
        print(f"❌ Erro ao remover e-mail: {e}")

    time.sleep(1)

def testar_agendamento_envio():
    print("\n🔹 Testando agendamento de envio...")
    dados = {"campanha_id": 1, "data_envio": "2025-03-10 10:00:00"}

    try:
        resposta = requests.post(f"{BASE_URL}/envios/agendados", json=dados)
        print(resposta.json())
    except Exception as e:
        print(f"❌ Erro ao agendar envio: {e}")

    time.sleep(1)

def testar_registro_envio():
    print("\n🔹 Testando registro de envio...")

    resposta_campanhas = requests.get(f"{BASE_URL}/campanhas")
    campanhas = resposta_campanhas.json() if resposta_campanhas.ok else []
    if not campanhas:
        print("❌ Nenhuma campanha encontrada. Teste cancelado.")
        return

    resposta_emails = requests.get(f"{BASE_URL}/emails")
    emails = resposta_emails.json() if resposta_emails.ok else []
    if not emails:
        print("❌ Nenhum e-mail encontrado. Teste cancelado.")
        return

    dados = {"campanha_id": campanhas[0]["id"], "email_id": emails[0]["id"]}
    resposta = requests.post(f"{BASE_URL}/envios", json=dados)
    exibir_resposta(resposta, sucesso_msg="Envio registrado com sucesso!")
    time.sleep(1)


def testar_registro_abertura():
    print("\n🔹 Testando registro de abertura...")
    dados = {"campanha_id": 1}
    resposta = requests.post(f"{BASE_URL}/abertura", json=dados)
    print(resposta.json())

def testar_registro_clique():
    print("\n🔹 Testando registro de clique...")
    dados = {"campanha_id": 1}
    resposta = requests.post(f"{BASE_URL}/clique", json=dados)
    print(resposta.json())

def testar_obter_relatorio():
    print("\n🔹 Testando obtenção de relatório...")
    
    try:
        resposta = requests.get(f"{BASE_URL}/relatorios")
        print(resposta.json())
    except Exception as e:
        print(f"❌ Erro ao obter relatório: {e}")

    time.sleep(1)

def testar_exportacao_csv():
    print("\n🔹 Testando exportação de relatório em CSV...")

    try:
        resposta = requests.get(f"{BASE_URL}/relatorios/export?formato=csv")
        
        if resposta.status_code == 200 and resposta.headers.get("Content-Type") == "text/csv":
            print("✅ Exportação de CSV bem-sucedida!")
        else:
            print(f"❌ Erro na exportação de CSV: {resposta.status_code}")
    except Exception as e:
        print(f"❌ Erro ao exportar CSV: {e}")

    time.sleep(1)

def testar_exportacao_pdf():
    print("\n🔹 Testando exportação de relatório em PDF...")

    try:
        resposta = requests.get(f"{BASE_URL}/relatorios/export?formato=pdf")
        
        if resposta.status_code == 200 and resposta.headers.get("Content-Type") == "application/pdf":
            print("✅ Exportação de PDF bem-sucedida!")
        else:
            print(f"❌ Erro na exportação de PDF: {resposta.status_code}")
    except Exception as e:
        print(f"❌ Erro ao exportar PDF: {e}")

    time.sleep(1)

def testar_envio_email_template():
    print("\n🔹 Testando envio de e-mail com template...")
    dados = {
        "email": "teste@email.com",
        "subject": "Promoção Exclusiva!",
        "content": "<h1>Olá, {{ nome }}!</h1><p>Aproveite nossa promoção exclusiva.</p>"
    }

    try:
        resposta = requests.post(f"{BASE_URL}/send-email-template", json=dados)
        print(resposta.json())
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail com template: {e}")

    time.sleep(1)

def testar_envio_email_com_anexo():
    print("\n🔹 Testando envio de e-mail com anexo...")

    dados = {
        "email": "teste@email.com",
        "subject": "Comprovante de Compra",
        "content": "<h1>Olá!</h1><p>Segue seu comprovante em anexo.</p>",
        "attachments": [
            {"name": "comprovante.pdf", "path": "arquivos/comprovante.pdf"}
        ]
    }

    try:
        resposta = requests.post(f"{BASE_URL}/send-email-template", json=dados)
        print(resposta.json())
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail com anexo: {e}")

    time.sleep(1)

if __name__ == "__main__":
    testar_criacao_email()
    testar_listagem_emails()
    testar_atualizacao_email()
    testar_remocao_email()
    testar_agendamento_envio()
    testar_registro_envio()
    testar_registro_abertura()
    testar_registro_clique()
    testar_obter_relatorio()
    testar_exportacao_csv()
    testar_exportacao_pdf()
    testar_envio_email_template()
    testar_envio_email_com_anexo()
import requests
import os
from backend.config import SENDINBLUE_API_KEY, SENDINBLUE_DEFAULT_SENDER
import base64

def send_email(destinatario, assunto, conteudo, attachments=None):
    url = "https://api.sendinblue.com/v3/smtp/email"
    headers = {
        "api-key": SENDINBLUE_API_KEY,
        "Content-Type": "application/json",
    }

    data = {
        "sender": {"name": "Seu Nome", "email": SENDINBLUE_DEFAULT_SENDER},
        "to": [{"email": destinatario}],
        "subject": assunto,
        "htmlContent": conteudo,
    }

    # Processar anexos
    if attachments:
        anexos_base64 = []
        for attachment in attachments:
            file_path = attachment.get("caminho")  # <- pega o caminho correto
            if file_path and os.path.exists(file_path):
                with open(file_path, "rb") as file:
                    encoded_content = base64.b64encode(file.read()).decode("utf-8")
                    nome_arquivo = os.path.basename(file_path)
                    anexos_base64.append({
                        "name": nome_arquivo,
                        "content": encoded_content
                    })
        if anexos_base64:
            data["attachment"] = anexos_base64

    response = requests.post(url, headers=headers, json=data)
    
    try:
        response.raise_for_status()  # Vai lançar erro se status != 200
        return True  # sucesso
    except requests.exceptions.RequestException as e:
        print("Erro ao enviar e-mail:", e)
        print("Resposta:", response.text)  # para depurar o erro da API
        return False  # falhou
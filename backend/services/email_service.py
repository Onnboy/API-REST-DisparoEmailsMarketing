import os
import sendgrid
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv

# Carrega as variáveis do .env
load_dotenv()

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_DEFAULT_SENDER = os.getenv("SENDGRID_DEFAULT_SENDER")

# Debug: Verifica se as chaves foram carregadas corretamente
print(f"Debug: Chave SendGrid carregada? {bool(SENDGRID_API_KEY)}")
print(f"Debug: Email remetente padrão? {SENDGRID_DEFAULT_SENDER}")

if not SENDGRID_API_KEY:
    raise ValueError("ERRO: A chave SENDGRID_API_KEY não foi carregada!")

if not SENDGRID_DEFAULT_SENDER:
    raise ValueError("ERRO: O remetente padrão SENDGRID_DEFAULT_SENDER não foi carregado!")

sg = sendgrid.SendGridAPIClient(SENDGRID_API_KEY)

def send_email(to_email, subject, content):
    message = Mail(
        from_email=SENDGRID_DEFAULT_SENDER,
        to_emails=to_email,
        subject=subject,
        html_content=content
    )
    try:
        response = sg.send(message)
        print(f"Debug: Resposta SendGrid {response.status_code}")
        return response.status_code
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return str(e)

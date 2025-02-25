import os
import mysql.connector
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

# Configuração do banco de dados
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "71208794"),
        database=os.getenv("DB_NAME", "base_emails_marketing")
    )

# Configuração do SendGrid
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
MAIL_DEFAULT_SENDER = os.getenv("SENDGRID_DEFAULT_SENDER")

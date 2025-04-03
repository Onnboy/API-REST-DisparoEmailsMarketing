import os
import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados MySQL."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='71208794',
            database='base_emails_marketing'
        )
        return connection
    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        raise

SENDINBLUE_API_KEY = os.getenv("SENDINBLUE_API_KEY")
SENDINBLUE_DEFAULT_SENDER = os.getenv("SENDINBLUE_DEFAULT_SENDER")

class Config:
    # Configurações do banco de dados
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'base_emails_marketing')

    # Configurações da aplicação
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev')
    DEBUG = os.getenv('FLASK_ENV', 'development') == 'development'

    # Configurações de email
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', '')

    # Configurações de webhook
    WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
    WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET', '')

    # Configurações de agendamento
    SCHEDULER_API_ENABLED = True
    JOBS = []

    # Configurações do Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

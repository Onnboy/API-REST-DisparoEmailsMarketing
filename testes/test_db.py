import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

try:
    connection = mysql.connector.connect(
        host="localhost",
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    print("✅ Conexão bem-sucedida ao banco de dados!")
    connection.close()
except mysql.connector.Error as err:
    print(f"❌ Erro ao conectar ao banco de dados: {err}")

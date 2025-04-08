import os
import mysql.connector
from mysql.connector import Error

def init_db():
    """Inicializa o banco de dados com o schema definido."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '71208794')
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            with open(schema_path, 'r') as file:
                sql_commands = file.read()
                
            for command in sql_commands.split(';'):
                if command.strip():
                    cursor.execute(command + ';')
            
            connection.commit()
            print("Banco de dados inicializado com sucesso!")
            
    except Error as e:
        print(f"Erro ao inicializar o banco de dados: {e}")
        
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

def get_db_connection():
    """Retorna uma conexão com o banco de dados."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '71208794'),
            database=os.getenv('DB_NAME', 'base_emails_marketing')
        )
        return connection
    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None 

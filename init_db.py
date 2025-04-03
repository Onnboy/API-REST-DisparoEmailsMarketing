import mysql.connector
from mysql.connector import Error

def init_database():
    try:
        # Conectar ao MySQL sem selecionar um banco de dados
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='71208794'
        )
        
        cursor = connection.cursor()
        
        # Criar o banco de dados se não existir
        cursor.execute("CREATE DATABASE IF NOT EXISTS base_emails_marketing")
        cursor.execute("USE base_emails_marketing")
        
        # Criar tabelas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS templates (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                descricao TEXT,
                html_content TEXT NOT NULL,
                css_content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS segmentos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                descricao TEXT,
                criterios JSON NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS campanhas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titulo VARCHAR(255) NOT NULL,
                mensagem TEXT NOT NULL,
                template_id INT,
                segmento_id INT,
                data_envio DATETIME,
                status VARCHAR(50) DEFAULT 'pendente',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (template_id) REFERENCES templates(id),
                FOREIGN KEY (segmento_id) REFERENCES segmentos(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contatos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL UNIQUE,
                dados_adicionais JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS envios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                campanha_id INT NOT NULL,
                contato_id INT NOT NULL,
                status VARCHAR(50) DEFAULT 'pendente',
                data_envio DATETIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (campanha_id) REFERENCES campanhas(id),
                FOREIGN KEY (contato_id) REFERENCES contatos(id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metricas_envio (
                id INT AUTO_INCREMENT PRIMARY KEY,
                envio_id INT NOT NULL,
                status ENUM('delivered', 'opened', 'clicked', 'responded') NOT NULL,
                data_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                detalhes JSON,
                FOREIGN KEY (envio_id) REFERENCES envios(id)
            )
        """)
        
        connection.commit()
        print("Banco de dados e tabelas criados com sucesso!")
        
    except Error as e:
        print(f"Erro ao criar banco de dados: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    init_database() 
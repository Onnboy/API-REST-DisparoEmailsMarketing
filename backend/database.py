from .config import get_db_connection

def init_db():
    """Inicializa o banco de dados criando as tabelas necessárias."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Criar tabela de integrações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS integracoes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            tipo VARCHAR(50) NOT NULL,
            configuracao JSON NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """)
    
    # Criar tabela de templates
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
    
    # Criar tabela de emails
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            nome VARCHAR(255),
            categoria VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """)
    
    # Criar tabela de segmentos
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
    
    # Criar tabela de campanhas
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
    
    # Criar tabela de agendamentos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            template_id INT NOT NULL,
            segmento_id INT NOT NULL,
            assunto VARCHAR(255) NOT NULL,
            data_envio DATETIME NOT NULL,
            dados_padrao JSON,
            status VARCHAR(50) DEFAULT 'pendente',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (template_id) REFERENCES templates(id),
            FOREIGN KEY (segmento_id) REFERENCES segmentos(id)
        )
    """)
    
    # Criar tabela de envios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS envios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            campanha_id INT NOT NULL,
            email_id INT NOT NULL,
            status VARCHAR(50) DEFAULT 'pendente',
            data_envio DATETIME,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (campanha_id) REFERENCES campanhas(id),
            FOREIGN KEY (email_id) REFERENCES emails(id)
        )
    """)
    
    # Criar tabela de métricas de envio
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
    
    # Criar tabela de eventos de tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eventos_tracking (
            id INT AUTO_INCREMENT PRIMARY KEY,
            envio_id INT NOT NULL,
            tipo_evento VARCHAR(50) NOT NULL,
            dados_adicionais JSON,
            data_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (envio_id) REFERENCES envios(id)
        )
    """)
    
    # Criar tabela de interações
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interacoes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            envio_id INT NOT NULL,
            email_id INT NOT NULL,
            tipo VARCHAR(50) NOT NULL,
            detalhes JSON,
            data_interacao DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (envio_id) REFERENCES envios(id),
            FOREIGN KEY (email_id) REFERENCES emails(id)
        )
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Banco de dados inicializado com sucesso!") 
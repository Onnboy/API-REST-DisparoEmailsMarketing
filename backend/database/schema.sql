-- Criar banco de dados
CREATE DATABASE IF NOT EXISTS base_emails_marketing;
USE base_emails_marketing;

-- Tabela de contatos
CREATE TABLE IF NOT EXISTS contatos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    nome VARCHAR(255),
    status ENUM('ativo', 'inativo', 'cancelado') DEFAULT 'ativo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabela de templates
CREATE TABLE IF NOT EXISTS templates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    html_content TEXT NOT NULL,
    css_content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabela de segmentos
CREATE TABLE IF NOT EXISTS segmentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    criterios JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabela de contatos por segmento
CREATE TABLE IF NOT EXISTS contatos_segmentos (
    contato_id INT NOT NULL,
    segmento_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (contato_id, segmento_id),
    FOREIGN KEY (contato_id) REFERENCES contatos(id) ON DELETE CASCADE,
    FOREIGN KEY (segmento_id) REFERENCES segmentos(id) ON DELETE CASCADE
);

-- Tabela de campanhas
CREATE TABLE IF NOT EXISTS campanhas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    descricao TEXT,
    template_id INT NOT NULL,
    segmento_id INT,
    status ENUM('rascunho', 'agendada', 'em_andamento', 'concluida', 'erro') DEFAULT 'rascunho',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE CASCADE,
    FOREIGN KEY (segmento_id) REFERENCES segmentos(id) ON DELETE SET NULL
);

-- Tabela de agendamentos
CREATE TABLE IF NOT EXISTS agendamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    template_id INT NOT NULL,
    segmento_id INT NOT NULL,
    assunto VARCHAR(255) NOT NULL,
    data_envio DATETIME NOT NULL,
    dados_padrao JSON,
    status ENUM('agendado', 'enviado', 'erro') DEFAULT 'agendado',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE CASCADE,
    FOREIGN KEY (segmento_id) REFERENCES segmentos(id) ON DELETE CASCADE
);

-- Tabela de integrações
CREATE TABLE IF NOT EXISTS integracoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo ENUM('smtp', 'webhook') NOT NULL,
    configuracao JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabela de logs de envio
CREATE TABLE IF NOT EXISTS logs_envio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    agendamento_id INT NOT NULL,
    contato_id INT NOT NULL,
    status ENUM('sucesso', 'erro') NOT NULL,
    mensagem TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agendamento_id) REFERENCES agendamentos(id) ON DELETE CASCADE,
    FOREIGN KEY (contato_id) REFERENCES contatos(id) ON DELETE CASCADE
); 
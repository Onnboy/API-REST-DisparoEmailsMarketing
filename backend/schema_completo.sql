-- Tabela de integrações
CREATE TABLE IF NOT EXISTS integracoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo ENUM('smtp', 'sendinblue') NOT NULL,
    configuracao JSON NOT NULL,
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

-- Tabela de contatos
CREATE TABLE IF NOT EXISTS contatos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    nome VARCHAR(255) NOT NULL,
    cargo VARCHAR(255),
    empresa VARCHAR(255),
    telefone VARCHAR(50),
    grupo VARCHAR(100),
    tags JSON,
    status ENUM('ativo', 'inativo') DEFAULT 'ativo',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabela de segmentos
CREATE TABLE IF NOT EXISTS segmentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    criterios JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabela de agendamentos
CREATE TABLE IF NOT EXISTS agendamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    template_id INT NOT NULL,
    segmento_id INT NOT NULL,
    assunto VARCHAR(255) NOT NULL,
    data_envio DATETIME NOT NULL,
    dados_padrao JSON,
    status ENUM('agendado', 'processando', 'concluido', 'erro') DEFAULT 'agendado',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (template_id) REFERENCES templates(id),
    FOREIGN KEY (segmento_id) REFERENCES segmentos(id)
);

-- Tabela de envios
CREATE TABLE IF NOT EXISTS envios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    contato_id INT NOT NULL,
    template_id INT NOT NULL,
    segmento_id INT NOT NULL,
    agendamento_id INT NOT NULL,
    status ENUM('enviado', 'erro') NOT NULL,
    erro TEXT,
    data_envio DATETIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contato_id) REFERENCES contatos(id),
    FOREIGN KEY (template_id) REFERENCES templates(id),
    FOREIGN KEY (segmento_id) REFERENCES segmentos(id),
    FOREIGN KEY (agendamento_id) REFERENCES agendamentos(id)
);

-- Tabela de eventos de tracking
CREATE TABLE IF NOT EXISTS eventos_tracking (
    id INT AUTO_INCREMENT PRIMARY KEY,
    envio_id INT NOT NULL,
    tipo_evento ENUM('abertura', 'clique') NOT NULL,
    dados_adicionais JSON,
    data_evento DATETIME NOT NULL,
    FOREIGN KEY (envio_id) REFERENCES envios(id)
);

-- Índices para melhor performance
CREATE INDEX idx_eventos_envio ON eventos_tracking(envio_id);
CREATE INDEX idx_eventos_tipo ON eventos_tracking(tipo_evento);
CREATE INDEX idx_eventos_data ON eventos_tracking(data_evento);
CREATE INDEX idx_contatos_email ON contatos(email);
CREATE INDEX idx_contatos_status ON contatos(status);
CREATE INDEX idx_agendamentos_status ON agendamentos(status);
CREATE INDEX idx_agendamentos_data ON agendamentos(data_envio);
CREATE INDEX idx_envios_status ON envios(status);
CREATE INDEX idx_envios_data ON envios(data_envio); 
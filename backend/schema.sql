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
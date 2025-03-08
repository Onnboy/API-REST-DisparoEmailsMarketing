CREATE DATABASE base_emails_marketing;
USE base_emails_marketing;

CREATE TABLE emails (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    nome VARCHAR(100) NOT NULL,
    data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
#SET foreign_key_checks = 1;
#DROP TABLE emails;

CREATE TABLE campanhas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    mensagem TEXT NOT NULL,
    data_envio DATETIME NOT NULL,
    status ENUM('pendente', 'enviado', 'cancelado') DEFAULT 'pendente'
);
#SET foreign_key_checks = 1;
#DROP TABLE campanhas;

CREATE TABLE envios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email_id INT,
    campanha_id INT,
    data_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('sucesso', 'falha') DEFAULT 'sucesso',
    FOREIGN KEY (email_id) REFERENCES emails(id) ON DELETE CASCADE,
    FOREIGN KEY (campanha_id) REFERENCES campanhas(id) ON DELETE CASCADE
);
#SET foreign_key_checks = 1;
#DROP TABLE envios;


CREATE TABLE interacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    envio_id INT,
    tipo ENUM('abertura', 'clique', 'resposta'),
    data_interacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (envio_id) REFERENCES envios(id) ON DELETE CASCADE
);
#SET foreign_key_checks = 1;
#DROP TABLE interacoes;

#INSERT INTO emails (email, nome)
#VALUES ('teste@gmail.com', 'Usuario Ghost');

#INSERT INTO campanhas (titulo, mensagem, data_envio, status, frequencia)
#VALUES ('Promoção Relampago', 'Desconto de 50% para você!', '2025-02-22 17:31:30', 'pendente', 'único');

#ALTER TABLE emails AUTO_INCREMENT = 1;
#ALTER TABLE campanhas AUTO_INCREMENT = 1;

#ALTER TABLE campanhas ADD COLUMN email VARCHAR(255) NOT NULL;
#ALTER TABLE envios MODIFY COLUMN status ENUM('sucesso', 'falha', 'pendente') DEFAULT 'pendente';
#SELECT * FROM emails WHERE id = 1;
#INSERT INTO emails (id, email, nome, data_cadastro, categoria) 
#VALUES (1, 'teste@email.com', 'Teste', NOW(), 'Marketing');



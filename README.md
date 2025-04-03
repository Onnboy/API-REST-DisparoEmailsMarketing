# Sistema de Marketing por Email

Sistema para gerenciamento de campanhas de email marketing, desenvolvido com Flask e MySQL.

## Funcionalidades

- Gerenciamento de contatos
- Criação e gerenciamento de templates de email
- Criação e gerenciamento de segmentos de contatos
- Criação e gerenciamento de campanhas
- Agendamento de envios de email
- Monitoramento de status dos serviços

## Requisitos

- Python 3.8+
- MySQL 8.0+
- pip (gerenciador de pacotes Python)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/sistema-email-marketing.git
cd sistema-email-marketing
```

2. Crie um ambiente virtual e ative-o:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure o banco de dados:
```bash
mysql -u root -p < backend/database/schema.sql
```

5. Configure as variáveis de ambiente:
Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=sua_senha
DB_NAME=base_emails_marketing
```

## Executando o Projeto

1. Ative o ambiente virtual (se ainda não estiver ativo):
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Inicie o servidor Flask:
```bash
flask run
```

O servidor estará disponível em `http://localhost:5000`

## Documentação da API

A documentação da API está disponível em `http://localhost:5000/docs` quando o servidor estiver em execução.

## Estrutura do Projeto

```
sistema-email-marketing/
├── backend/
│   ├── __init__.py
│   ├── config.py
│   ├── database/
│   │   └── schema.sql
│   └── routes/
│       ├── agendamentos.py
│       ├── campanhas.py
│       ├── emails.py
│       ├── segmentos.py
│       ├── status.py
│       └── templates.py
├── requirements.txt
└── README.md
```

## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes. 
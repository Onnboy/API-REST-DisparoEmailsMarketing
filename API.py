from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import mysql.connector

app = Flask(__name__)

def conectar_bd():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="71208794",
        database="base_email_marketing"
    )

@app.route('/')
def home():
    return jsonify({"mensagem": "API funcionando! Use as rotas disponíveis."})

@app.route('/enviar_email', methods=['POST'])
def enviar_email():
    dados = request.json
    destinatarios = dados.get('destinatarios')  # Lista de emails
    assunto = dados.get('assunto')
    mensagem = dados.get('mensagem')

    try:
        # Configurações do servidor SMTP (Gmail)
        remetente = "seu_email@gmail.com"
        senha = "sua_senha"

        for destinatario in destinatarios:
            # Criação do email
            msg = MIMEMultipart()
            msg['From'] = remetente
            msg['To'] = destinatario
            msg['Subject'] = assunto
            msg.attach(MIMEText(mensagem, 'plain'))

            # Envio de email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(remetente, senha)
            server.sendmail(remetente, destinatario, msg.as_string())
            server.quit()

        return jsonify({"mensagem": "Emails enviados com sucesso!"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    

# Adicionar email (evita duplicados)
@app.route('/adicionar_email', methods=['POST'])
def adicionar_email():
    dados = request.json
    nome = dados.get("nome")
    sobrenome = dados.get("sobrenome")
    email = dados.get("email")

    db = conectar_bd()
    cursor = db.cursor()

    try:
        # Verifica se o email já existe
        cursor.execute("SELECT id FROM clientes WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"erro": "Email já cadastrado."}), 400
        
        cursor.execute("INSERT INTO clientes (nome, sobrenome, email) VALUES (%s, %s, %s)", 
                       (nome, sobrenome, email))
        db.commit()
        return jsonify({"mensagem": "Email adicionado com sucesso!"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 400
    finally:
        cursor.close()
        db.close()

# Listar emails
@app.route('/listar_emails', methods=['GET'])
def listar_emails():
    db = conectar_bd()
    cursor = db.cursor()
    cursor.execute("SELECT id, nome, sobrenome, email FROM clientes")
    emails = cursor.fetchall()
    cursor.close()
    db.close()

    return jsonify([{"id": e[0], "nome": e[1], "sobrenome": e[2], "email": e[3]} for e in emails])

# Atualizar email
@app.route('/atualizar_email/<int:id>', methods=['PUT'])
def atualizar_email(id):
    dados = request.json
    nome = dados.get("nome")
    sobrenome = dados.get("sobrenome")
    email = dados.get("email")

    db = conectar_bd()
    cursor = db.cursor()

    try:
        cursor.execute("UPDATE clientes SET nome = %s, sobrenome = %s, email = %s WHERE id = %s", 
                       (nome, sobrenome, email, id))
        db.commit()
        return jsonify({"mensagem": "Email atualizado com sucesso!"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 400
    finally:
        cursor.close()
        db.close()

# Remover email
@app.route('/remover_email/<int:id>', methods=['DELETE'])
def remover_email(id):
    db = conectar_bd()
    cursor = db.cursor()

    try:
        cursor.execute("DELETE FROM clientes WHERE id = %s", (id,))
        db.commit()
        return jsonify({"mensagem": "Email removido com sucesso!"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 400
    finally:
        cursor.close()
        db.close()

if __name__ == '__main__':
    app.run(debug=True)

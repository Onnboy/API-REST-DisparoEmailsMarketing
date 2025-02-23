from flask import Blueprint, request, jsonify
from backend.config import get_db_connection

blueprint = Blueprint('api', __name__)

# Rota para listar todos os emails cadastrados
@blueprint.route('/emails', methods=['GET'])
def get_emails():
    with get_db_connection() as connection:
        with connection.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT * FROM emails;")
            emails = cursor.fetchall()
    return jsonify(emails)


# Rota para adicionar um novo email
@blueprint.route('/emails', methods=['POST'])
def add_email():
    data = request.get_json()
    email = data.get('email')
    nome = data.get('nome')

    if not email or not nome:
        return jsonify({'error': 'Email e Nome são obrigatórios'}), 400

    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO emails (email, nome) VALUES (%s, %s)", (email, nome))
                connection.commit()
        return jsonify({'message': 'Email cadastrado com sucesso!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# Rota para remover um email pelo ID
@blueprint.route('/emails/<int:id>', methods=['DELETE'])
def delete_email(id):
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM emails WHERE id = %s", (id,))
                if cursor.rowcount == 0:
                    return jsonify({'error': 'Nenhum email encontrado com esse ID'}), 404
                connection.commit()
        return jsonify({'message': 'Email removido com sucesso!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Rota para listar todas as campanhas
@blueprint.route('/campanhas', methods=['GET'])
def get_campanhas():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM campanhas;")
    campanhas = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(campanhas)

# Rota para criar uma nova campanha
@blueprint.route('/campanhas', methods=['POST'])
def add_campanha():
    data = request.get_json()
    titulo = data.get('titulo')
    mensagem = data.get('mensagem')
    data_envio = data.get('data_envio')
    frequencia = data.get('frequencia', 'único')  # Padrão: campanha única

    if not titulo or not mensagem or not data_envio:
        return jsonify({'error': 'Título, mensagem e data de envio são obrigatórios'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO campanhas (titulo, mensagem, data_envio, frequencia) VALUES (%s, %s, %s, %s)",
            (titulo, mensagem, data_envio, frequencia)
        )
        connection.commit()
        return jsonify({'message': 'Campanha criada com sucesso!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# Rota para remover uma campanha pelo ID
@blueprint.route('/campanhas/<int:id>', methods=['DELETE'])
def delete_campanha(id):
    try:
        with get_db_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM campanhas WHERE id = %s", (id,))
                connection.commit()
        return jsonify({'message': 'Campanha removida com sucesso!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Rota para listar todos os envios de emails
@blueprint.route('/envios', methods=['GET'])
def get_envios():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT envios.id, emails.email, campanhas.titulo, envios.data_envio, envios.status
        FROM envios
        JOIN emails ON envios.email_id = emails.id
        JOIN campanhas ON envios.campanha_id = campanhas.id
    """)
    envios = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(envios)

# Rota para registrar um envio de email
@blueprint.route('/envios', methods=['POST'])
def add_envio():
    data = request.get_json()
    email_id = data.get('email_id')
    campanha_id = data.get('campanha_id')
    status = data.get('status', 'sucesso')  # Padrão: sucesso

    if not email_id or not campanha_id:
        return jsonify({'error': 'Email ID e Campanha ID são obrigatórios'}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            "INSERT INTO envios (email_id, campanha_id, status) VALUES (%s, %s, %s)",
            (email_id, campanha_id, status)
        )
        connection.commit()
        return jsonify({'message': 'Envio registrado com sucesso!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

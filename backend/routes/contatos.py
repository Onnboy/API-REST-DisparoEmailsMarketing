from flask import Blueprint, request, jsonify
from backend.config import get_db_connection
import json

contatos_bp = Blueprint('contatos', __name__)

@contatos_bp.route('/', methods=['GET'])
def listar_contatos():
    """Lista todos os contatos."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM contatos")
        contatos = cursor.fetchall()
        
        return jsonify(contatos)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@contatos_bp.route('/', methods=['POST'])
def criar_contato():
    """Cria um novo contato."""
    try:
        dados = request.get_json()
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = """
            INSERT INTO contatos (email, nome, cargo, empresa, telefone, grupo, tags)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            dados.get('email'),
            dados.get('nome'),
            dados.get('cargo'),
            dados.get('empresa'),
            dados.get('telefone'),
            dados.get('grupo'),
            json.dumps(dados.get('tags', []))
        ))
        
        connection.commit()
        contato_id = cursor.lastrowid
        
        return jsonify({
            "id": contato_id,
            "mensagem": "Contato criado com sucesso"
        }), 201
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@contatos_bp.route('/<int:contato_id>', methods=['GET'])
def obter_contato(contato_id):
    """Obtém um contato específico."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM contatos WHERE id = %s", (contato_id,))
        contato = cursor.fetchone()
        
        if not contato:
            return jsonify({"erro": "Contato não encontrado"}), 404
            
        return jsonify(contato)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@contatos_bp.route('/<int:contato_id>', methods=['PUT'])
def atualizar_contato(contato_id):
    """Atualiza um contato existente."""
    try:
        dados = request.get_json()
        
        connection = get_db_connection()
        cursor = connection.cursor()
        
        query = """
            UPDATE contatos 
            SET email = %s, nome = %s, cargo = %s, empresa = %s, 
                telefone = %s, grupo = %s, tags = %s
            WHERE id = %s
        """
        cursor.execute(query, (
            dados.get('email'),
            dados.get('nome'),
            dados.get('cargo'),
            dados.get('empresa'),
            dados.get('telefone'),
            dados.get('grupo'),
            json.dumps(dados.get('tags', [])),
            contato_id
        ))
        
        connection.commit()
        
        if cursor.rowcount == 0:
            return jsonify({"erro": "Contato não encontrado"}), 404
            
        return jsonify({"mensagem": "Contato atualizado com sucesso"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

@contatos_bp.route('/<int:contato_id>', methods=['DELETE'])
def remover_contato(contato_id):
    """Remove um contato."""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        
        cursor.execute("DELETE FROM contatos WHERE id = %s", (contato_id,))
        connection.commit()
        
        if cursor.rowcount == 0:
            return jsonify({"erro": "Contato não encontrado"}), 404
            
        return jsonify({"mensagem": "Contato removido com sucesso"})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close() 
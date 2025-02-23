from flask import Flask, jsonify
from flask_cors import CORS
from config import get_db_connection
from backend.routes import blueprint as routes

app = Flask(__name__)
CORS(app)

# Registrando as rotas no Flask
app.register_blueprint(routes)

# Rota de teste da conexão com MySQL
@app.route('/db-test', methods=['GET'])
def db_test():
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            db_name = cursor.fetchone()[0]
            cursor.close()
            connection.close()
            return jsonify({'message': f'Conectado ao banco de dados: {db_name}'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Falha na conexão com o banco de dados'}), 500

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask,  send_from_directory
from flasgger import Swagger
from backend.routes.routes import register_routes
import os


app = Flask(__name__)
Swagger(app)

register_routes(app)

@app.route('/')
def home():
    return "Bem-vindo à API de Disparo de E-mails!"

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask
from backend.routes.routes import register_routes

app = Flask(__name__)


# Registrando todas as rotas no app
register_routes(app)

if __name__ == '__main__':
    app.run(debug=True)

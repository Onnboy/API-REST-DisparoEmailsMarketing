from flask import Flask
from backend.routes.routes import register_routes
from backend.routes.send_test_email import sendtestemail_bp 

app = Flask(__name__)

app.register_blueprint(sendtestemail_bp)

# Registrando todas as rotas no app
register_routes(app)

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask
from backend.routes.emails import emails_bp
from backend.routes.campanhas import campanhas_bp
from backend.routes.envios import envios_bp
from backend.routes.send_test_email import sendtestemail_bp

def register_routes(app: Flask):
    app.register_blueprint(emails_bp)
    app.register_blueprint(campanhas_bp)
    app.register_blueprint(envios_bp)
    app.register_blueprint(sendtestemail_bp)
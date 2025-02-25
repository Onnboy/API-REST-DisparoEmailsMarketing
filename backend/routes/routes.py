from flask import Flask
from backend.routes.emails import emails_bp
from backend.routes.campanhas import campanhas_bp
from backend.routes.envios import envios_bp

def register_routes(app: Flask):
    app.register_blueprint(emails_bp)
    app.register_blueprint(campanhas_bp)
    app.register_blueprint(envios_bp)

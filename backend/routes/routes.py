from flask import Flask
from backend.routes.emails import emails_bp
from backend.routes.envios import envios_bp
from backend.routes.campanhas import campanhas_bp
from backend.routes.relatorios import relatorios_bp
from backend.routes.estatisticas import estatisticas_bp
from backend.routes.agendar_envio import agendar_envio_bp
from backend.routes.enviar_email_simples import sendemail_simple_bp
from backend.routes.exportar_arq import exportar_bp
from backend.routes.enviar_email_template import sendemail_template_bp
from backend.routes.templates import templates_bp
from flask import Blueprint

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def home():
    return "Bem-vindo à minha API de Disparo de E-mails!"

def register_routes(app: Flask):
    app.register_blueprint(emails_bp)
    app.register_blueprint(envios_bp)
    app.register_blueprint(campanhas_bp)
    app.register_blueprint(sendemail_simple_bp)
    app.register_blueprint(estatisticas_bp)
    app.register_blueprint(relatorios_bp)
    app.register_blueprint(agendar_envio_bp)
    app.register_blueprint(exportar_bp)
    app.register_blueprint(sendemail_template_bp)
    app.register_blueprint(templates_bp)
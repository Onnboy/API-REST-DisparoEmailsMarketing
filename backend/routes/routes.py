from flask import Flask
from backend.routes.emails import emails_bp
from backend.routes.envios import envios_bp
from backend.routes.campanhas import campanhas_bp
from backend.routes.relatorios import relatorios_bp
from backend.routes.estatisticas import estatisticas_bp
from backend.routes.agendar_envio import agendar_envio_bp
from backend.routes.send_test_email import sendtestemail_bp
from backend.routes.exportar_arq import exportar_bp
from backend.routes.send_email import sendemail_bp

def register_routes(app: Flask):
    app.register_blueprint(emails_bp)
    app.register_blueprint(envios_bp)
    app.register_blueprint(campanhas_bp)
    app.register_blueprint(sendtestemail_bp)
    app.register_blueprint(estatisticas_bp)
    app.register_blueprint(relatorios_bp)
    app.register_blueprint(agendar_envio_bp)
    app.register_blueprint(exportar_bp)
    app.register_blueprint(sendemail_bp)

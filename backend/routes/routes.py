from flask import Flask, Blueprint
from backend.routes.integracoes import integracoes_bp
from backend.routes.emails import emails_bp
from backend.routes.templates import templates_bp
from backend.routes.contatos import contatos_bp
from backend.routes.segmentos import segmentos_bp
from backend.routes.agendamentos import agendamentos_bp
from backend.routes.metricas import metricas_bp
from backend.routes.tracking import tracking_bp
from backend.routes.exportar_arq import exportar_bp
from backend.routes.campanhas import campanhas_bp
from backend.routes.envios import envios_bp
import logging
import sys

# Configurar logging para mostrar no console
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

logger.debug("Módulo routes.py sendo carregado...")

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def home():
    logger.debug("Rota raiz acessada!")
    return "Bem-vindo à minha API de Disparo de E-mails!"

def register_routes(app: Flask):
    logger.debug("Iniciando registro de rotas...")
    
    # Registrar primeiro os blueprints de funcionalidades básicas
    app.register_blueprint(main_bp)
    logger.debug("main_bp registrado")
    
    # Registrar blueprint de integrações
    app.register_blueprint(integracoes_bp, url_prefix='/api/integracoes')
    logger.debug("integracoes_bp registrado")
    
    # Registrar blueprint de emails
    app.register_blueprint(emails_bp, url_prefix='/api/emails')
    logger.debug("emails_bp registrado")
    
    # Registrar blueprint de templates
    app.register_blueprint(templates_bp, url_prefix='/api/templates')
    logger.debug("templates_bp registrado")
    
    # Registrar blueprint de contatos
    app.register_blueprint(contatos_bp, url_prefix='/api/contatos')
    logger.debug("contatos_bp registrado")
    
    # Registrar blueprint de segmentos
    app.register_blueprint(segmentos_bp, url_prefix='/api/segmentos')
    logger.debug("segmentos_bp registrado")
    
    # Registrar blueprint de agendamentos
    app.register_blueprint(agendamentos_bp, url_prefix='/api/agendamentos')
    logger.debug("agendamentos_bp registrado")
    
    # Registrar blueprint de métricas
    app.register_blueprint(metricas_bp, url_prefix='/api/metricas')
    logger.debug("metricas_bp registrado")
    
    # Registrar blueprint de tracking
    app.register_blueprint(tracking_bp, url_prefix='/api/tracking')
    logger.debug("tracking_bp registrado")
    
    # Registrar blueprint de exportação
    app.register_blueprint(exportar_bp, url_prefix='/api/relatorios')
    logger.debug("exportar_bp registrado")
    
    # Registrar blueprint de campanhas
    app.register_blueprint(campanhas_bp, url_prefix='/api/campanhas')
    logger.debug("campanhas_bp registrado")
    
    # Registrar blueprint de envios
    app.register_blueprint(envios_bp, url_prefix='/api/envios')
    logger.debug("envios_bp registrado")
    
    # Listar todas as rotas registradas
    logger.debug("Rotas registradas:")
    for rule in app.url_map.iter_rules():
        logger.debug(f"{rule.endpoint}: {rule.methods} {rule}")
    
    return app
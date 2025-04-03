from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
from backend.routes.routes import register_routes
from .database import init_db

def create_app():
    """Cria e configura a aplicação Flask."""
    app = Flask(__name__, static_folder='static')
    
    # Configurar CORS
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Configurar Swagger
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": 'apispec',
                "route": '/apispec.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/docs"
    }
    
    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "API de Email Marketing",
            "description": "API para sistema de disparo de emails marketing",
            "contact": {
                "responsibleOrganization": "Level Marketing",
                "responsibleDeveloper": "Equipe de Desenvolvimento",
            },
            "version": "1.0"
        },
        "schemes": ["http", "https"],
        "operationId": "getmyData"
    }
    
    Swagger(app, config=swagger_config, template=swagger_template)
    
    # Inicializar o banco de dados
    init_db()
    
    # Registrar as rotas
    register_routes(app)
    
    return app

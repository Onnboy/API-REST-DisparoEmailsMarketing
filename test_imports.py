from backend import create_app
from backend.routes.status import status_bp
from backend.routes.emails import emails_bp
from backend.routes.templates import templates_bp
from backend.routes.campanhas import campanhas_bp
from backend.routes.segmentos import segmentos_bp
from backend.routes.agendamentos import agendamentos_bp

print("Todos os módulos foram importados com sucesso!")

app = create_app()
print("\nBlueprints registrados:")
for rule in app.url_map.iter_rules():
    print(f"{rule.endpoint}: {rule.rule}") 
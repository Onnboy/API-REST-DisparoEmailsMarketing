from celery import Celery
from backend.config import Config

celery_app = Celery('backend',
                    broker=Config.REDIS_URL,
                    backend=Config.REDIS_URL)

# Configurações do Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Sao_Paulo',
    enable_utc=True,
)

# Importa as tasks
celery_app.autodiscover_tasks(['backend.tasks']) 
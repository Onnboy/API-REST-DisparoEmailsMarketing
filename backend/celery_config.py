from celery import Celery
from backend.config import Config

# Configuração do Celery
celery_app = Celery('email_marketing',
                    broker='redis://localhost:6379/0',
                    backend='redis://localhost:6379/0')

# Configurações do Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Sao_Paulo',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hora
    worker_max_tasks_per_child=100,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=300,  # 5 minutos
    task_max_retries=3
) 
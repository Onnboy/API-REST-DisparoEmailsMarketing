import hmac
import hashlib
import os
from backend.config import Config
import json
import base64
import time

def gerar_token_tracking(envio_id, tipo_evento, dados_adicionais=None):
    """Gera um token seguro para tracking de eventos."""
    dados = {
        'envio_id': envio_id,
        'tipo_evento': tipo_evento,
        'dados_adicionais': dados_adicionais,
        'timestamp': str(int(time.time()))
    }
    
    # Ordenar dados para garantir consistência
    dados_ordenados = json.dumps(dados, sort_keys=True)
    
    # Gerar assinatura
    assinatura = hmac.new(
        Config.WEBHOOK_SECRET.encode(),
        dados_ordenados.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Adicionar assinatura aos dados
    dados['assinatura'] = assinatura
    
    # Codificar em base64
    return base64.b64encode(json.dumps(dados).encode()).decode() 
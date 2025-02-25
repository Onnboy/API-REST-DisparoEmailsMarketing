from flask import Blueprint, jsonify
from backend.services.email_service import send_email

sendtestemail_bp = Blueprint('sendtestemail', __name__)

@sendtestemail_bp.route("/send-test-email", methods=["GET"])
def send_test_email():
    """Envia um e-mail de teste."""
    response = send_email("destinatario@email.com", "Teste", "<h1>Este é um e-mail de teste com SendGrid!</h1>")
    
    if response == 202:
        return jsonify({"message": "E-mail enviado com sucesso!"}), 200
    else:
        print(f"Erro ao enviar e-mail: Código {response}") # Plano B se necessario for
        return jsonify({"error": "Falha ao enviar e-mail"}), 500

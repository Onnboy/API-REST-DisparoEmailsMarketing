from flask import Blueprint, request, jsonify
from backend.services.email_service import send_email

sendtestemail_bd = Blueprint('sendtestemail', __name__)

@sendtestemail_bd.route("/send-test-email", methods=["GET"])
def send_test_email():
    """Envia um e-mail de teste."""
    response = send_email("destinatario@email.com", "Teste", "<h1>Este é um e-mail de teste com SendGrid!</h1>")
    
    if response == 202:
        return jsonify({"message": "E-mail enviado com sucesso!"}), 200
    else:
        return jsonify({"error": "Falha ao enviar e-mail"}), 500
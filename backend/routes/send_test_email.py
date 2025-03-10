from flask import Blueprint, jsonify, request
from flasgger import swag_from
from backend.services.email_service import send_email

sendtestemail_bp = Blueprint('sendtestemail', __name__)

@sendtestemail_bp.route("/send-test-email", methods=["GET", "POST"])
def send_test_email():
    """Envia um e-mail de teste."""
    if request.method == "POST":
        dados = request.json
        destinatario = dados.get("email", "bomfimsantarosa@gmail.com")  
    else:
        destinatario = "bomfimsantarosa@gmail.com"

    sucesso = send_email(destinatario, "Teste", "<h1>Este é um e-mail de teste!</h1>")
    
    if sucesso:
        return jsonify({"message": f"E-mail enviado com sucesso para {destinatario}!"}), 200
    return jsonify({"error": "Falha ao enviar e-mail"}), 500
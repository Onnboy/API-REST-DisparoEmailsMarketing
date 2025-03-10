from flask import Blueprint, jsonify, request
from backend.services.email_service import send_email

sendemail_bp = Blueprint('sendemail', __name__)

@sendemail_bp.route('/send-email-template', methods=['POST'])
def enviar_email_template():
    """
    Envia e-mail com template e opcionalmente anexo.
    """
    dados = request.json
    destinatario = dados.get("email")
    assunto = dados.get("subject", "Assunto padrão")
    conteudo = dados.get("content", "<h1>Conteúdo padrão</h1>")
    attachments = dados.get("attachments", [])  # Lista de caminhos

    if not destinatario:
        return jsonify({"error": "E-mail do destinatário é obrigatório."}), 400

    sucesso = send_email(destinatario, assunto, conteudo, attachments)

    if sucesso:
        return jsonify({"message": f"E-mail enviado com sucesso para {destinatario}!"}), 200
    else:
        return jsonify({"error": "Falha ao enviar o e-mail."}), 500

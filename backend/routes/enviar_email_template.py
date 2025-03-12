from flask import Blueprint, jsonify, request
from backend.services.email_service import send_email
from flasgger import swag_from

sendemail_template_bp = Blueprint('sendemail_template', __name__)

@sendemail_template_bp.route("/send-email-template", methods=["GET", "POST"])
@swag_from({
    "tags": ["Envio de E-mails"],
    "summary": "Enviar e-mail simples",
    "description": "Envia um e-mail simples, sem template, apenas para teste ou comunicação básica.",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": False,
            "schema": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "example": "teste@exemplo.com"
                    }
                }
            },
            "description": "Opcional: E-mail do destinatário. Se não informado, será enviado para o padrão cadastrado."
        }
    ],
    "responses": {
        200: {
            "description": "E-mail enviado com sucesso",
            "schema": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "example": "E-mail enviado com sucesso para teste@exemplo.com!"
                    }
                }
            }
        },
        500: {
            "description": "Falha ao enviar o e-mail",
            "schema": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "example": "Falha ao enviar e-mail"
                    }
                }
            }
        }
    }
})
def enviar_email_template():
    """
    Envia e-mail com template e opcionalmente anexo.
    """
    dados = request.json
    destinatario = dados.get("email")
    assunto = dados.get("subject", "Assunto padrão")
    conteudo = dados.get("content", "<h1>Conteúdo padrão</h1>")
    attachments = dados.get("attachments", [])

    if not destinatario:
        return jsonify({"error": "E-mail do destinatário é obrigatório."}), 400

    sucesso = send_email(destinatario, assunto, conteudo, attachments)

    if sucesso:
        return jsonify({"message": f"E-mail enviado com sucesso para {destinatario}!"}), 200
    else:
        return jsonify({"error": "Falha ao enviar o e-mail."}), 500

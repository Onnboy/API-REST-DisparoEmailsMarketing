from flask import Blueprint, jsonify, request
from flasgger import swag_from
from backend.services.email_service import send_email

sendemail_simple_bp = Blueprint('sendemail_simple', __name__)

@sendemail_simple_bp.route("/send-email", methods=["POST"])
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
def enviar_email_simples():
    """
    Envia um e-mail simples para o destinatário informado.
    ---
    """
    if request.method == "POST":
        dados = request.json
        destinatario = dados.get("email", "bomfimsantarosa@gmail.com")  
    else:
        destinatario = "bomfimsantarosa@gmail.com"

    sucesso = send_email(destinatario, "Teste", "<h1>Email Informativo</h1>")
    
    if sucesso:
        return jsonify({"message": f"E-mail enviado com sucesso para {destinatario}!"}), 200
    return jsonify({"error": "Falha ao enviar e-mail"}), 500
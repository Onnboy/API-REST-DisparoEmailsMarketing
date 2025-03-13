from flask import Blueprint, jsonify, request
from backend.services.email_service import send_email
from backend.config import get_db_connection
from flasgger import swag_from

sendemail_template_bp = Blueprint('sendemail_template', __name__)

@sendemail_template_bp.route("/send-email-template", methods=["POST"])
@swag_from({
    "tags": ["Envio de E-mails"],
    "summary": "Enviar e-mail com template e anexo",
    "description": "Envia um e-mail com template, anexo e atualiza o status para 'enviado'.",
    "parameters": [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "example": "teste@exemplo.com"},
                    "subject": {"type": "string", "example": "Promoção Especial"},
                    "content": {"type": "string", "example": "<h1>Olá {{ nome }}</h1>"},
                    "attachments": {
                        "type": "array",
                        "items": {"type": "object"},
                        "example": [{"name": "arquivo.pdf", "path": "caminho/arquivo.pdf"}]
                    },
                    "campanha_id": {"type": "integer", "example": 1},
                    "email_id": {"type": "integer", "example": 10}
                },
                "required": ["email", "campanha_id", "email_id"]
            }
        }
    ],
    "responses": {
        200: {"description": "E-mail enviado e status atualizado com sucesso."},
        400: {"description": "Dados inválidos."},
        500: {"description": "Falha no envio ou na atualização do status."}
    }
})
def enviar_email_template():
    """
    Envia e-mail com template e opcionalmente anexo.
    Atualiza automaticamente o status do envio para 'enviado' se o envio for bem-sucedido.
    """
    dados = request.json
    destinatario = dados.get("email")
    assunto = dados.get("subject", "Assunto padrão")
    conteudo = dados.get("content", "<h1>Conteúdo padrão</h1>")
    attachments = dados.get("attachments", [])
    campanha_id = dados.get("campanha_id")
    email_id = dados.get("email_id")

    if not destinatario or not campanha_id or not email_id:
        return jsonify({"error": "Campos 'email', 'campanha_id' e 'email_id' são obrigatórios."}), 400

    sucesso = send_email(destinatario, assunto, conteudo, attachments)

    if sucesso:
        try:
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute("""
                UPDATE envios 
                SET status = 'enviado', data_envio = NOW()
                WHERE campanha_id = %s AND email_id = %s
            """, (campanha_id, email_id))
            connection.commit()
            cursor.close()
            connection.close()

            return jsonify({"message": f"E-mail enviado com sucesso para {destinatario}, status atualizado para 'enviado'!"}), 200

        except Exception as e:
            return jsonify({"error": f"E-mail enviado, mas erro ao atualizar status: {str(e)}"}), 500

    else:
        return jsonify({"error": "Falha ao enviar o e-mail."}), 500

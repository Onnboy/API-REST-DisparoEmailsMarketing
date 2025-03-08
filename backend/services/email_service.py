import os
import sib_api_v3_sdk
from backend.config import get_db_connection
from sib_api_v3_sdk.rest import ApiException
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SENDINBLUE_API_KEY")
DEFAULT_SENDER = os.getenv("SENDINBLUE_DEFAULT_SENDER")

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = API_KEY

api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

def send_email(to_email, subject, content, campanha_id=None):
    sender = {"name": "Meu Nome", "email": DEFAULT_SENDER}
    recipient = [{"email": to_email}]

    email = sib_api_v3_sdk.SendSmtpEmail(
        sender=sender,
        to=recipient,
        subject=subject,
        html_content=content
    )

    try:
        sucesso = api_instance.send_transac_email(email)
        if sucesso and campanha_id is not None:
            atualizar_taxa_entrega(campanha_id)
        return True  
    except ApiException as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False 

def atualizar_taxa_entrega(campanha_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE campanhas 
        SET taxa_entrega = taxa_entrega + 1
        WHERE id = %s
    """, (campanha_id,))

    connection.commit()
    cursor.close()
    connection.close()
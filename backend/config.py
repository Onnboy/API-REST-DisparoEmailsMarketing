import mysql.connector
import os
from dotenv import load_dotenv

import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="71208794",
        database="base_emails_marketing"
    )

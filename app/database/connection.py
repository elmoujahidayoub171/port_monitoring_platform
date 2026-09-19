import psycopg2
from dotenv import load_dotenv
import os
load_dotenv()
def get_connection():
    conn = psycopg2.connect(dbname=os.getenv("DB_NAME"),
                                             user=os.getenv("DB_USER"),
                                             password=os.getenv("DB_PASSWORD"),
                                             host=os.getenv("HOSTNAME"),
                                             port=os.getenv("DB_PORT")
                                             )
    return conn

    



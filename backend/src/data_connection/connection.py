import psycopg2
from src.logger import logging
from src.exception import MyException
import sys
import string 
# global connection object

conn = None

def connect_db()->psycopg2.extensions.connection:
    global conn
    
    if conn is not None and conn.closed == 0:
        print("Database already connected.")
        return conn
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="DBMS_proj",
            user="postgres",
            password="Debtanu@7861",
            port="5432"
        )
        print("Database connection established successfully.")
        return conn
    
    except Exception as e:
        raise MyException(e, sys)
    
    
def disconnect_db()->psycopg2.extensions.connection:
    global conn
    if conn is None or conn.closed != 0:
        return None
    
    try:
        conn.close()
        print("Database connection closed successfully.")
        return None

    except Exception as e:
        raise MyException(e, sys)
    


# connect_db()
# disconnect_db()
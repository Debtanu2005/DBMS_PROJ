import mysql.connector
from src.logger import logging
from src.exception import MyException
import sys

conn = None

def connect_db():
    global conn

    if conn is not None and conn.is_connected():
        print("Database already connected.")
        return conn

    try:
        conn = mysql.connector.connect(
            host="localhost",
            database="gyanpustak",
            user="vr_1",
            password="123456",
            port=3306
        )
        print("Database connection established successfully.")
        return conn

    except Exception as e:
        raise MyException(e, sys)


def disconnect_db():
    global conn

    if conn is None or not conn.is_connected():
        return None

    try:
        conn.close()
        print("Database connection closed successfully.")
        return None

    except Exception as e:
        raise MyException(e, sys)
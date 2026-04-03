import jwt
import datetime
import os
from dotenv import load_dotenv
from src.logger import logging
from src.exception import MyException

load_dotenv()  # Load environment variables from .env file

SECRET_KEY = os.getenv("secret_key")  # Default value for development
# print(f"Using SECRET_KEY: {SECRET_KEY}")  

# Algorithm used for encoding/decoding
ALGORITHM = "HS256"

# Token expiry time (in minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict)->str:
    """
    Create JWT token
    :param data: dictionary (e.g. {"user_id": 1, "role": "admin"})
    :return: encoded JWT token
    """
    to_encode = data.copy()

    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return token


def verify_token(token: str)->dict | None:
    """
    Verify JWT token
    :param token: JWT token string
    :return: decoded payload or None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload

    except jwt.ExpiredSignatureError:
        logging.warning("Token expired")
        print("Token expired")
        return None

    except jwt.InvalidTokenError:
        logging.error("Invalid token")
        print("Invalid token")
        return None


def decode_token(token: str)->dict | None:
    """
    Decode token without validation (optional use)
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception as e:
        logging.error(f"Error decoding token: {e}")
        print("Error decoding token:", e)
        return None
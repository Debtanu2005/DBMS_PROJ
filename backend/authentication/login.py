from authentication.jwt import create_access_token
from authentication.hashing import verify_password
from src.data_connection.connection import connect_db, disconnect_db
from src.logger import logging
from src.exception import MyException


class LoginManager:
    def __init__(self):
        self.conn = connect_db()
        self.cursor = self.conn.cursor()

    def login(self, email: str, password: str) -> str:
        try:
            self.cursor.execute("""
                SELECT user_id, email, password, role
                FROM users
                WHERE email = %s
            """, (email,))

            user_data = self.cursor.fetchone()

            if not user_data:
                logging.warning(f"Login failed for email: {email}")
                raise Exception("Invalid email or password")

            user_id, email, hashed_password, role = user_data

            # ✅ Step 2: Verify password
            if not verify_password(password, hashed_password):
                logging.warning(f"Invalid password for email: {email}")
                raise MyException("Invalid email or password")

            # ✅ Step 3: Create JWT token
            token_data = {
                "user_id": user_id,
                "email": email,
                "role": role
            }

            access_token = create_access_token(token_data)

            logging.info(f"User {email} logged in successfully")
            return access_token

        except Exception as e:
            logging.error(f"Login error: {str(e)}")
            raise e

    def __del__(self):
        try:
            disconnect_db() 
        except:
            logging.error("Error occurred while closing the database connection")
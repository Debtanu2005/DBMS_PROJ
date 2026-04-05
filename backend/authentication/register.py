from authentication.jwt import create_access_token
from src.data_connection.connection import connect_db, disconnect_db
from src.logger import logging
from src.artifacts.entities import student
from src.exception import MyException
from authentication.hashing import hash_password


class RegisterManager:
    def __init__(self):
        self.conn = connect_db()
        self.cursor = self.conn.cursor()

    def register(self, email: str, password: str, student_info: student) -> str:
        try:
            # Step 1: Check if user already exists
            self.cursor.execute("""
                SELECT user_id FROM users WHERE email = %s
            """, (email,))

            if self.cursor.fetchone():
                logging.warning(f"Registration failed for email: {email} - already exists")
                raise Exception("Email already registered")

            # Step 2: Hash password
            hashed_password = hash_password(password)

            # Step 3: Insert into users table   
            self.cursor.execute("""
                INSERT INTO users (email, password, role, created_at)
                VALUES (%s, %s, %s, NOW())
                RETURNING user_id
            """, (email, hashed_password, student_info.role))

            user_id = self.cursor.fetchone()[0]   # ✅ ONLY ONCE

            # Step 4: Insert into students table
            self.cursor.execute("""
                INSERT INTO students (
                    student_id, first_name, last_name, phone, dob,
                    university_id, major, status, year_of_student
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                student_info.first_name,
                student_info.last_name,
                student_info.phone,
                student_info.dob,
                student_info.university_id,
                student_info.major,
                student_info.status,
                student_info.year_of_student
            ))

            self.conn.commit()

            # Step 5: Create JWT token
            token_data = {
                "user_id": user_id,
                "email": email,
                "role": student_info.role
            }

            access_token = create_access_token(token_data)

            logging.info(f"User {email} registered successfully with user_id {user_id}")

            return access_token

        except Exception as e:
            self.conn.rollback()
            logging.error(f"Registration error: {str(e)}")
            raise e

    def __del__(self):
        try:
            self.cursor.close()
            disconnect_db(self.conn)   # FIXED
        except:
            pass
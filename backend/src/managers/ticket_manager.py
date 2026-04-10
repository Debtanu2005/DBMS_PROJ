from src.data_connection.connection import connect_db, disconnect_db
from src.logger import logging


class TicketManager:
    def __init__(self):
        self.conn = connect_db()
        self.cursor = self.conn.cursor()

    def create_ticket(self, user_id: int, category: str, title: str, description: str) -> dict:
        try:
            # Verify user is a student
            self.cursor.execute("""
                SELECT u.role, s.first_name, s.last_name, u.email
                FROM users u
                JOIN students s ON s.student_id = u.user_id
                WHERE u.user_id = %s
            """, (user_id,))

            user = self.cursor.fetchone()

            if not user:
                raise Exception("User not found or not a student")

            role, first_name, last_name, email = user

            if role != "student":
                raise Exception("Only students can create tickets")

            # Insert ticket
            self.cursor.execute("""
                INSERT INTO tickets (created_by, category, title, description, status, created_at)
                VALUES (%s, %s, %s, %s, 'new', NOW())
            """, (user_id, category, title, description))

            self.conn.commit()
            ticket_id = self.cursor.lastrowid

            logging.info(f"Ticket {ticket_id} created by user {user_id}")

            return {
                "ticket_id": ticket_id,
                "category": category,
                "title": title,
                "description": description,
                "status": "new",
                "created_by": {
                    "user_id": user_id,
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name
                }
            }

        except Exception as e:
            self.conn.rollback()
            logging.error(f"Ticket creation error: {str(e)}")
            raise e

    def __del__(self):
        try:
            self.cursor.close()
            disconnect_db()
        except:
            pass
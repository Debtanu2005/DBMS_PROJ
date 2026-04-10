from src.data_connection.connection import connect_db, disconnect_db
from src.logger import logging
from src.exception import MyException


class ViewOrders:
    def __init__(self):
        self.conn = connect_db()
        self.cursor = self.conn.cursor()

    # ================== VIEW ORDERS ==================
    def view_orders(self, user_id: int) -> list:
        try:
            self.cursor.execute(
                """
                SELECT 
                    o.order_id,
                    b.title,
                    b.isbn,
                    oi.quantity,
                    o.created_at
                FROM orders o
                JOIN order_items oi ON o.order_id = oi.order_id
                JOIN books b ON oi.book_id = b.book_id
                WHERE o.student_id = %s
                ORDER BY o.created_at DESC
                """,
                (user_id,)
            )

            return self.cursor.fetchall()

        except Exception as e:
            logging.error(f"Error viewing orders for user_id {user_id}: {str(e)}")
            raise MyException("Error viewing orders", str(e))
    
    def __del__(self):
        try:
            disconnect_db()
        except:
            logging.error("Error occurred while closing DB connection")


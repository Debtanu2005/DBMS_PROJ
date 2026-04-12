from src.data_connection.connection import connect_db, disconnect_db
from src.logger import logging
from src.exception import MyException


class CartView:
    def __init__(self):
        self.conn = connect_db()
        self.cursor = self.conn.cursor()

    def view_cart(self, user_id: int) -> list:
        try:
            self.cursor.execute(
                """
                SELECT c.cart_id, b.book_id, b.title, b.publisher, b.price,
                       ci.quantity, b.format, b.purchase_option, b.type
                FROM books b
                JOIN cart_items ci ON b.book_id = ci.book_id
                JOIN cart c ON ci.cart_id = c.cart_id
                WHERE c.student_id = %s
                """,
                (user_id,)
            )
            rows = self.cursor.fetchall()
            return [
                {
                    "cart_id"         : row[0],
                    "book_id"         : row[1],
                    "title"           : row[2],
                    "author"          : row[3],
                    "price"           : float(row[4]),
                    "quantity"        : row[5],
                    "format"          : row[6],
                    "purchase_option" : row[7],
                    "type"            : row[8]
                }
                for row in rows
            ]
        except Exception as e:
            logging.error(f"Error viewing cart for user_id {user_id}: {str(e)}")
            raise MyException("Error viewing cart", str(e))

    def __del__(self):
        try:
            disconnect_db()
        except:
            logging.error("Error occurred while closing DB connection")
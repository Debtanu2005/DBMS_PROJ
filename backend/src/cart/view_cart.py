from src.data_connection.connection import connect_db, disconnect_db
from src.logger import logging
from src.exception import MyException

class CartView:
    def __init__(self):
        self.conn = connect_db()
        self.cursor = self.conn.cursor()

    # ================== VIEW CART ==================
    def view_cart(self, user_id: int) -> list:
        try: 
            self.cursor.execute(
                """
                select c.cart_id, b.title , b.isbn, c.quantity from books b 
                join cart_items c on b.book_id = c.book_id
                join cart c1 on c.cart_id = c1.cart_id
                where c1.student_id = %s
                """,
                (user_id,)
            )
            return self.cursor.fetchall()
        except Exception as e:
            logging.error(f"Error viewing cart for user_id {user_id}: {str(e)}")
            raise MyException("Error viewing cart", "An error occurred while retrieving cart items")
    
    def __del__(self):
        try:
            disconnect_db()
        except:
            logging.error("Error occurred while closing DB connection")
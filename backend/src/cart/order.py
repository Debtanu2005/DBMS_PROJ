from src.data_connection.connection import connect_db, disconnect_db
from src.logger import logging
from src.exception import MyException
from src.artifacts.entities import order_desc
import datetime


class OrderManager:
    def __init__(self):
        self.conn = connect_db()
        self.cursor = self.conn.cursor()

    # ================== already ordered check ==================
    def already_ordered(self, user_id: int) -> bool:
        self.cursor.execute(
            """
            SELECT o.order_id
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            JOIN cart_items ci ON oi.book_id = ci.book_id
            JOIN cart c ON ci.cart_id = c.cart_id
            WHERE c.student_id = %s AND o.created_at >= NOW() - INTERVAL '1 day'
            """,
            (user_id,)
        )
        return self.cursor.fetchone() is not None

    # ================= CREATE ORDER =================

    def execute_order(self, user_id: int, order_info: order_desc) -> int:
        self.cursor.execute(
         """
            INSERT INTO orders (student_id, created_at, status, shipping_type, card_type, card_last4)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING order_id
            """,
            (
                user_id,
                datetime.datetime.utcnow(), 
                "new",
                order_info.shipping_type,
                order_info.card_type,
                order_info.card_last_four
            )
        )


        return self.cursor.fetchone()[0]

    # ================= COPY CART → ORDER ITEMS =================
    def order_items(self, order_id: int, cart_id: int):
        self.cursor.execute(
            """
            INSERT INTO order_items (order_id, book_id, quantity)
            SELECT %s, book_id, quantity
            FROM cart_items
            WHERE cart_id = %s
            """,
            (order_id, cart_id)
        )

    # ================= UPDATE STOCK =================
    def update_books_table(self, cart_id: int):
        self.cursor.execute(
            """
            UPDATE books b
            SET quantity = b.quantity - ci.quantity
            FROM cart_items ci
            WHERE ci.cart_id = %s AND ci.book_id = b.book_id
            """,
            (cart_id,)
        )

    # ================= DELETE CART =================
    def delete_cart(self, cart_id: int):
        self.cursor.execute(
            "DELETE FROM cart_items WHERE cart_id = %s",
            (cart_id,)
        )
        self.cursor.execute(
            "DELETE FROM cart WHERE cart_id = %s",
            (cart_id,)
        )

    # ================= FULL ORDER (TRANSACTION SAFE) =================
    def execute_full_order(self, user_id: int, cart_id: int, order_info: order_desc) -> dict:
        try:
            # Check if user has already ordered in the last 24 hours
            if self.already_ordered(user_id):
                raise MyException("Order limit exceeded", "You can only place one order every 24 hours")

            #  Create order
            order_id = self.execute_order(user_id, order_info)

            #  Copy items
            self.order_items(order_id, cart_id)

            #  Update stock
            self.update_books_table(cart_id)

            #  Delete cart
            self.delete_cart(cart_id)

            # COMMIT ONCE (IMPORTANT)
            self.conn.commit()

            logging.info(f"Order {order_id} completed for user {user_id}")

            return {"order_id": order_id}

        except Exception as e:
            self.conn.rollback()  
            logging.error(f"Error executing order: {str(e)}")
            raise MyException("Failed to execute order", str(e))

    def __del__(self):
        try:
            disconnect_db()
        except:
            logging.error("Error closing DB connection")
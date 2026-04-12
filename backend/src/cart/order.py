from src.data_connection.connection import connect_db
from src.logger import logging
from src.exception import MyException
from src.artifacts.entities import order_desc
import datetime
import sys


class OrderManager:
    def __init__(self):
        self.conn = connect_db()
        self.cursor = self.conn.cursor()

    def get_orders(self, user_id: int) -> dict:
        self.cursor.execute(
            """
            SELECT 
                o.order_id,
                o.status,
                o.created_at,
                COALESCE(SUM(oi.quantity * b.price), 0) AS total,
                COALESCE(
                    json_agg(
                        json_build_object(
                            'title',    b.title,
                            'author',   b.author,
                            'quantity', oi.quantity,
                            'price',    b.price
                        )
                    ) FILTER (WHERE b.book_id IS NOT NULL),
                    '[]'::json
                ) AS items
            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            LEFT JOIN books b ON oi.book_id = b.book_id
            WHERE o.student_id = %s
            GROUP BY o.order_id
            ORDER BY o.created_at DESC
            """,
            (user_id,)
        )

        results = self.cursor.fetchall()
        orders = []
        for row in results:
            orders.append({
                "order_id":   row[0],
                "status":     row[1],
                "created_at": row[2].isoformat() if row[2] else None,
                "total":      float(row[3]),
                "items":      row[4] if row[4] else []
            })

        return {"orders": orders}

    def already_ordered(self, user_id: int) -> bool:
        self.cursor.execute(
            """
            SELECT o.order_id
            FROM orders o
            WHERE o.student_id = %s 
            AND o.created_at >= NOW() - INTERVAL '1 day'
            LIMIT 1
            """,
            (user_id,)
        )
        return self.cursor.fetchone() is not None

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
        order_id = self.cursor.fetchone()[0]
        print("DEBUG order_id:", order_id)
        return order_id

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

    def update_books_table(self, cart_id: int):
        self.cursor.execute(
            """
            UPDATE books
            SET quantity = books.quantity - ci.quantity
            FROM cart_items ci
            WHERE ci.book_id = books.book_id
            AND ci.cart_id = %s
            """,
            (cart_id,)
        )

    def delete_cart(self, cart_id: int):
        self.cursor.execute(
            "DELETE FROM cart_items WHERE cart_id = %s",
            (cart_id,)
        )
        self.cursor.execute(
            "DELETE FROM cart WHERE cart_id = %s",
            (cart_id,)
        )

    def execute_full_order(self, user_id: int, cart_id: int, order_info: order_desc) -> dict:
        try:
            if self.already_ordered(user_id):
                raise MyException("Order limit exceeded", "You can only place one order every 24 hours", sys)

            order_id = self.execute_order(user_id, order_info)
            self.order_items(order_id, cart_id) 
            self.update_books_table(cart_id)
            self.delete_cart(cart_id)
            self.conn.commit()

            logging.info(f"Order {order_id} completed for user {user_id}")
            return {"order_id": order_id}

        except Exception as e:
            self.conn.rollback()
            logging.error(f"Error executing order: {str(e)}")
            raise e

    def __del__(self):
        try:
            self.cursor.close()
            self.conn.close()
        except Exception:
            pass
from src.data_connection.connection import connect_db, disconnect_db
from src.logger import logging
from src.exception import MyException
import sys


class ViewOrders:
    def __init__(self):
        self.conn = connect_db()
        self.cursor = self.conn.cursor()

    # ================== VIEW ORDERS ==================
    def view_orders(self, user_id: int) -> list:
        try:
            self.cursor.execute("""
                SELECT 
                    o.order_id,
                    o.status,
                    o.created_at,
                    o.shipping_type,
                    o.card_type,

                    b.book_id,
                    b.title,
                    b.price,
                    oi.quantity

                FROM orders o
                JOIN order_items oi ON o.order_id = oi.order_id
                JOIN books b ON oi.book_id = b.book_id
                WHERE o.student_id = %s
                ORDER BY o.created_at DESC
            """, (user_id,))

            rows = self.cursor.fetchall()

            orders_map = {}

            for row in rows:
                order_id = row[0]

                if order_id not in orders_map:
                    orders_map[order_id] = {
                        "order_id": order_id,
                        "status": row[1],
                        "created_at": row[2],
                        "order_total": 0,
                        "items": []
                    }

                item = {
                    "title": row[6],
                    "price": float(row[7]),
                    "quantity": row[8]
                }

                # add item
                orders_map[order_id]["items"].append(item)

                # calculate total
                orders_map[order_id]["order_total"] += item["price"] * item["quantity"]

            return list(orders_map.values())

        except Exception as e:
            logging.exception("Error viewing orders")
            raise MyException("Error viewing orders", sys)
    
    def __del__(self):
        try:
            disconnect_db()
        except:
            logging.error("Error occurred while closing DB connection")


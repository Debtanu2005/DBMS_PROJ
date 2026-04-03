from src.data_connection.connection import connect_db, disconnect_db
from src.artifacts.entities import Cart_Item

class OrderBook:
    def __init__(self):
        self.conn = connect_db()
        self.cursor = self.conn.cursor()

    def add_to_cart(self, order) -> int:
        """
        Adds a book to student's cart.
        If cart doesn't exist → creates one.
        If book already exists → updates quantity.
        Returns cart_id
        """

        # Step 1: Check if cart exists
        self.cursor.execute("""
            SELECT cart_id FROM cart WHERE student_id = %s
        """, (order.student_id,))
        
        result = self.cursor.fetchone()

        # Step 2: Create cart if not exists
        if result is None:
            self.cursor.execute("""
                INSERT INTO cart (student_id)
                VALUES (%s)
                RETURNING cart_id
            """, (order.student_id,))
            
            cart_id = self.cursor.fetchone()[0]
        else:
            cart_id = result[0]

        # Step 3: Check if book already in cart
        self.cursor.execute("""
            SELECT id, quantity FROM cart_items
            WHERE cart_id = %s AND book_id = %s
        """, (cart_id, order.book_id))

        item = self.cursor.fetchone()

        if item:
            # Step 4: Update quantity
            self.cursor.execute("""
                UPDATE cart_items
                SET quantity = quantity + %s
                WHERE id = %s
            """, (order.quantity, item[0]))
        else:
            # Step 5: Insert new item
            self.cursor.execute("""
                INSERT INTO cart_items (cart_id, book_id, quantity)
                VALUES (%s, %s, %s)
            """, (cart_id, order.book_id, order.quantity))

        self.conn.commit()
        return cart_id

    def get_cart(self, student_id: int):
        """
        Fetch all items in student's cart
        """

        self.cursor.execute("""
            SELECT c.cart_id, ci.book_id, ci.quantity
            FROM cart c
            JOIN cart_items ci ON c.cart_id = ci.cart_id
            WHERE c.student_id = %s
        """, (student_id,))

        return self.cursor.fetchall()

    def remove_from_cart(self, cart_id: int, book_id: int):
        """
        Remove a book from cart
        """

        self.cursor.execute("""
            DELETE FROM cart_items
            WHERE cart_id = %s AND book_id = %s
        """, (cart_id, book_id))

        self.conn.commit()
        return {"message": "Item removed"}

    def clear_cart(self, cart_id: int):
        """
        Remove all items from cart
        """

        self.cursor.execute("""
            DELETE FROM cart_items
            WHERE cart_id = %s
        """, (cart_id,))

        self.conn.commit()
        return {"message": "Cart cleared"}

    def __del__(self):
        try:
            self.cursor.close()
            disconnect_db(self.conn)
        except:
            pass
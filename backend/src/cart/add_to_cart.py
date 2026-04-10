from src.data_connection.connection import connect_db, disconnect_db
from src.logger import logging
from src.exception import MyException

class CartManager:
    def __init__(self):
        self.conn = connect_db()
        self.cursor = self.conn.cursor()

    def check_user_cart(self, user_id: int)->dict  | None:
        self.cursor.execute("SELECT cart_id FROM cart WHERE student_id = %s", (user_id,))
        cart = self.cursor.fetchone()
        if cart:
            return {"cart_id": cart[0], "user_id": user_id}  # Return existing cart_id
        else:
            return None
    def create_cart(self, user_id: int) -> dict:
        self.cursor.execute("INSERT INTO cart (student_id) VALUES (%s) RETURNING cart_id", (user_id,))
        cart_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return {"cart_id": cart_id, "user_id": user_id}
    def add_to_cart(self, user_id: int, book_id: int, quantity: int):
        try:
            # ✅ Check student
            self.cursor.execute(
                "SELECT student_id FROM students WHERE student_id = %s",
                (user_id,)
            )
            if not self.cursor.fetchone():
                raise MyException(f"Student {user_id} does not exist", "Invalid user")

            # ✅ Check book
            self.cursor.execute(
                "SELECT book_id FROM books WHERE book_id = %s",
                (book_id,)
            )
            if not self.cursor.fetchone():
                raise MyException(f"Book {book_id} does not exist", "Invalid book")

            # ✅ Cart logic
            cart_data = self.check_user_cart(user_id)
            cart_id = cart_data["cart_id"] if cart_data else None

            if not cart_id:
                cart_id = self.create_cart(user_id)["cart_id"]

            # ✅ Check existing item
            self.cursor.execute(
                "SELECT quantity FROM cart_items WHERE cart_id = %s AND book_id = %s",
                (cart_id, book_id)
            )
            existing_item = self.cursor.fetchone()

            if existing_item:
                new_quantity = existing_item[0] + quantity
                self.cursor.execute(
                    "UPDATE cart_items SET quantity = %s WHERE cart_id = %s AND book_id = %s",
                    (new_quantity, cart_id, book_id)
                )
            else:
                self.cursor.execute(
                    "INSERT INTO cart_items (cart_id, book_id, quantity) VALUES (%s, %s, %s)",
                    (cart_id, book_id, quantity)
                )

            self.conn.commit()

            return {
                "cart_id": cart_id,
                "user_id": user_id,
                "book_id": book_id,
                "quantity": quantity
            }

        except Exception as e:
            self.conn.rollback()  
            logging.error(f"Error adding to cart: {str(e)}")
            raise MyException("Failed to add item to cart", str(e))
        
        
    def __del__(self):
        try:
            disconnect_db() 
        except:
            logging.error("Error occurred while closing the database connection")
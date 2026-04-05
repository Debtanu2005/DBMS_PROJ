from src.artifacts.entities import Cart_Item, cart, CourseBook
from src.data_connection.connection import connect_db, disconnect_db

class CartManager:
    def __init__(self):
        self.conn = connect_db()

        self.cursor = self.conn.cursor()
    def add_to_cart(self, order: Cart_Item, student_id: int) -> int:


        # ✅ Step 0: Validate book exists (using CourseBook structure)
        self.cursor.execute("""
            SELECT *
            FROM books
            WHERE book_id = %s
        """, (order.book_id,))

        book_data = self.cursor.fetchone()

        if  book_data:
            raise Exception("Book already exist")

        # Convert to CourseBook entity (optional but clean)
        book = CourseBook(
            course_id=0,  # not needed here
            book_id=book_data[0],
            title=book_data[2],
            isbn=book_data[1],
            publisher=book_data[3],
            price=book_data[4],
            quantity=book_data[5],
            type=book_data[6],
            purchase_option=book_data[7],
            format=book_data[8],
            language=book_data[9],
            edition=book_data[10],
            category=book_data[11]
        )

        # ✅ Step 1: Check if cart exists
        self.cursor.execute("""
            SELECT cart_id, student_id, created_at, updated_at
            FROM cart WHERE student_id = %s
        """, (student_id,))  # ⚠️ using student_id to find cart

        result = self.cursor.fetchone()

        if result is None:
            # ✅ Create new cart
            self.cursor.execute("""
                INSERT INTO cart (student_id)
                VALUES (%s)
                RETURNING cart_id, student_id, created_at, updated_at
            """, (order.cart_id,))

            cart_data = self.cursor.fetchone()

            user_cart = cart(
                cart_id=cart_data[0],
                student_id=cart_data[1],
                created_at=str(cart_data[2]),
                updated_at=str(cart_data[3])
            )
        else:
            user_cart = cart(
                cart_id=result[0],
                student_id=result[1],
                created_at=str(result[2]),
                updated_at=str(result[3])
            )

        # ✅ Step 2: Check if item exists in cart
        self.cursor.execute("""
            SELECT id, quantity FROM cart_items
            WHERE cart_id = %s AND book_id = %s
        """, (user_cart.cart_id, order.book_id))

        item = self.cursor.fetchone()

        if item:
            # ✅ Update quantity
            self.cursor.execute("""
                UPDATE cart_items
                SET quantity = quantity + %s
                WHERE id = %s
            """, (order.quantity, item[0]))
        else:
            # ✅ Insert new item
            self.cursor.execute("""
                INSERT INTO cart_items (cart_id, book_id, quantity)
                VALUES (%s, %s, %s)
            """, (user_cart.cart_id, order.book_id, order.quantity))

        self.conn.commit()

        return user_cart.cart_id
    
    def __del__(self):
        disconnect_db()

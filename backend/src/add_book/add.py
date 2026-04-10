from src.data_connection.connection import connect_db, disconnect_db
from src.logger import logging
from src.exception import MyException
from src.artifacts.entities import book_new
import sys


# ================= MANAGER =================
class BookADD:
    def __init__(self):
        self.conn = connect_db()
        self.cursor = self.conn.cursor()

    #  CHECK ADMIN
    def check_admin(self, user_id: int) -> bool:
        self.cursor.execute(
            "SELECT role FROM users WHERE user_id = %s",
            (user_id,)
        )
        data = self.cursor.fetchone()

        if data and data[0] in ("admin", "super_admin"):
            return True
        return False

    #  ADD BOOK
    def add_book(self, user_id: int, Book_info: book_new) -> int:
        try:
            # 🔐 Check admin
            if not self.check_admin(user_id):
                raise MyException("Not authorized", "Admin access required")

            # Validate ENUM values (VERY IMPORTANT)
            valid_types = ["new", "used"]
            valid_formats = ["hardcover", "softcover", "ebook"]
            valid_purchase = ["rent", "buy"]

            if Book_info.type not in valid_types:
                raise MyException("Invalid type", "Use 'new' or 'used'")

            if Book_info.format not in valid_formats:
                raise MyException("Invalid format", "Use hardcover/softcover/ebook")

            if Book_info.purchase_option not in valid_purchase:
                raise MyException("Invalid purchase option", "Use rent/buy")

            # Check duplicate ISBN
            self.cursor.execute(
                "SELECT book_id FROM books WHERE isbn = %s",
                (Book_info.isbn,)
            )
            if self.cursor.fetchone():
                raise MyException("Duplicate ISBN", "Book already exists")

            # Insert book (FIXED QUERY)
            self.cursor.execute(
                """
                INSERT INTO books
                (title, isbn, publisher, price, quantity, type,
                 purchase_option, format, language, edition, category)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING book_id
                """,
                (
                    Book_info.title,
                    Book_info.isbn,
                    Book_info.publisher,
                    Book_info.price,
                    Book_info.quantity,
                    Book_info.type,
                    Book_info.purchase_option,
                    Book_info.format,
                    Book_info.language,
                    Book_info.edition,
                    Book_info.category
                )
            )

            book_id = self.cursor.fetchone()[0]

            self.conn.commit()

            logging.info(f"Book added successfully with ID: {book_id}")

            return book_id

        except Exception as e:
            self.conn.rollback()   #  IMPORTANT
            logging.exception("Error adding book") 
            raise MyException("Failed to add book", str(e))

    def __del__(self):
        try:
            disconnect_db()
        except:
            logging.error("Error occurred while closing DB connection")
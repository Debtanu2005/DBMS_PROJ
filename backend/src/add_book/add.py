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

    # ================= CHECK ADMIN =================
    def check_admin(self, user_id: int) -> bool:
        self.cursor.execute(
            "SELECT role FROM users WHERE user_id = %s",
            (user_id,)
        )
        data = self.cursor.fetchone()

        if data and data[0] in ("admin", "super_admin"):
            return True
        return False

    # ================= ADD BOOK =================
    def add_book(self, user_id: int, Book_info: book_new) -> int:
        try:
            # ✅ Check admin
            if not self.check_admin(user_id):
                raise  MyException("Not authorized", sys)

            # ✅ Validate ENUM values
            valid_types = ["new", "used"]
            valid_formats = ["hardcover", "softcover", "ebook"]
            valid_purchase = ["rent", "buy"]

            # ❌ FIX: use correct attribute consistently
            if Book_info.book_type not in valid_types:
                raise MyException("Invalid type", "Use 'new' or 'used'")

            if Book_info.format not in valid_formats:
                raise MyException("Invalid format", "Use hardcover/softcover/ebook")

            if Book_info.purchase_option not in valid_purchase:
                raise MyException("Invalid purchase option", str(sys.exc_info()[1]))

            #Check duplicate ISBN
            self.cursor.execute(
                "SELECT book_id FROM books WHERE isbn = %s",
                (Book_info.isbn,)
            )
            if self.cursor.fetchone():
                raise MyException("Duplicate ISBN", "Book already exists")

            # Insert book
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
                    Book_info.book_type,   # FIXED
                    Book_info.purchase_option,
                    Book_info.format,
                    Book_info.language,
                    Book_info.edition,
                    Book_info.category
                )
            )

            # ✅ Get inserted book_id
            result = self.cursor.fetchone()
            if not result:
                raise MyException("Insert failed", "No book_id returned")

            book_id = result[0]

            # ✅ Insert into course_books
            self.cursor.execute(
                """
                INSERT INTO course_books (course_id, book_id, type)
                VALUES (%s, %s, %s)
                """,
                (
                    Book_info.course_id,
                    book_id,
                    Book_info.type   #FIXED (was inconsistent)
                )
            )

            # ✅ Commit
            self.conn.commit()

            logging.info(f"Book added successfully with ID: {book_id}")

            return book_id

        except Exception as e:
            self.conn.rollback()   # ✅ IMPORTANT
            logging.exception("Error adding book")
            raise MyException("Failed to add book", str(e))

    # ================= CLEANUP =================
    def __del__(self):
        try:
            disconnect_db()
        except Exception as e:
            logging.error(f"Error while closing DB connection: {str(e)}")
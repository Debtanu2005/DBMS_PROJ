from src.data_connection.connection import connect_db, disconnect_db
from src.logger import logging
from src.exception import MyException

class Add_review:
    def __init__(self):
        try:
            self.conn = connect_db()
            self.cursor = self.conn.cursor()
        except Exception as e:
            logging.error("Error occurred while connecting to the database")
            raise MyException("Error occurred while connecting to the database")

    def add_review(self, review_id: int, student_id: int, book_id: int, rating: int, comment: str) -> None:
        rev = self.cursor.execute(""" select * from reviews where review_id = %s && student_id = %s""", (review_id, student_id))
        if rev:
            raise MyException("Review already exists")
        
        self.cursor.execute(""" insert into reviews (review_id, student_id, book_id, rating, comment) 
            values (%s, %s, %s, %s, %s)""", (review_id, student_id, book_id, rating, comment))
        self.conn.commit()

    def __del__(self):
        disconnect_db()


    

        
from src.data_connection.connection import connect_db, disconnect_db

class BookSearch:
    def __init__(self):
        self.conn = connect_db()
        self.cursor = self.conn.cursor()

    def search(self, query):
        # Search for books by name or author
        self.cursor.execute("""
            SELECT books.book_id, books.title, books.publisher, books.quantity, reviews.rating
            FROM books join reviews on books.book_id = reviews.book_id
            WHERE title ILIKE %s OR publisher ILIKE %s
        """, (f'%{query}%', f'%{query}%'))
        
        results = self.cursor.fetchall()
        return results

    def __del__(self):
        disconnect_db()
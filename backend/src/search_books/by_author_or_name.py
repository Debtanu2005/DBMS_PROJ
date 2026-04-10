from src.data_connection.connection import connect_db, disconnect_db

class BookSearch:
    def __init__(self):
        self.conn = connect_db()
        self.cursor = self.conn.cursor()

    def search(self, query) -> dict:
        self.cursor.execute("""
            SELECT books.book_id, books.title, books.publisher, books.quantity, reviews.rating
            FROM books 
            JOIN reviews ON books.book_id = reviews.book_id
            WHERE title ILIKE %s OR publisher ILIKE %s
        """, (f'%{query}%', f'%{query}%'))

        results = self.cursor.fetchall()   # ✅ actual data
        
        book_ids = [row[0] for row in results]

        return {
            "book_ids": book_ids,
            "results": results
        }
    

    def __del__(self):
        disconnect_db()
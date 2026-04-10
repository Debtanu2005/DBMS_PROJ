from src.data_connection.connection import connect_db, disconnect_db

class CourseBookSearch:
    def __init__(self):
        self.conn = connect_db()
        self.cursor = self.conn.cursor()

    def search(self, course_name: str) -> dict:
        self.cursor.execute("""
            select b.book_id, b.title, b.author, b.stock, b.rating from  courses c1
            join course_books c on c1.course_id = c.course_id
            join books b on  c.book_id = b.book_id
            where c1.course_name = %s

        """, (course_name,))

        results = self.cursor.fetchall()   # ✅ actual data
        
        book_ids = [row[0] for row in results]

        books = []
        for row in results:
            books.append({
                "id": row[0],
                "title": row[1],
                "author": row[2],   # publisher used as author
                "stock": row[3],
                "rating": row[4]
            })

        return {
            "results": books
        }

    def __del__(self):
        disconnect_db()

from src.data_connection.connection import connect_db, disconnect_db
import datetime
from authentication.hashing import hash_password

def add_admin():
    conn = connect_db()
    cursor = conn.cursor()

    # Check if admin already exists
    cursor.execute("SELECT * FROM users WHERE email = %s", ("admin@example2.com",))
    admin = cursor.fetchone()

    if not admin:
        # Add a new admin user
        hashed_password = hash_password("admin12345")
        cursor.execute("""
            INSERT INTO users (email, password, role, created_at) VALUES
            (%s, %s, %s, %s)
        """, ("admin@example2.com", hashed_password, "admin", datetime.datetime.now()))
        conn.commit()
        print("Admin user added successfully.")
    else:
        print("Admin user already exists.")

    disconnect_db()

add_admin()
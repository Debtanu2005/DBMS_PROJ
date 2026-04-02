from src.data_connection.connection import connect_db, disconnect_db


def create_tables():
    # Establish connection to the database
    conn = connect_db()
    
    # Create a cursor object to execute SQL queries
    cursor = conn.cursor()

    # ========================= USERS TABLE =========================
    # Stores all types of users (student, admin, support, etc.)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,  -- Auto-incremented unique ID
            email VARCHAR(100) UNIQUE NOT NULL,  -- Unique email for login
            password VARCHAR(255) NOT NULL,  -- Hashed password
            role VARCHAR(20) CHECK (role IN ('student','support','admin','super_admin')) NOT NULL,  -- Role validation
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- Account creation time
        );
    """)

    # ========================= UNIVERSITIES TABLE =========================
    # Stores university details
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS universities (
            university_id SERIAL PRIMARY KEY,  -- Unique university ID
            name VARCHAR(100),
            address TEXT,
            rep_name VARCHAR(100),  -- Representative name
            rep_email VARCHAR(100),
            rep_phone VARCHAR(15)
        );
    """)

    # ========================= STUDENTS TABLE =========================
    # Stores student-specific details (linked to users table)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INT PRIMARY KEY,  -- Same as user_id
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            phone VARCHAR(15),
            dob DATE,  -- Date of birth
            university_id INT,  -- Foreign key to universities
            major VARCHAR(50),
            status VARCHAR(10) CHECK (status IN ('UG','PG')),  -- Undergraduate/Postgraduate
            year_of_student INT,
            FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (university_id) REFERENCES universities(university_id)
        );
    """)

    # ========================= EMPLOYEES TABLE =========================
    # Stores employee/support/admin details
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            emp_id INT PRIMARY KEY,  -- Same as user_id
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            gender VARCHAR(10),
            salary DECIMAL(10,2),
            aadhaar VARCHAR(20) UNIQUE,  -- Unique government ID
            phone VARCHAR(15),
            FOREIGN KEY (emp_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
    """)

    # ========================= DEPARTMENTS TABLE =========================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            dept_id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            university_id INT,
            FOREIGN KEY (university_id) REFERENCES universities(university_id)
        );
    """)

    # ========================= INSTRUCTORS TABLE =========================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS instructors (
            instructor_id SERIAL PRIMARY KEY,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            university_id INT,
            dept_id INT,
            FOREIGN KEY (university_id) REFERENCES universities(university_id),
            FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
        );
    """)

    # ========================= COURSES TABLE =========================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            course_id SERIAL PRIMARY KEY,
            course_name VARCHAR(100),
            university_id INT,
            year_of_course INT,
            semester INT,
            FOREIGN KEY (university_id) REFERENCES universities(university_id)
        );
    """)

    # ========================= COURSE-DEPARTMENT (M:N) =========================
    # Many-to-many relationship between courses and departments
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS course_depart (
            course_id INT,
            dept_id INT,
            PRIMARY KEY(course_id, dept_id),
            FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
            FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE CASCADE
        );
        """)
    
    # ========================= COURSE-INSTRUCTOR (M:N) =========================
    # Many-to-many relationship between courses and instructors
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS course_instructor (
        course_id INT,
        instructor_id INT,
        PRIMARY KEY (course_id, instructor_id),
        FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
        FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id) ON DELETE CASCADE
    );
    """)

    # ========================= BOOKS TABLE =========================
    # Stores book inventory
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            book_id SERIAL PRIMARY KEY,
            title VARCHAR(200),
            isbn VARCHAR(50) UNIQUE,
            publisher VARCHAR(100),
            price DECIMAL(10,2),
            quantity INT,
            type VARCHAR(10) CHECK (type IN ('new','used')),
            purchase_option VARCHAR(10) CHECK (purchase_option IN ('rent','buy')),
            format VARCHAR(20) CHECK (format IN ('hardcover','softcover','ebook')),
            language VARCHAR(50),
            edition INT,
            category VARCHAR(100)
        );
    """)

    # ========================= COURSE-BOOKS (M:N) =========================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS course_books (
            course_id INT,
            book_id INT,
            type VARCHAR(20) CHECK (type IN ('required','recommended')),
            PRIMARY KEY (course_id, book_id),
            FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE,
            FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
        );
    """)

    # ========================= CART TABLE =========================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart (
            cart_id SERIAL PRIMARY KEY,
            student_id INT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        );
    """)

    # ========================= CART ITEMS =========================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cart_items (
            cart_id INT,
            book_id INT,
            quantity INT,
            PRIMARY KEY (cart_id, book_id),
            FOREIGN KEY (cart_id) REFERENCES cart(cart_id) ON DELETE CASCADE,
            FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
        );
    """)

    # ========================= ORDERS =========================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id SERIAL PRIMARY KEY,
            student_id INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) CHECK (status IN ('new','processed','shipped','canceled')),
            shipping_type VARCHAR(20) CHECK (shipping_type IN ('standard','2-day','1-day')),
            card_type VARCHAR(20),
            card_last4 VARCHAR(4),
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE
        );
    """)

    # ========================= ORDER ITEMS =========================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            order_id INT,
            book_id INT,
            quantity INT,
            PRIMARY KEY (order_id, book_id),
            FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
            FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
        );
    """)

    # ========================= TICKETS =========================
    # Support/helpdesk system
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id SERIAL PRIMARY KEY,
            created_by INT,
            category VARCHAR(20) CHECK (category IN ('profile','products','cart','orders','other')),
            title VARCHAR(200),
            description TEXT,
            status VARCHAR(20) CHECK (status IN ('new','assigned','in_progress','completed')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_by INT,
            FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (resolved_by) REFERENCES employees(emp_id) ON DELETE SET NULL
        );
    """)

    # ========================= REVIEWS =========================
    # User reviews for books
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            review_id SERIAL PRIMARY KEY,
            student_id INT,
            book_id INT,
            rating INT CHECK (rating BETWEEN 1 AND 5),
            comment TEXT,
            FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE
        );
    """)
   
    # Save all changes to database
    conn.commit()

    # Close cursor
    cursor.close()

    print("All tables created successfully.")

    # Disconnect from database
    disconnect_db()

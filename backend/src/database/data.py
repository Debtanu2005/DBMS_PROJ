from src.data_connection.connection import connect_db, disconnect_db

def insert_data():
    conn = connect_db()
    cursor = conn.cursor()

    # ================= USERS =================
    cursor.execute("""
    INSERT INTO users (email,password,role) VALUES
    ('s1@mail.com','pass','student'),
    ('s2@mail.com','pass','student'),
    ('s3@mail.com','pass','student'),
    ('admin1@mail.com','pass','admin'),
    ('support1@mail.com','pass','support'),
    ('super@mail.com','pass','super_admin');
    """)

    # ================= UNIVERSITIES =================
    cursor.execute("""
    INSERT INTO universities (name,address,rep_name,rep_email,rep_phone) VALUES
    ('IIT Delhi','Delhi','Raj','raj@iitd.ac.in','9999999991'),
    ('NIT Trichy','TN','Suresh','suresh@nitt.edu','9999999992'),
    ('BITS Pilani','Rajasthan','Anil','anil@bits.edu','9999999993');
    """)

    # ================= STUDENTS =================
    cursor.execute("""
    INSERT INTO students VALUES
    (1,'Rahul','Reddy','9000000001','2003-01-01',1,'CSE','UG',3),
    (2,'Anjali','Sharma','9000000002','2002-02-02',2,'ECE','UG',4),
    (3,'Kiran','Patel','9000000003','2004-03-03',3,'ME','UG',2);
    """)

    # ================= EMPLOYEES =================
    cursor.execute("""
    INSERT INTO employees VALUES
    (4,'Admin','One','M',90000,'111111111111','8000000001'),
    (5,'Support','One','F',50000,'222222222222','8000000002');
    """)

    # ================= DEPARTMENTS =================
    cursor.execute("""
    INSERT INTO departments (name,university_id) VALUES
    ('CSE',1),('ECE',1),('ME',2),('EEE',2),('CS',3);
    """)

    # ================= INSTRUCTORS =================
    cursor.execute("""
    INSERT INTO instructors (first_name,last_name,university_id,dept_id) VALUES
    ('Dr','A',1,1),
    ('Dr','B',1,2),
    ('Dr','C',2,3),
    ('Dr','D',3,5);
    """)

    # ================= COURSES =================
    cursor.execute("""
    INSERT INTO courses (course_name,university_id,year_of_course,semester) VALUES
    ('Data Structures',1,2025,1),
    ('Operating Systems',1,2025,2),
    ('Digital Electronics',2,2025,1),
    ('Thermodynamics',2,2025,2),
    ('Algorithms',3,2025,1);
    """)

    # ================= COURSE-DEPARTMENT =================
    cursor.execute("""
    INSERT INTO course_depart VALUES
    (1,1),(1,2),
    (2,1),
    (3,4),
    (4,3),
    (5,5);
    """)

    # ================= COURSE-INSTRUCTOR =================
    cursor.execute("""
    INSERT INTO course_instructor VALUES
    (1,1),(2,1),
    (3,2),(4,3),
    (5,4);
    """)

    # ================= BOOKS =================
    cursor.execute("""
    INSERT INTO books (title,isbn,publisher,price,quantity,type,purchase_option,format,language,edition,category) VALUES
    ('DSA Made Easy','ISBN001','Pearson',500,20,'new','buy','hardcover','English',1,'CS'),
    ('OS Concepts','ISBN002','Wiley',650,15,'new','buy','softcover','English',2,'CS'),
    ('Digital Circuits','ISBN003','McGraw',400,10,'used','rent','ebook','English',3,'ECE'),
    ('Thermodynamics Basics','ISBN004','Springer',550,12,'new','buy','hardcover','English',1,'ME'),
    ('Algorithms Unlocked','ISBN005','MIT Press',700,8,'new','buy','ebook','English',2,'CS'),
    ('Advanced DSA','ISBN006','Pearson',800,5,'used','rent','softcover','English',3,'CS'),
    ('Microprocessors','ISBN007','Oxford',450,9,'new','buy','hardcover','English',2,'ECE'),
    ('Fluid Mechanics','ISBN008','Elsevier',600,7,'new','buy','softcover','English',1,'ME');
    """)

    # ================= COURSE-BOOK =================
    cursor.execute("""
    INSERT INTO course_books VALUES
    (1,1,'required'),
    (1,6,'recommended'),
    (2,2,'required'),
    (3,3,'required'),
    (3,7,'recommended'),
    (4,4,'required'),
    (5,5,'required');
    """)

    # ================= CART =================
    cursor.execute("""
    INSERT INTO cart (student_id) VALUES (1),(2),(3);
    """)

    # ================= CART ITEMS =================
    cursor.execute("""
    INSERT INTO cart_items VALUES
    (1,1,1),(1,6,1),
    (2,3,2),
    (3,5,1),(3,8,1);
    """)

    # ================= ORDERS =================
    cursor.execute("""
    INSERT INTO orders (student_id,status,shipping_type,card_type,card_last4) VALUES
    (1,'new','standard','VISA','1234'),
    (2,'processed','2-day','MASTER','5678'),
    (3,'shipped','1-day','VISA','9999');
    """)

    # ================= ORDER ITEMS =================
    cursor.execute("""
    INSERT INTO order_items VALUES
    (1,1,1),(1,6,1),
    (2,3,2),
    (3,5,1);
    """)

    # ================= TICKETS =================
    cursor.execute("""
    INSERT INTO tickets (created_by,category,title,description,status,resolved_by) VALUES
    (1,'products','Wrong Book','Received wrong item','new',NULL),
    (2,'orders','Late Delivery','Order delayed','assigned',5),
    (3,'cart','Cart Bug','Items disappearing','in_progress',5);
    """)

    # ================= REVIEWS =================
    cursor.execute("""
    INSERT INTO reviews (student_id,book_id,rating,comment) VALUES
    (1,1,5,'Excellent book'),
    (2,3,4,'Good content'),
    (3,5,5,'Very useful'),
    (1,6,3,'Average'),
    (2,2,4,'Nice explanations');
    """)

    # Commit all inserts
    conn.commit()

    cursor.close()
    disconnect_db()

    print("Data inserted successfully!")
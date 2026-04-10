from authentication.register import RegisterManager
from src.artifacts.entities import student

if __name__ == "__main__":
    register_manager = RegisterManager()
    student_info = student(
        first_name="John",
        last_name="Doe5",
        phone="1234567690",
        dob="1995-01-01",
        university_id=3,
        major="electrical engineering",
        status="PG",
        year_of_student=3,
        role="student"
    )
    email = "john.doe@example4.com"
    password = "password123"
    try:
        token = register_manager.register(email, password, student_info)
        print("Registration successful. JWT Token:", token)
    except Exception as e:
        print("Registration failed:", str(e))

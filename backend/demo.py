from authentication.register import RegisterManager  
from authentication.login import LoginManager

if __name__== "__main__":
    login_manager = LoginManager()
    try:
        token = login_manager.login(
            email="pqrst@gmail.com",
            password="wordpass123"
        )
        print(f"Login successful. Access token: {token}")
    except Exception as e:
        print(f"Login failed: {e}")
    

# if __name__ == "__main__":
#     register_manager = RegisterManager()

#     # Sample student data (dict)
#     student_data = {
#         "first_name": "John",
#         "last_name": "Doe",
#         "phone": "1234567890",
#         "dob": "2000-01-01",
#         "university_id": 1,
#         "major": "Computer Science",
#         "status": "UG",
#         "year_of_student": 2,
#         "role": "student"
#     }

#     # ✅ Convert dict → student object
#     student_info = student(**student_data)

#     try:
#         token = register_manager.register(
#             email="example@example.com",
#             password="password123",
#             student_info=student_info
#         )
#         print(f"Registration successful. Access token: {token}")

#     except Exception as e:
#         print(f"Registration failed: {e}")


#create a student object and register a user using the RegisterManager class. This will test the entire registration flow, including database insertion and JWT token creation.
# if __name__ == "__main__":
#     student_info = student(
#         first_name="John",
#         last_name="Doe",
#         phone="1234567890",
#         dob="2000-01-01",
#         university_id=1,
#         major="Computer Science",
#         status="UG",
#         year_of_student=2,
#         role="student"
#     )
#     register_manager = RegisterManager()
#     try:
#         token = register_manager.register(
#             email="pqrst@gmail.com",
#             password="wordpass123",
#             student_info=student_info
#         )
#         print(f"Registration successful. Access token: {token}")
#     except Exception as e:
#         print(f"Registration failed: {e}")
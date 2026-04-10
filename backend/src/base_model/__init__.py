from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

class Student(BaseModel):
    first_name: str
    last_name: str
    phone: str
    dob: str
    university_id: int
    major: str
    status: str
    year_of_student: int
    role: str

from dataclasses import dataclass
from typing import Optional, Literal


@dataclass
class student:
    first_name: str
    last_name: str
    phone: str
    dob: str
    university_id: int
    major: str
    status: str
    year_of_student: int
    role: str ="student"
    student_id: Optional[int] = None 

@dataclass
class Cart_Item:
    cart_id: int
    book_id: int
    quantity: int

@dataclass
class cart:
    student_id: int
    cart_id: int
    created_at: str
    updated_at: str
@dataclass
class CourseBook:
    course_id: int
    book_id: int
    title: str
    isbn: str
    publisher: str
    price: float
    quantity: int
    type: str
    purchase_option: str
    format: str
    language: str
    edition: int
    category: str

@dataclass
class order_desc:
    # order_id: int
    # student_id: int
    # created_at: str
    status: str
    shipping_type: str
    card_type: str
    card_last_four: str

@dataclass
class book_new:
    title: str
    isbn : str
    publisher: str 
    price: int
    quantity: int
    book_type: str
    purchase_option: str 
    format: str
    language: str
    edition : int
    category: str

@dataclass
class TicketCreate:
    category: Literal['profile', 'products', 'cart', 'orders', 'other']
    title: str
    description: str

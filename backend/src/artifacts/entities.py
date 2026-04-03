from dataclasses import dataclass

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
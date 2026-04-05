from fastapi import APIRouter
from authentication.register import RegisterManager
from authentication.login import LoginManager
from src.artifacts.entities import student
from src.search_books.by_author_or_name import BookSearch
router = APIRouter()

@router.post("/register")
def register_user(email: str, password: str, student_info: dict):
    student_info = student(**student_info)
    register_manager = RegisterManager()
    try:
        token = register_manager.register(email, password, student_info)
        return {"access_token": token}
    except Exception as e:
        return {"error": str(e)}

@router.post("/login")
def login_user(email: str, password: str):
    login_manager = LoginManager()
    try:
        token = login_manager.login(email, password)
        return {"access_token": token}
    except Exception as e:
        return {"error": str(e)}
    
@router.get("/login/search_books")
def search_books(author: str = None, name: str = None):
    book_search = BookSearch()
    try:
        books = book_search.search(author=author, name=name)
        return {"books": books}
    except Exception as e:
        return {"error": str(e)}
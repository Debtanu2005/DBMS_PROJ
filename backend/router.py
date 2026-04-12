
from fastapi import APIRouter, Request, Depends, HTTPException, status, Body
from authentication.register import RegisterManager
from authentication.login import LoginManager
from src.artifacts.entities import book_new, student, order_desc  # FIXED: Combined imports
from src.search_books.by_author_or_name import BookSearch
from src.cart.order import OrderManager
from src.cart.add_to_cart import CartManager
from authentication.jwt import verify_token 
from src.cart.view_cart import CartView
from src.cart.view_orders import ViewOrders
from src.base_model import LoginRequest
from src.add_book.add import BookADD

from authentication.dependencies import student_only
from src.artifacts.entities import TicketCreate
from src.managers.ticket_manager import TicketManager
from src.data_connection.connection import connect_db, disconnect_db
from src.logger import logging
from src.exception import MyException

router = APIRouter()

# ================= NEW: AUTH DEPENDENCY =================
# This replaces the repetitive token extraction in every route
async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Missing or invalid Authorization header"
        )
    try:
        token = auth_header.split(" ")[1]
        payload = verify_token(token)
        return payload["user_id"]
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid token"
        )

# ================= REGISTER =================
@router.post("/register")
async def register_user(data: dict ):
    register_manager = RegisterManager()
    try:
        email = data["email"]
        password = data["password"]
        # FIXED: Added .get() to prevent KeyErrors if student_info is missing
        student_info = student(**data.get("student_info", {}))
        token = register_manager.register(email, password, student_info)
        return {"access_token": token}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) # CHANGED: Proper HTTP error

# ================= LOGIN =================
@router.post("/login")
async def login_user(data: LoginRequest):
    login_manager = LoginManager()
    try:
        # data is now an object, access properties with dot notation
        token = login_manager.login(data.email, data.password)
        print("LOGIN TOKEN:", token)
        return {"data": token}
        # result = login_manager.login(data.email, data.password)
        # return result
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e)) # CHANGED: 401 for Login fail

# ================= SEARCH BOOKS =================

@router.get("/search_books")
async def search_books(q: str = None, author: str = None, name: str = None):
    book_search = BookSearch()
    try:
        query = q or name or author   # ✅ FIX
        books = book_search.search(query=query)
        print("SEARCH RESULT:", books)
        return books 

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================= ADD TO CART =================
# CHANGED: Added Depends(get_current_user)
@router.post("/add_to_cart")
async def add_to_cart(book_id: int, quantity: int = 1, user_id: int = Depends(get_current_user)):
    cart_manager = CartManager()
    try:
        result = cart_manager.add_to_cart(
            user_id=user_id,
            book_id=book_id,
            quantity=quantity
        )
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ================= EXECUTE ORDER =================
# CHANGED: Added Depends(get_current_user)
@router.post("/execute_order")
async def execute_order(
    cart_id: int,
    order_info: dict = Body(...),
    user_id: int = Depends(get_current_user)
):
    try:
        print("ORDER INFO RECEIVED:", order_info)
        print("CART ID:", cart_id)
        print("USER ID:", user_id)

        order_description = order_desc(
            status=order_info.get('status', 'new'),
            shipping_type=order_info.get('shipping_type', 'standard'),
            card_type=order_info.get('card_type', 'CASH'),
            card_last_four=order_info.get('card_last_four', '0000')
        )

        order_manager = OrderManager()
        result = order_manager.execute_full_order(
            user_id=user_id,
            cart_id=cart_id,
            order_info=order_description
        )
        return result   # ← return result directly, not wrapped in {"result": result}

    except MyException as e:
        print("ORDER ERROR (known):", str(e))
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        print("ORDER ERROR (unexpected):", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    

# ================= VIEW CART =================
@router.get("/view_cart")
async def view_cart(user_id: int = Depends(get_current_user)):
    cart_view = CartView()
    try:
        cart_items = cart_view.view_cart(user_id)
        return {"cart_items": cart_items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================= VIEW ORDERS =================
@router.get("/view_orders")
async def view_orders_endpoint(user_id: int = Depends(get_current_user)):
    orders_service = ViewOrders() # CHANGED: Renamed variable to avoid class conflict
    try:
        orders = orders_service.view_orders(user_id)
        return {"orders": orders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# ================= ADD BOOK (ADMIN) =================
@router.post("/add_book")
async def add_book_endpoint(
    book_info: dict,
    user=Depends(get_current_user)   # get full user, not just id
):
    try:
        # ADMIN CHECK
        if user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin only")

        book_add_service = BookADD()
        book_data = book_new(**book_info)

        new_book_id = book_add_service.add_book(user.id, book_data)

        return {"book_id": new_book_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


    # ================= CREATE TICKETS =================
@router.post("/ticket/create")
def create_ticket(request: Request, ticket: TicketCreate):
    user = student_only(request)
    print("TOKEN PAYLOAD:", user)  # ← add this, check terminal
    manager = TicketManager()
    user_id = user.get("user_id") or user.get("sub") or user.get("id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id not found in token")
    return manager.create_ticket(user_id, ticket.category, ticket.title, ticket.description)


@router.get("/all_books")
def get_all_books():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT book_id, title, publisher, price, quantity,
                   type, purchase_option, format, language, edition, category
            FROM books
        """)
        rows = cursor.fetchall()
        cursor.close()
        return [
            {
                "book_id"         : row[0],
                "title"           : row[1],
                "author"          : row[2],  
                "price"           : float(row[3]),
                "quantity"        : row[4],
                "type"            : row[5],
                "purchase_option" : row[6],
                "format"          : row[7],
                "language"        : row[8],
                "edition"         : row[9],
                "category"        : row[10]
            }
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@router.post("/remove_from_cart")
async def remove_from_cart(book_id: int, user_id: int = Depends(get_current_user)):
    cart_manager = CartManager()
    try:
        result = cart_manager.remove_from_cart(user_id=user_id, book_id=book_id)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
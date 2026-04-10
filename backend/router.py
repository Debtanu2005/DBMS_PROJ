from fastapi import APIRouter, Request, Depends, HTTPException, status
from authentication.register import RegisterManager
from authentication.login import LoginManager
from src.artifacts.entities import student, order_desc  # FIXED: Combined imports
from src.search_books.by_author_or_name import BookSearch
from src.cart.order import OrderManager
from src.cart.add_to_cart import CartManager
from authentication.jwt import verify_token 
from src.cart.view_cart import CartView
from src.cart.view_orders import ViewOrders
from src.base_model import LoginRequest

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
async def login_user(data: LoginRequest): # Change 'dict' to 'LoginRequest'
    login_manager = LoginManager()
    try:
        # data is now an object, access properties with dot notation
        token = login_manager.login(data.email, data.password)
        return {"access_token": token}
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
        return {"books": books}
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
async def execute_order(cart_id: int, order_info: dict, user_id: int = Depends(get_current_user)):
    order_manager = OrderManager()
    try:
        order_description = order_desc(**order_info)
        result = order_manager.execute_full_order(
            user_id=user_id,
            cart_id=cart_id,
            order_info=order_description
        )
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

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
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    password = password.encode("utf-8")[:72].decode("utf-8")  # ✅ FIX
    return pwd_context.hash(password)

def verify_password(plain, hashed):
    plain = plain.encode("utf-8")[:72].decode("utf-8")  # ✅ FIX
    return pwd_context.verify(plain, hashed)
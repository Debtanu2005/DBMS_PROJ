import bcrypt

def hash_password(password: str) -> str:
    truncated = password.encode("utf-8")[:72]
    return bcrypt.hashpw(truncated, bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    truncated = plain.encode("utf-8")[:72]
    return bcrypt.checkpw(truncated, hashed.encode("utf-8"))
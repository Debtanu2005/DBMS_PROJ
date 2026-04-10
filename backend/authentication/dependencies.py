from fastapi import Header, HTTPException
from authentication.jwt import verify_token


def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.split(" ")[1]
    payload = verify_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Token expired or invalid")

    return payload  # contains user_id, email, role


def student_only(authorization: str = Header(...)):
    user = get_current_user(authorization)

    if user.get("role") != "student":
        raise HTTPException(status_code=403, detail="Students only")

    return user
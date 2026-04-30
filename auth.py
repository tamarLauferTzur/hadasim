import secrets
from typing import Optional

from fastapi import Header, HTTPException

from models import User


def make_token():
    return secrets.token_hex(16)


async def get_current_teacher(authorization: Optional[str] = Header(None)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="missing token")
    token = authorization[len("Bearer "):]
    user = await User.find_one(User.token == token)
    if user is None:
        raise HTTPException(status_code=401, detail="invalid token")
    if user.role != "teacher":
        raise HTTPException(status_code=403, detail="teachers only")
    return user

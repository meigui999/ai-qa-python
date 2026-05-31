"""认证接口：注册 / 登录"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.core.security import hash_password, verify_password, create_token

router = APIRouter(prefix="/api/auth", tags=["认证"])


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    user = User(username=req.username, password=hash_password(req.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_token(user.id, user.username)
    return {"code": 200, "message": "注册成功", "data": {"token": token, "username": user.username}}


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.password):
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    token = create_token(user.id, user.username)
    return {"code": 200, "message": "登录成功", "data": {"token": token, "username": user.username}}

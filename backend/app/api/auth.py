import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.response import success
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models import User
from app.schemas.auth import AuthUser, LoginRequest, RegisterRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["认证管理"])


@router.post("/register", summary="用户注册", description="新用户注册账号，用户名需唯一")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.scalar(select(User).where(User.username == payload.username))
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(
        username=payload.username,
        password=hash_password(payload.password),
        real_name=payload.real_name,
        department=payload.department,
        email=payload.email,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("新用户注册: %s (id=%d)", user.username, user.id)
    return success(
        AuthUser(
            id=user.id,
            username=user.username,
            real_name=user.real_name,
            role=user.role,
            total_points=user.total_points,
        ).model_dump(),
        "注册成功",
    )


@router.post("/login", summary="用户登录", description="用户名密码登录，返回 JWT Token")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.username == payload.username))
    if not user or not verify_password(payload.password, user.password):
        logger.warning("登录失败: %s", payload.username)
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    token = create_access_token(str(user.id))
    logger.info("用户登录: %s (id=%d)", user.username, user.id)
    return success(
        {
            "access_token": token,
            "token_type": "bearer",
            "user": AuthUser(
                id=user.id,
                username=user.username,
                real_name=user.real_name,
                role=user.role,
                total_points=user.total_points,
            ).model_dump(),
        }
    )

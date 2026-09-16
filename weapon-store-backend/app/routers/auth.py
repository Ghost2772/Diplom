from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserResponse
from app.services.demo import create_demo_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/demo")
async def demo_config(response: Response):
    response.headers["Cache-Control"] = "no-store"
    return {
        "enabled": settings.DEMO_LOGIN_ENABLED,
        "session_minutes": settings.DEMO_SESSION_MINUTES,
    }


@router.post("/demo", response_model=Token)
async def demo_login(response: Response, db: AsyncSession = Depends(get_db)):
    if not settings.DEMO_LOGIN_ENABLED:
        raise HTTPException(status_code=404, detail="Демонстрационный вход отключён")

    user = await create_demo_user(db)
    response.headers["Cache-Control"] = "no-store"
    return {
        "access_token": create_access_token({"sub": user.email}, expires_at=user.demo_expires_at),
        "token_type": "bearer",
    }


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
        is_active=True,
        is_admin=False,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or user.is_demo:
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Учетная запись отключена")

    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}

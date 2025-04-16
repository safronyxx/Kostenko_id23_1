from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User
from app.services.auth import (
    get_current_user,
    create_access_token,
    authenticate_user
)
from app.schemas.user import UserResponse

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# АВТОРИЗАЦИЯ И ПОЛУЧ ИНФОРМАЦ О ТЕКУЩЕМ ПОЛЬЗОВАТЕЛЕ

@router.post("/token")
# получение токена по почте и паролю
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
# показывает данные текущ пользователя
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


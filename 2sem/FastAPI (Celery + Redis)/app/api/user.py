from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import services
from app.db.database import SessionLocal
from app.schemas.user import UserResponse, UserCreate


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# РЕГИСТРАЦИЯ НОВОГО ПОЛЬЗОВАТЕЛЯ
@router.post("/sign-up/", response_model=UserResponse)
def sign_up(user: UserCreate, db: Session = Depends(get_db)):
    return services.auth.register_user(db, user)


from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# ОПЕРАЦИИ НАД ПОЛЬЗОВАТЕЛЯМИ

# создание нового пользователя
def create_user(db: Session, user: UserCreate):
    db_user = User(email=user.email, password=user.password)
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user) # создает юзера
        return db_user
    except SQLAlchemyError as e:
        db.rollback() # иначе откатывает состояние бд
        return None

# получ нужного пользователя по его почте
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

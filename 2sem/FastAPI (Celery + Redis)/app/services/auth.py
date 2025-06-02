from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.core.settings import settings
from app.db.database import SessionLocal
from app.cruds.user import get_user_by_email, create_user
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

# АВТОРИЗАЦИЯ И РЕГИСТРАЦИЯ

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# токен
def create_access_token(data: dict):
    return jwt.encode(data, settings.secret_key, algorithm="HS256")

# проверка
def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email=email)
    if not user or not verify_password(password, user.password):
        return None
    return user

# регистрация
def register_user(db: Session, user: UserCreate) -> UserResponse:
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user.password = hash_password(user.password)

    created_user = create_user(db=db, user=user)
    if not created_user:
        raise HTTPException(status_code=500, detail="Failed to create user")

    return UserResponse(id=created_user.id, email=created_user.email)


# авторизация
def login_user(db: Session, email: str, password: str):
    user = authenticate_user(db, email, password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return create_access_token({"sub": str(user.id)})

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

# зависимость для получения пользователя по токену
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user

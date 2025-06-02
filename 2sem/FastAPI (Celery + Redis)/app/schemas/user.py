from pydantic_settings import BaseSettings

# ЮЗЕР СХЕМЫ
class UserBase(BaseSettings):
    email: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True

class Token(BaseSettings):
    access_token: str
    token_type: str
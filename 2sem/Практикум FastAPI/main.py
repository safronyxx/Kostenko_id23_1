from fastapi import FastAPI
from app.api import user, auth, crypto

app = FastAPI(
    title="FastAPI",
    description="ИД23-1 Костенко Мария",
    version="1.0.0"
)

app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(auth.router, tags=["Auth"])
app.include_router(crypto.router, prefix="/crypto", tags=["Crypto"])


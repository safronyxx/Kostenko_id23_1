from app.api import user, auth, crypto
from app.api.websocket import websocket_endpoint
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="FastAPI",
    description="ИД23-1 Костенко Мария",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# подключ роутеров
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(auth.router, tags=["Auth"])
app.include_router(crypto.router, prefix="/crypto", tags=["Crypto"])

# эндпоинт WebSocket
@app.websocket("/ws")
async def websocket_route(
    websocket: WebSocket,
    token: str = None
):
    await websocket_endpoint(websocket, token)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=1,
        loop="asyncio",
        timeout_keep_alive=5
    )
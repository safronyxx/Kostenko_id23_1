import asyncio
import json
import redis
from fastapi import WebSocket, WebSocketDisconnect, Depends
from collections import defaultdict

from fastapi.security import OAuth2PasswordBearer

from app.core.settings import settings
from jose import jwt, JWTError

from app.db.database import SessionLocal
from app.services.auth import get_current_user

active_connections = defaultdict(list)
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)


async def redis_listener(user_id: int, websocket: WebSocket):
    pubsub = redis_client.pubsub()
    channel = f"user:{user_id}:ws_notifications"
    pubsub.subscribe(channel)

    try:
        async for message in pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    await websocket.send_json(data)
                    print(f"Отправлено на WebSocket: {data}")
                except Exception as e:
                    print(f"Ошибка при обработке сообщения: {e}")
    except Exception as e:
        print(f"Ошибка прослушивания Redis: {e}")
    finally:
        pubsub.unsubscribe(channel)




oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

async def websocket_endpoint(websocket: WebSocket, token: str = Depends(oauth2_scheme)):
    try:
        await websocket.accept()
        db = SessionLocal()
        user = get_current_user(token=token, db=db)  # Извлекаем user_id из токена
        user_id = user.id

        active_connections[user_id].append(websocket)
        listener_task = asyncio.create_task(redis_listener(user_id, websocket))

        while True:
            try:
                await websocket.receive_text()
            except WebSocketDisconnect:
                break
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        listener_task.cancel()
        try:
            await listener_task
        except:
            pass
        if user_id in active_connections:
            active_connections[user_id].remove(websocket)
            if not active_connections[user_id]:
                del active_connections[user_id]
from celery import Celery
from fastapi import FastAPI
from app.core.settings import settings
import asyncio
from celery.signals import worker_shutdown
from celery import Celery
from app.core.settings import settings

# экземпл celery
celery_app = Celery(
    'app.tasks',
    broker=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0',
    backend=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0',
    broker_connection_retry_on_startup=True,
    include=['app.tasks.crypto_tasks']
)

# конфигур
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    broker_connection_retry=True,
    broker_connection_max_retries=100,
)


# уведы (доработать)
def notify_ws_task(user_id: int, message: dict):
    from app.api.websocket import active_connections
    import asyncio

    async def send_message(ws, msg):
        try:
            await ws.send_json(msg)
        except Exception as e:
            print(f"WebSocket error: {e}")

    connections = active_connections.get(user_id, [])

    if connections:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            tasks = [send_message(ws, message) for ws in connections]
            loop.run_until_complete(asyncio.gather(*tasks))
        finally:
            loop.close()

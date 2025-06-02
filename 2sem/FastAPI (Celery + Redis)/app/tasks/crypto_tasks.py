import redis
import json
from fastapi.encoders import jsonable_encoder
from app.celery_worker import celery_app
from app.core.settings import settings
from app.services.crypto import encode_text, decode_text
import asyncio

# инициализация Redis клиента
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)

async def send_ws_notification(user_id: int, message: dict):
    try:
        channel = f"user:{user_id}:ws_notifications"
        message_json = json.dumps({
            **message,
            "user_id": user_id
        })
        redis_client.publish(channel, message_json)
        print(f"Уведомление отправлено в {channel}: {message}")
    except Exception as e:
        print(f"Ошибка при получении уведомления: {e}")

def run_async_notification(user_id: int, message: dict):
    loop = asyncio.get_event_loop()
    loop.create_task(send_ws_notification(user_id, message))


# ЩИФРОВАНИЕ
@celery_app.task(bind=True)
def async_encode_task(self, user_id: int, text: str, key: str, task_id: str):
    try:
        run_async_notification(user_id, {
            "status": "STARTED",
            "task_id": task_id,
            "operation": "encode"
        })

        # кодирование
        result = encode_text(text, key)
        print(f"Encoding completed for task {task_id}")

        run_async_notification(user_id, {
            "status": "COMPLETED",
            "task_id": task_id,
            "operation": "encode",
            "result": jsonable_encoder(result)
        })

        return result
    except Exception as e:
        print(f"Encoding task failed: {str(e)}")
        run_async_notification(user_id, {
            "status": "FAILED",
            "task_id": task_id,
            "operation": "encode",
            "error": str(e)
        })
        raise


# ДЕШИФРОВАНИЕ
@celery_app.task(bind=True)
def async_decode_task(self, user_id: int, encoded_data: str, key: str,
                     huffman_codes: dict, padding: int, task_id: str):
    try:
        run_async_notification(user_id, {
            "status": "STARTED",
            "task_id": task_id,
            "operation": "decode"
        })

        # декодирование
        result = decode_text(
            encoded_data=encoded_data,
            key=key,
            huffman_codes=huffman_codes,
            padding=padding
        )
        print(f"Decoding completed for task {task_id}")

        run_async_notification(user_id, {
            "status": "COMPLETED",
            "task_id": task_id,
            "operation": "decode",
            "result": jsonable_encoder(result)
        })

        return result
    except Exception as e:
        print(f"Decoding task failed: {str(e)}")
        run_async_notification(user_id, {
            "status": "FAILED",
            "task_id": task_id,
            "operation": "decode",
            "error": str(e)
        })
        raise
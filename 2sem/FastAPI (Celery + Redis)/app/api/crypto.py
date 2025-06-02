from fastapi import APIRouter, Depends
from app.schemas.crypto import EncodeRequest, EncodeResponse, DecodeRequest, DecodeResponse
from app.services.crypto import encode_text, decode_text
from app.models.user import User
from app.services.auth import get_current_user
from app.tasks.crypto_tasks import async_encode_task, async_decode_task
import uuid
from app.services.auth import get_current_user
from celery.result import AsyncResult
from fastapi import HTTPException


router = APIRouter()

# РОУТЫ ШИФР И ДЕШИФР
@router.post("/encode", response_model=EncodeResponse)
def encode_data(
    payload: EncodeRequest,
    current_user: User = Depends(get_current_user)
):
    return encode_text(payload.text, payload.key)

@router.post("/decode", response_model=DecodeResponse)
def decode_data(
    payload: DecodeRequest,
    current_user: User = Depends(get_current_user)
):
    return decode_text(
        encoded_data=payload.encoded_data,
        key=payload.key,
        huffman_codes=payload.huffman_codes,
        padding=payload.padding
    )

# Асинхронные роуты
@router.post("/encode/async")
async def encode_async(
    payload: EncodeRequest,
    current_user: User = Depends(get_current_user)
):
    task_id = str(uuid.uuid4())
    async_encode_task.delay(
        user_id=current_user.id,
        text=payload.text,
        key=payload.key,
        task_id=task_id
    )
    return {"status": "submitted", "task_id": task_id}

@router.post("/decode/async")
async def decode_async(
    payload: DecodeRequest,
    current_user: User = Depends(get_current_user)
):
    task_id = str(uuid.uuid4())
    async_decode_task.delay(
        user_id=current_user.id,
        encoded_data=payload.encoded_data,
        key=payload.key,
        huffman_codes=payload.huffman_codes,
        padding=payload.padding,
        task_id=task_id
    )
    return {"status": "submitted", "task_id": task_id}


@router.get("/task/{task_id}")
async def get_task_result(task_id: str):
    task_result = AsyncResult(task_id)

    if not task_result.ready():
        return {"status": "PENDING"}

    if task_result.failed():
        return {"status": "FAILED", "error": str(task_result.result)}

    return {
        "status": "COMPLETED",
        "result": task_result.result
    }
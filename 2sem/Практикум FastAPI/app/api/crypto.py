from fastapi import APIRouter, Depends
from app.schemas.crypto import EncodeRequest, EncodeResponse, DecodeRequest, DecodeResponse
from app.services.crypto import encode_text, decode_text
from app.models.user import User
from app.services.auth import get_current_user

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

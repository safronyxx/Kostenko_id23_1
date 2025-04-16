from pydantic_settings import BaseSettings
from typing import Dict

# ШИФРОВАНИЕ СХЕМЫ

class EncodeRequest(BaseSettings):
    text: str
    key: str

# зашифрованные данные и параметры
class EncodeResponse(BaseSettings):
    encoded_data: str
    key: str
    huffman_codes: Dict[str, str]
    padding: int

# данные и параметры для расшифровки
class DecodeRequest(BaseSettings):
    encoded_data: str
    key: str
    huffman_codes: Dict[str, str]
    padding: int

# результат расшифровки
class DecodeResponse(BaseSettings):
    decoded_text: str

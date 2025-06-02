import asyncio
import websockets
import json
import requests

TOKEN = input("Введите токен: ")
BASE_URL = "http://localhost:8000"


async def listen_for_notifications(task_id: str):
    uri = f"ws://localhost:8000/ws?token={TOKEN}"
    try:
        async with websockets.connect(uri) as websocket:
            print("WebSocket подключен. Ожидание уведомлений...")
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    if data.get("task_id") == task_id:
                        print(f"Получено уведомление для задачи {task_id}: {data}")
                        if data.get("status") in ["COMPLETED", "FAILED"]:
                            print(f"Задача {task_id} завершена: {data}")
                            return data
                except websockets.exceptions.ConnectionClosed:
                    print("Соединение закрыто. Переподключение...")
                    await asyncio.sleep(1)
                    continue
    except Exception as e:
        print(f"Ошибка WebSocket: {e}")

async def create_task_and_listen(): # ТЕСТОВАЯ ЧАСТЬ
    response = requests.post(
        f"{BASE_URL}/crypto/encode/async",
        json={"text": "test message", "key": "123"},
        headers={"Authorization": f"Bearer {TOKEN}"}
    )
    task_data = response.json()
    task_id = task_data["task_id"]
    print(f"Создана задача с ID: {task_id}")
    result = await listen_for_notifications(task_id)
    print(f"Результат задачи: {result}")

if __name__ == "__main__":
    asyncio.run(create_task_and_listen())
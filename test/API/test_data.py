import random
import string
from datetime import datetime
from typing import Dict, Any


class TestData:
    """Класс для генерации тестовых данных"""

    @staticmethod
    def generate_pet_data(pet_id: int = None) -> Dict[str, Any]:
        """Сгенерировать данные питомца"""
        if pet_id is None:
            pet_id = random.randint(1000, 9999)

        return {
            "id": pet_id,
            "category": {
                "id": random.randint(1, 10),
                "name": random.choice(["dogs", "cats", "birds", "fish"])
            },
            "name": f"TestPet_{pet_id}",
            "photoUrls": [
                "http://example.com/photo1.jpg",
                "http://example.com/photo2.jpg"
            ],
            "tags": [
                {
                    "id": random.randint(1, 5),
                    "name": random.choice(["friendly", "playful", "quiet", "active"])
                }
            ],
            "status": random.choice(["available", "pending", "sold"])
        }

    @staticmethod
    def generate_order_data(order_id: int = None) -> Dict[str, Any]:
        """Сгенерировать данные заказа"""
        if order_id is None:
            order_id = random.randint(1, 10)

        return {
            "id": order_id,
            "petId": random.randint(1000, 9999),
            "quantity": random.randint(1, 5),
            "shipDate": datetime.now().isoformat() + "Z",
            "status": random.choice(["placed", "approved", "delivered"]),
            "complete": random.choice([True, False])
        }

    @staticmethod
    def generate_user_data(username: str = None) -> Dict[str, Any]:
        """Сгенерировать данные пользователя"""
        if username is None:
            username = f"testuser_{random.randint(1000, 9999)}"

        return {
            "id": random.randint(1000, 9999),
            "username": username,
            "firstName": f"First_{username}",
            "lastName": f"Last_{username}",
            "email": f"{username}@example.com",
            "password": "".join(random.choices(string.ascii_letters + string.digits, k=10)),
            "phone": f"+1{random.randint(100, 999)}{random.randint(100, 999)}{random.randint(1000, 9999)}",
            "userStatus": random.randint(0, 1)
        }
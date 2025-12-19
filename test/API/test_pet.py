import pytest
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class TestPetAPI:
    """Тесты для API питомцев"""

    @pytest.mark.smoke
    @pytest.mark.pet
    def test_create_pet(self, api_client, test_data, cleanup_pet):
        """Тест создания нового питомца"""
        logger.info("Test: Create new pet")

        # Подготовка данных
        pet_data = test_data.generate_pet_data()

        # Создание питомца
        response = api_client.post("/pet", data=pet_data)

        # Проверки
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        response_data = response.json()
        assert response_data["id"] == pet_data["id"]
        assert response_data["name"] == pet_data["name"]
        assert response_data["status"] == pet_data["status"]

        # Регистрируем для очистки
        cleanup_pet(pet_data["id"])

        logger.info(f"✓ Pet created successfully with ID: {pet_data['id']}")

    @pytest.mark.pet
    def test_get_pet_by_id(self, api_client, test_data, cleanup_pet):
        """Тест получения питомца по ID"""
        logger.info("Test: Get pet by ID")

        # Создаем питомца для теста
        pet_data = test_data.generate_pet_data()
        create_response = api_client.post("/pet", data=pet_data)
        cleanup_pet(pet_data["id"])

        # Получаем питомца
        response = api_client.get(f"/pet/{pet_data['id']}")

        # Проверки
        assert response.status_code == 200
        response_data = response.json()

        assert response_data["id"] == pet_data["id"]
        assert response_data["name"] == pet_data["name"]
        assert response_data["category"]["id"] == pet_data["category"]["id"]

        logger.info(f"✓ Pet retrieved successfully: {response_data['name']}")

    @pytest.mark.pet
    def test_update_pet(self, api_client, test_data, cleanup_pet):
        """Тест обновления питомца"""
        logger.info("Test: Update pet")

        # Создаем питомца
        pet_data = test_data.generate_pet_data()
        api_client.post("/pet", data=pet_data)
        cleanup_pet(pet_data["id"])

        # Обновляем данные
        updated_data = pet_data.copy()
        updated_data["name"] = "UpdatedName"
        updated_data["status"] = "sold"

        response = api_client.put("/pet", data=updated_data)

        # Проверки
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["name"] == "UpdatedName"
        assert response_data["status"] == "sold"

        logger.info("✓ Pet updated successfully")

    @pytest.mark.pet
    def test_delete_pet(self, api_client, test_data):
        """Тест удаления питомца"""
        logger.info("Test: Delete pet")

        # Создаем питомца для удаления
        pet_data = test_data.generate_pet_data()
        api_client.post("/pet", data=pet_data)

        # Удаляем питомца
        response = api_client.delete(f"/pet/{pet_data['id']}")

        # Проверки
        assert response.status_code == 200

        # Проверяем, что питомец действительно удален
        get_response = api_client.get(f"/pet/{pet_data['id']}")
        assert get_response.status_code == 404, "Pet should not exist after deletion"

        logger.info("✓ Pet deleted successfully")

    @pytest.mark.pet
    @pytest.mark.parametrize("status", ["available", "pending", "sold"])
    def test_find_pets_by_status(self, api_client, status):
        """Тест поиска питомцев по статусу"""
        logger.info(f"Test: Find pets by status '{status}'")

        response = api_client.get("/pet/findByStatus", params={"status": status})

        # Проверки
        assert response.status_code == 200

        pets = response.json()
        assert isinstance(pets, list)

        # Если есть питомцы, проверяем их статус
        if pets:
            for pet in pets:
                assert pet["status"] == status

        logger.info(f"✓ Found {len(pets)} pets with status '{status}'")

    @pytest.mark.pet
    def test_get_nonexistent_pet(self, api_client):
        """Тест получения несуществующего питомца"""
        logger.info("Test: Get non-existent pet")

        nonexistent_id = 999999999
        response = api_client.get(f"/pet/{nonexistent_id}")

        assert response.status_code == 404

        error_data = response.json()
        assert "message" in error_data
        assert "Pet not found" in error_data["message"]

        logger.info("✓ Correctly returned 404 for non-existent pet")

    @pytest.mark.regression
    @pytest.mark.pet
    def test_create_pet_invalid_data(self, api_client):
        """Тест создания питомца с невалидными данными"""
        logger.info("Test: Create pet with invalid data")

        invalid_data = {
            "id": "invalid_id",  # Строка вместо числа
            "name": 123,  # Число вместо строки
            "status": "invalid_status"  # Невалидный статус
        }

        response = api_client.post("/pet", data=invalid_data)

        # Petstore может вернуть 400 или 500 на невалидные данные
        assert response.status_code in [400, 405, 500]

        logger.info(f"✓ Correctly rejected invalid data with status {response.status_code}")
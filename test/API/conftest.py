import pytest
import logging
from utils.api_client import PetStoreAPIClient
from data.test_data import TestData

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@pytest.fixture(scope="session")
def api_client():
    """Фикстура API клиента"""
    return PetStoreAPIClient()


@pytest.fixture(scope="session")
def test_data():
    """Фикстура тестовых данных"""
    return TestData()


@pytest.fixture
def cleanup_pet(api_client):
    """Фикстура для очистки созданных питомцев"""
    created_pets = []

    def _add_pet(pet_id: int):
        created_pets.append(pet_id)

    yield _add_pet

    # После теста удаляем созданных питомцев
    for pet_id in created_pets:
        try:
            api_client.delete(f"/pet/{pet_id}")
        except:
            pass  # Игнорируем ошибки при удалении
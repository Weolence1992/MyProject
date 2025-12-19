import pytest
import logging
import time

logger = logging.getLogger(__name__)


class TestStoreAPI:
    """Тесты для API магазина"""

    @pytest.mark.smoke
    @pytest.mark.store
    def test_create_order(self, api_client, test_data):
        """Тест создания заказа"""
        logger.info("Test: Create order")

        order_data = test_data.generate_order_data()

        response = api_client.post("/store/order", data=order_data)

        # Проверки
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["id"] == order_data["id"]
        assert response_data["petId"] == order_data["petId"]
        assert response_data["quantity"] == order_data["quantity"]
        assert response_data["status"] == order_data["status"]

        logger.info(f"✓ Order created successfully with ID: {order_data['id']}")

    @pytest.mark.store
    def test_get_order_by_id(self, api_client, test_data):
        """Тест получения заказа по ID"""
        logger.info("Test: Get order by ID")

        # Создаем заказ для теста
        order_data = test_data.generate_order_data(order_id=5)  # Используем ID 1-10
        api_client.post("/store/order", data=order_data)

        # Получаем заказ
        response = api_client.get(f"/store/order/{order_data['id']}")

        # Проверки
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["id"] == order_data["id"]
        assert response_data["status"] == order_data["status"]

        logger.info(f"✓ Order retrieved successfully: ID {order_data['id']}")

    @pytest.mark.store
    def test_delete_order(self, api_client, test_data):
        """Тест удаления заказа"""
        logger.info("Test: Delete order")

        # Создаем заказ для удаления
        order_data = test_data.generate_order_data(order_id=3)
        api_client.post("/store/order", data=order_data)

        # Удаляем заказ
        response = api_client.delete(f"/store/order/{order_data['id']}")

        # Проверки
        assert response.status_code == 200

        # Проверяем, что заказ удален
        get_response = api_client.get(f"/store/order/{order_data['id']}")
        assert get_response.status_code == 404

        logger.info("✓ Order deleted successfully")

    @pytest.mark.store
    def test_get_inventory(self, api_client):
        """Тест получения инвентаря"""
        logger.info("Test: Get inventory")

        response = api_client.get("/store/inventory")

        # Проверки
        assert response.status_code == 200

        inventory = response.json()
        assert isinstance(inventory, dict)

        # Проверяем структуру инвентаря
        for status, count in inventory.items():
            assert isinstance(status, str)
            assert isinstance(count, int)
            assert count >= 0

        logger.info(f"✓ Inventory retrieved: {len(inventory)} status types")

    @pytest.mark.regression
    @pytest.mark.store
    @pytest.mark.parametrize("order_id", [0, 11, -1, "invalid"])
    def test_get_invalid_order(self, api_client, order_id):
        """Тест получения невалидного заказа"""
        logger.info(f"Test: Get invalid order ID: {order_id}")

        response = api_client.get(f"/store/order/{order_id}")

        # Должен вернуть 400 для невалидного ID или 404 для валидного но несуществующего
        assert response.status_code in [400, 404]

        logger.info(f"✓ Correctly handled invalid order ID with status {response.status_code}")
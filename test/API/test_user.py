import pytest
import logging

logger = logging.getLogger(__name__)


class TestUserAPI:
    """Тесты для API пользователей"""

    @pytest.mark.smoke
    @pytest.mark.user
    def test_create_user(self, api_client, test_data):
        """Тест создания пользователя"""
        logger.info("Test: Create user")

        user_data = test_data.generate_user_data()

        response = api_client.post("/user", data=user_data)

        # Проверки
        assert response.status_code == 200

        response_data = response.json()
        assert "message" in response_data
        assert str(user_data["id"]) in response_data["message"]

        logger.info(f"✓ User created: {user_data['username']}")

    @pytest.mark.user
    def test_get_user_by_username(self, api_client, test_data):
        """Тест получения пользователя по имени"""
        logger.info("Test: Get user by username")

        # Создаем пользователя
        user_data = test_data.generate_user_data(username="testuser123")
        api_client.post("/user", data=user_data)

        # Получаем пользователя
        response = api_client.get(f"/user/{user_data['username']}")

        # Проверки
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["username"] == user_data["username"]
        assert response_data["email"] == user_data["email"]

        logger.info(f"✓ User retrieved: {user_data['username']}")

    @pytest.mark.user
    def test_update_user(self, api_client, test_data):
        """Тест обновления пользователя"""
        logger.info("Test: Update user")

        # Создаем пользователя
        user_data = test_data.generate_user_data(username="updatetest")
        api_client.post("/user", data=user_data)

        # Обновляем данные
        updated_data = user_data.copy()
        updated_data["email"] = "updated@example.com"
        updated_data["phone"] = "+1234567890"

        response = api_client.put(f"/user/{user_data['username']}", data=updated_data)

        # Проверки
        assert response.status_code == 200

        # Проверяем обновление
        get_response = api_client.get(f"/user/{user_data['username']}")
        updated_user = get_response.json()

        assert updated_user["email"] == "updated@example.com"
        assert updated_user["phone"] == "+1234567890"

        logger.info("✓ User updated successfully")

    @pytest.mark.user
    def test_delete_user(self, api_client, test_data):
        """Тест удаления пользователя"""
        logger.info("Test: Delete user")

        # Создаем пользователя для удаления
        user_data = test_data.generate_user_data(username="deletetest")
        api_client.post("/user", data=user_data)

        # Удаляем пользователя
        response = api_client.delete(f"/user/{user_data['username']}")

        # Проверки
        assert response.status_code == 200

        # Проверяем, что пользователь удален
        get_response = api_client.get(f"/user/{user_data['username']}")
        assert get_response.status_code == 404

        logger.info("✓ User deleted successfully")

    @pytest.mark.user
    def test_user_login(self, api_client, test_data):
        """Тест входа пользователя"""
        logger.info("Test: User login")

        # Создаем пользователя с известными учетными данными
        username = "loginuser"
        password = "testpass123"

        user_data = test_data.generate_user_data(username=username)
        user_data["password"] = password

        api_client.post("/user", data=user_data)

        # Пытаемся войти
        response = api_client.get("/user/login",
                                  params={"username": username, "password": password})

        # Проверки
        assert response.status_code == 200

        response_data = response.json()
        assert "message" in response_data
        assert "logged in" in response_data["message"].lower()

        # Проверяем наличие cookie/session
        assert "X-Expires-After" in response.headers or "X-Rate-Limit" in response.headers

        logger.info("✓ User logged in successfully")

    @pytest.mark.user
    def test_user_logout(self, api_client):
        """Тест выхода пользователя"""
        logger.info("Test: User logout")

        response = api_client.get("/user/logout")

        # Проверки
        assert response.status_code == 200

        response_data = response.json()
        assert "message" in response_data
        assert "ok" in response_data["message"].lower()

        logger.info("✓ User logged out successfully")

    @pytest.mark.regression
    @pytest.mark.user
    def test_create_users_with_array(self, api_client, test_data):
        """Тест создания нескольких пользователей"""
        logger.info("Test: Create users with array")

        users = [
            test_data.generate_user_data(username=f"arrayuser_{i}")
            for i in range(3)
        ]

        response = api_client.post("/user/createWithArray", data=users)

        # Проверки
        assert response.status_code == 200

        response_data = response.json()
        assert "message" in response_data

        logger.info("✓ Users created with array")
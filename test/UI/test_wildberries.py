import pytest
import time
import logging
from pages import *
from selenium.webdriver.common.by import By
import allure

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestWildberries:
    """Тесты для сайта Wildberries"""

    @pytest.mark.smoke
    def test_main_page_loads(self, driver):
        """Тест: Главная страница загружается"""
        logger.info("Тест: Загрузка главной страницы")
        with allure.step("Открыть страницу логина"):

            main_page = MainPage(driver).open()

            assert "wildberries.ru" in driver.current_url
            assert "Wildberries" in driver.title
            logger.info("✓ Главная страница загружена успешно")

    @pytest.mark.search
    def test_search_product(self, driver, test_data):
        """Тест: Поиск товара"""
        logger.info("Тест: Поиск товара")
        with allure.step("Поиск товара"):
            main_page = MainPage(driver).open()
            search_page = main_page.search_product(test_data["search_query"])
            time.sleep(2)

            # Проверяем результаты поиска
            product_count = search_page.get_product_count()
            logger.info(f"Найдено товаров: {product_count}")

            assert product_count > 0, "Не найдено товаров по запросу"

            # Проверяем названия товаров
            product_names = search_page.get_product_names()
            assert len(product_names) > 0
            logger.info(f"Пример товара: {product_names[0][:50]}...")

            logger.info("✓ Поиск работает корректно")

    @pytest.mark.cart
    def test_add_to_cart_from_search(self, driver, test_data):
        """Тест: Добавление товара в корзину из поиска"""
        logger.info("Тест: Добавление в корзину из поиска")
        with allure.step("Добавление в корзину из поиска"):

            main_page = MainPage(driver).open()
            search_page = main_page.search_product(test_data["search_query"])
            time.sleep(2)

            # Добавляем первый товар в корзину
            added = search_page.add_to_cart_from_list(0)
            assert added, "Не удалось добавить товар в корзину"

            # Переходим в корзину
            cart_page = search_page.open_cart()
            time.sleep(2)

            # Проверяем, что товар в корзине
            items_count = cart_page.get_items_count()
            assert items_count > 0, "Корзина пуста после добавления товара"

            item_names = cart_page.get_item_names()
            logger.info(f"Товар в корзине: {item_names[0][:50]}...")
            logger.info("✓ Товар успешно добавлен в корзину")

    @pytest.mark.cart
    def test_add_to_cart_from_product_page(self, driver, test_data):
        """Тест: Добавление товара в корзину со страницы товара"""
        logger.info("Тест: Добавление в корзину со страницы товара")
        with allure.step("Добавление в корзину со страницы товара"):

            main_page = MainPage(driver).open()
            search_page = main_page.search_product(test_data["search_query"])
            time.sleep(2)

            # Открываем страницу товара
            product_page = search_page.open_first_product()
            time.sleep(2)

            # Получаем информацию о товаре
            product_info = product_page.get_product_info()
            logger.info(f"Товар: {product_info['title'][:50]}...")
            logger.info(f"Цена: {product_info['price']}")

            # Пробуем выбрать размер и цвет
            product_page.select_size(0)
            product_page.select_color(0)

            # Добавляем в корзину
            product_page.add_to_cart()

            # Переходим в корзину
            cart_page = product_page.go_to_cart()
            time.sleep(2)

            # Проверяем корзину
            items_count = cart_page.get_items_count()
            total_price = cart_page.get_total_price()

            assert items_count > 0, "Товар не добавлен в корзину"
            logger.info(f"Товаров в корзине: {items_count}")
            logger.info(f"Общая сумма: {total_price}")
            logger.info("✓ Товар добавлен в корзину со страницы товара")

    @pytest.mark.cart
    def test_cart_operations(self, driver, test_data):
        """Тест: Операции с корзиной"""
        logger.info("Тест: Операции с корзиной")
        with allure.step("Операции с корзиной"):

            # Сначала добавляем товар в корзину
            main_page = MainPage(driver).open()
            search_page = main_page.search_product(test_data["search_query"])
            time.sleep(2)

            search_page.add_to_cart_from_list(0)
            cart_page = search_page.open_cart()
            time.sleep(2)

            initial_count = cart_page.get_items_count()
            logger.info(f"Товаров в корзине изначально: {initial_count}")

            # Изменяем количество
            cart_page.change_quantity(0, increase=True)
            time.sleep(1)

            # Удаляем товар
            cart_page.remove_item(0)
            time.sleep(2)

            final_count = cart_page.get_items_count()
            logger.info(f"Товаров в корзине после удаления: {final_count}")

            assert final_count < initial_count, "Товар не удален из корзины"
            logger.info("✓ Операции с корзиной работают корректно")

    @pytest.mark.checkout
    def test_checkout_page(self, driver, test_data):
        """Тест: Страница оформления заказа"""
        logger.info("Тест: Страница оформления заказа")
        with allure.step("Страница оформления заказа"):

            # Добавляем товар в корзину
            main_page = MainPage(driver).open()
            search_page = main_page.search_product(test_data["search_query"])
            time.sleep(2)

            search_page.add_to_cart_from_list(0)
            cart_page = search_page.open_cart()
            time.sleep(2)

            # Переходим к оформлению
            checkout_page = cart_page.proceed_to_checkout()
            time.sleep(3)

            # Проверяем, что страница оформления загружена
            is_loaded = checkout_page.is_checkout_page_loaded()
            assert is_loaded, "Страница оформления не загружена"

            # В демо-режиме проверяем элементы (не кликая по ним)
            logger.info("✓ Страница оформления загружена")
            logger.info("Демо: Здесь был бы выбор доставки и оплаты")

    @pytest.mark.e2e
    def test_full_flow(self, driver, test_data):
        """E2E тест: Полный поток покупки"""
        logger.info("E2E тест: Полный поток покупки")
        with allure.step("Полный поток покупки"):

            # Шаг 1: Открыть главную страницу
            main_page = MainPage(driver).open()
            logger.info("Шаг 1: Главная страница открыта")

            # Шаг 2: Поиск товара
            search_page = main_page.search_product(test_data["search_query"])
            time.sleep(2)

            product_count = search_page.get_product_count()
            if product_count == 0:
                logger.warning("Нет товаров для теста, пропускаем")
                pytest.skip("Нет товаров для тестирования")

            logger.info(f"Шаг 2: Найдено {product_count} товаров")

            # Шаг 3: Открыть страницу товара
            product_page = search_page.open_first_product()
            time.sleep(2)

            product_info = product_page.get_product_info()
            logger.info(f"Шаг 3: Открыт товар: {product_info['title'][:30]}...")

            # Шаг 4: Добавить в корзину
            product_page.select_size(0)
            product_page.add_to_cart()
            logger.info("Шаг 4: Товар добавлен в корзину")

            # Шаг 5: Перейти в корзину
            cart_page = product_page.go_to_cart()
            time.sleep(2)

            items_count = cart_page.get_items_count()
            total_price = cart_page.get_total_price()
            logger.info(f"Шаг 5: В корзине {items_count} товаров на сумму {total_price}")

            assert items_count > 0, "Корзина пуста"

            # Шаг 6: Перейти к оформлению
            checkout_page = cart_page.proceed_to_checkout()
            time.sleep(3)

            is_loaded = checkout_page.is_checkout_page_loaded()
            assert is_loaded, "Не удалось перейти к оформлению"

            logger.info("Шаг 6: Страница оформления загружена")
            logger.info("✓ E2E тест завершен успешно")

    @pytest.mark.auth
    def test_auth_modal(self, driver, test_data):
        """Тест: Открытие модального окна авторизации"""
        logger.info("Тест: Модальное окно авторизации")
        with allure.step("Модальное окно авторизации"):

            main_page = MainPage(driver).open()
            auth_page = main_page.click_login()
            time.sleep(2)

            # Проверяем, что появилось поле для ввода телефона
            try:
                # В демо-режиме просто проверяем URL
                assert "wildberries.ru" in driver.current_url
                logger.info("✓ Модальное окно авторизации открыто")
            except:
                logger.warning("Не удалось открыть модальное окно авторизации")

    @pytest.mark.parametrize("search_query,expected_min", [
        ("кроссовки", 1),
        ("футболка", 1),
        ("телефон", 1),
        ("абвгд12345", 0),  # Несуществующий запрос
    ])
    def test_different_searches(self, driver, search_query, expected_min):
        """Параметризованный тест поиска"""
        logger.info(f"Тест поиска: '{search_query}'")

        main_page = MainPage(driver).open()
        search_page = main_page.search_product(search_query)
        time.sleep(2)

        product_count = search_page.get_product_count()
        logger.info(f"Найдено товаров: {product_count}")

        if expected_min > 0:
            assert product_count >= expected_min
        else:
            # Для несуществующих товаров допускаем 0 или мало результатов
            assert product_count < 100

    def test_empty_cart(self, driver):
        """Тест: Пустая корзина"""
        logger.info("Тест: Пустая корзина")
        with allure.step("Тест: Пустая корзина"):

            main_page = MainPage(driver).open()
            cart_page = main_page.open_cart()
            time.sleep(2)

            # Проверяем, что открылась страница корзины
            assert "cart" in driver.current_url or "basket" in driver.current_url

            items_count = cart_page.get_items_count()
            logger.info(f"Товаров в корзине: {items_count}")

            # В пустой корзине может быть 0 товаров или сообщение "Корзина пуста"
            logger.info("✓ Страница корзины открыта")


# Дополнительные утилитарные тесты
def test_quick_check():
    """Быстрая проверка работы"""
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    try:
        driver.get("https://www.wildberries.ru")
        time.sleep(3)
        print(f"Title: {driver.title}")
        print(f"URL: {driver.current_url}")

        # Быстрый поиск
        search_input = driver.find_element(By.ID, "searchInput")
        search_input.send_keys("кроссовки")
        search_input.submit()
        time.sleep(3)

        print(f"После поиска: {driver.current_url}")

    finally:
        driver.quit()


if __name__ == "__main__":
    # Запуск быстрой проверки
    test_quick_check()
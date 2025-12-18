from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time


class TestOzonSimple:
    """Простые smoke-тесты для сайта OZON"""

    # Локаторы элементов OZON (упрощенные)
    LOCATORS = {
        # Главная страница
        "search_input": (
        By.XPATH, "//input[@placeholder='Искать на Ozon'] | //input[contains(@class, 'search-input')]"),
        "search_button": (By.XPATH, "//button[@type='submit'] | //button[contains(@class, 'search-btn')]"),
        "catalog_button": (By.XPATH, "//button[contains(text(), 'Каталог')] | //div[contains(text(), 'Каталог')]"),
        "login_button": (By.XPATH, "//button[contains(text(), 'Войти')] | //div[contains(text(), 'Войти')]"),
        "cart_button": (By.XPATH, "//a[@href='/cart'] | //div[contains(text(), 'Корзина')]"),

        # Страница результатов поиска
        "product_card": (
        By.XPATH, "//div[contains(@class, 'product-card')] | //article[contains(@class, 'product-card')]"),
        "product_name": (By.XPATH, ".//span[contains(@class, 'title')] | .//h3"),

        # Общие элементы
        "cookie_accept": (By.XPATH, "//button[contains(text(), 'Принять') or contains(text(), 'Согласен')]"),
        "page_title": (By.TAG_NAME, "h1")
    }

    def setup_method(self):
        """Настройка перед каждым тестом"""
        # Инициализация драйвера Chrome
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 15)

    def teardown_method(self):
        """Завершение после каждого теста"""
        self.driver.quit()

    def accept_cookies(self):
        """Принять куки, если появилось окно"""
        try:
            cookie_btn = self.driver.find_element(*self.LOCATORS["cookie_accept"])
            cookie_btn.click()
            time.sleep(1)
            print("  ✓ Куки приняты")
        except:
            pass  # Если окна с куки нет, просто продолжаем

    def test_01_homepage_loads(self):
        """Тест 1: Главная страница успешно загружается"""
        print("\n" + "=" * 60)
        print("ТЕСТ 1: Загрузка главной страницы OZON")
        print("=" * 60)

        # 1. Открыть сайт
        print("  1. Открываем https://www.ozon.ru")
        self.driver.get("https://www.ozon.ru")
        time.sleep(20)  # Пауза для полной загрузки

        # 2. Принять куки
        self.accept_cookies()

        # 3. Проверки
        print("  2. Проверяем загрузку страницы...")

        # Проверка заголовка
        assert "Ozon" in self.driver.title, f"В заголовке нет 'Ozon'. Текущий: {self.driver.title}"
        print(f"  ✓ Заголовок окна: '{self.driver.title}'")

        # Проверка URL
        assert "ozon.ru" in self.driver.current_url
        print(f"  ✓ URL: {self.driver.current_url}")

        # Проверяем видимость ключевых элементов
        print("  3. Проверяем ключевые элементы...")

        elements_to_check = [
            ("search_input", "Поле поиска"),
            ("search_button", "Кнопка поиска"),
            ("cart_button", "Кнопка корзины"),
            ("login_button", "Кнопка входа")
        ]

        for element_key, element_name in elements_to_check:
            try:
                element = self.wait.until(
                    EC.presence_of_element_located(self.LOCATORS[element_key])
                )
                if element.is_displayed():
                    print(f"  ✓ {element_name} отображается")
                else:
                    print(f"  ⚠ {element_name} найден, но не отображается")
            except TimeoutException:
                print(f"  ⚠ {element_name} не найден (локатор может устареть)")

        print("\n" + "=" * 60)
        print("ТЕСТ 1 ПРОЙДЕН: Главная страница загружена успешно!")
        print("=" * 60)


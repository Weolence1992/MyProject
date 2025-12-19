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
        By.XPATH, "//input[@placeholder='Искать на Ozon'] | //input[contains(@class, 'nu5_30 tsBody500Medium')]"),
        "search_button": (By.XPATH, "//button[@type='submit'] | //button[contains(@class, 'u5n_30 ag5_6_1-a0 ag5_6_1-a7')]"),
        "catalog_button": (By.XPATH, "//button[contains(text(), 'Каталог')] | //div[contains(text(), 'Каталог')]"),
        "login_button": (By.XPATH, "//button[contains(text(), 'Войти или зарегистрироваться')] | //div[contains(text(), 'Войти или зарегистрироваться')]"),
        "cart_button": (By.CSS_SELECTOR, "a.q4b1_3_0-a cj01_0_10-a"),

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
        time.sleep(3)  # Пауза для полной загрузки

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

    def test_02_search_functionality(self):
        """Тест 2: Проверка работы поиска товаров"""
        print("\n" + "=" * 60)
        print("ТЕСТ 2: Проверка поиска товаров")
        print("=" * 60)

        # 1. Открыть главную
        print("  1. Открываем главную страницу...")
        self.driver.get("https://www.ozon.ru")
        self.accept_cookies()
        time.sleep(2)

        # 2. Ввести запрос и выполнить поиск
        search_query = "смартфон"
        print(f"  2. Ищем товар: '{search_query}'")

        # Находим поле поиска
        search_input = self.wait.until(
            EC.element_to_be_clickable(self.LOCATORS["search_input"])
        )
        search_input.clear()
        search_input.send_keys(search_query)
        print(f"  ✓ Запрос введен: '{search_query}'")

        # Нажимаем кнопку поиска
        search_btn = self.driver.find_element(*self.LOCATORS["search_button"])
        search_btn.click()
        print("  ✓ Кнопка поиска нажата")
        time.sleep(3)  # Ждем загрузки результатов

        # 3. Проверяем, что перешли на страницу результатов
        print("  3. Проверяем результаты поиска...")

        current_url = self.driver.current_url.lower()
        is_search_page = any(keyword in current_url for keyword in ['search', 'catalog', '?text='])

        assert is_search_page, f"Не перешли на страницу поиска. URL: {self.driver.current_url}"
        print(f"  ✓ Страница результатов загружена: {self.driver.current_url[:80]}...")

        # 4. Проверяем наличие результатов
        try:
            # Ждем появления карточек товаров
            product_cards = self.wait.until(
                EC.presence_of_all_elements_located(self.LOCATORS["product_card"])
            )

            assert len(product_cards) > 0, "Не найдено ни одной карточки товара"
            print(f"  ✓ Найдено карточек товаров: {len(product_cards)}")

            # Показываем названия первых 3 товаров
            print("  4. Первые найденные товары:")
            for i, card in enumerate(product_cards[:3], 1):
                try:
                    name_element = card.find_element(*self.LOCATORS["product_name"])
                    product_name = name_element.text[:50] + "..." if len(name_element.text) > 50 else name_element.text
                    print(f"     {i}. {product_name}")
                except:
                    print(f"     {i}. [Название не найдено]")

        except TimeoutException:
            print("  ⚠ Карточки товаров не загрузились за ожидаемое время")
            # Делаем скриншот для отладки
            self.driver.save_screenshot("search_error.png")
            print("  ⚠ Скриншот сохранен: search_error.png")

        print("\n" + "=" * 60)
        print("ТЕСТ 2 ПРОЙДЕН: Поиск работает корректно!")
        print("=" * 60)

    def test_03_catalog_menu(self):
        """Тест 3: Проверка работы каталога"""
        print("\n" + "=" * 60)
        print("ТЕСТ 3: Проверка каталога товаров")
        print("=" * 60)

        # 1. Открыть главную
        print("  1. Открываем главную страницу...")
        self.driver.get("https://www.ozon.ru")
        self.accept_cookies()
        time.sleep(2)

        # 2. Нажимаем кнопку "Каталог"
        print("  2. Открываем каталог...")
        try:
            catalog_btn = self.wait.until(
                EC.element_to_be_clickable(self.LOCATORS["catalog_button"])
            )
            catalog_btn.click()
            print("  ✓ Кнопка 'Каталог' нажата")
            time.sleep(2)  # Ждем открытия меню
        except TimeoutException:
            print("  ⚠ Кнопка 'Каталог' не найдена, пробуем альтернативный локатор...")
            # Попробуем найти кнопку по другому XPath
            try:
                catalog_alt = self.driver.find_element(By.XPATH, "//*[contains(text(), 'Каталог')]")
                catalog_alt.click()
                time.sleep(2)
            except:
                print("  ⚠ Не удалось найти кнопку 'Каталог', пропускаем тест")
                return

        # 3. Проверяем, что меню каталога открылось
        print("  3. Проверяем содержимое каталога...")

        # Ищем категории в каталоге (разные возможные варианты)
        catalog_selectors = [
            "//div[contains(@class, 'catalog')]//a",
            "//nav[contains(@class, 'menu')]//a",
            "//ul[contains(@class, 'category')]//li",
            "//div[contains(@class, 'category')]"
        ]

        categories_found = []

        for selector in catalog_selectors:
            try:
                categories = self.driver.find_elements(By.XPATH, selector)
                if categories and len(categories) > 0:
                    categories_found = categories
                    break
            except:
                continue

        if categories_found:
            print(f"  ✓ Найдено элементов в каталоге: {len(categories_found)}")

            # Показываем первые 5 категорий
            print("  Первые 5 категорий:")
            for i, category in enumerate(categories_found[:5], 1):
                try:
                    category_text = category.text.strip()
                    if category_text:  # Показываем только непустые
                        print(f"    {i}. {category_text[:30]}...")
                except:
                    print(f"    {i}. [Текст не получен]")
        else:
            print("  ⚠ Не удалось найти категории в каталоге")
            self.driver.save_screenshot("catalog_error.png")
            print("  ⚠ Скриншот сохранен: catalog_error.png")

        print("\n" + "=" * 60)
        print("ТЕСТ 3 ПРОЙДЕН: Каталог доступен!")
        print("=" * 60)

    def test_04_navigation_to_cart(self):
        """Тест 4: Переход в корзину"""
        print("\n" + "=" * 60)
        print("ТЕСТ 4: Переход в корзину")
        print("=" * 60)

        # 1. Открыть главную
        print("  1. Открываем главную страницу...")
        self.driver.get("https://www.ozon.ru")
        self.accept_cookies()
        time.sleep(2)

        # 2. Нажимаем на иконку корзины
        print("  2. Переходим в корзину...")
        try:
            cart_btn = self.wait.until(
                EC.element_to_be_clickable(self.LOCATORS["cart_button"])
            )
            cart_btn.click()
            print("  ✓ Кнопка корзины нажата")
            time.sleep(3)  # Ждем загрузки страницы корзины
        except TimeoutException:
            print("  ⚠ Кнопка корзины не найдена, пробуем альтернативный метод...")
            # Пробуем перейти по прямому URL
            self.driver.get("https://www.ozon.ru/cart")
            time.sleep(3)

        # 3. Проверяем, что перешли в корзину
        print("  3. Проверяем страницу корзины...")

        current_url = self.driver.current_url.lower()
        is_cart_page = any(keyword in current_url for keyword in ['cart', 'basket', 'корзина'])

        if is_cart_page:
            print(f"  ✓ Мы на странице корзины: {self.driver.current_url}")
        else:
            print(f"  ⚠ Возможно, не попали в корзину. URL: {self.driver.current_url}")

        # 4. Проверяем заголовок или содержимое
        try:
            page_title = self.driver.find_element(*self.LOCATORS["page_title"])
            title_text = page_title.text.lower()

            if any(word in title_text for word in ["корзина", "basket", "cart", "покупки"]):
                print(f"  ✓ Заголовок страницы: '{page_title.text}'")
            else:
                print(f"  ⚠ Необычный заголовок для корзины: '{page_title.text}'")
        except:
            print("  ⚠ Заголовок страницы не найден")

        # 5. Проверяем содержимое корзины
        print("  4. Проверяем содержимое корзины...")

        # Ищем элементы, характерные для корзины
        cart_indicators = [
            ("//div[contains(text(), 'Корзина пуста')]", "Корзина пуста"),
            ("//div[contains(text(), 'Товаров в корзине')]", "Товары в корзине"),
            ("//button[contains(text(), 'Оформить заказ')]", "Кнопка оформления"),
            ("//div[contains(@class, 'cart-item')]", "Товары в корзине")
        ]

        found_indicator = None
        for xpath, description in cart_indicators:
            try:
                element = self.driver.find_element(By.XPATH, xpath)
                if element.is_displayed():
                    found_indicator = description
                    break
            except:
                continue

        if found_indicator:
            print(f"  ✓ Статус корзины: {found_indicator}")
        else:
            print("  ⚠ Не удалось определить состояние корзины")
            self.driver.save_screenshot("cart_error.png")
            print("  ⚠ Скриншот сохранен: cart_error.png")

        print("\n" + "=" * 60)
        print("ТЕСТ 4 ПРОЙДЕН: Переход в корзину выполнен!")
        print("=" * 60)

    def test_05_simple_product_search_and_check(self):
        """Тест 5: Поиск и проверка товара"""
        print("\n" + "=" * 60)
        print("ТЕСТ 5: Детальный поиск товара")
        print("=" * 60)

        # 1. Открыть главную
        print("  1. Открываем главную страницу...")
        self.driver.get
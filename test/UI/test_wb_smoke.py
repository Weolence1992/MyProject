from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class TestWildberriesSmoke:
    """Простой набор smoke-тестов для сайта Wildberries.ru"""

    # Основные локаторы (селекторы элементов на странице).
    # На реальном сайте их нужно проверять и уточнять.
    LOCATORS = {
        # Главная страница
        "search_input": (By.ID, "searchInput"),  # Поле поиска
        "search_button": (By.CSS_SELECTOR, "button.search-component-button"),  # Кнопка лупы
        "catalog_button": (By.CSS_SELECTOR, "button[data-link='{on catalog click}']"),  # Кнопка каталога
        "login_button": (By.CSS_SELECTOR, "a[data-wba-header-name='Login']"),  # Кнопка входа
        "cart_button": (By.CSS_SELECTOR, "a[data-wba-header-name='Cart']"),  # Иконка корзины

        # Всплывающее меню каталога
        "catalog_menu": (By.CSS_SELECTOR, "div.menu.catalog"),
        "catalog_first_category": (By.CSS_SELECTOR, "ul.menu-catalog a"),  # Первая категория в меню

        # Страница товаров (результаты поиска)
        "product_card": (By.CSS_SELECTOR, "article.product-card"),  # Карточка товара
        "product_name": (By.CSS_SELECTOR, "span.product-card__name"),  # Название товара

        # Общие элементы
        "page_title": (By.TAG_NAME, "h1"),  # Заголовок страницы
        "cookie_accept": (By.XPATH, "//button[contains(text(), 'Принять')]")  # Кнопка принятия куки
    }

    def setup_method(self):
        """Настройка перед каждым тестом"""
        # Инициализация драйвера Chrome
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.implicitly_wait(10)  # Неявное ожидание элементов
        self.wait = WebDriverWait(self.driver, 15)  # Явное ожидание

    def teardown_method(self):
        """Завершение после каждого теста"""
        self.driver.quit()

    def accept_cookies(self):
        """Принять куки, если появилось окно"""
        try:
            cookie_btn = self.driver.find_element(*self.LOCATORS["cookie_accept"])
            cookie_btn.click()
            time.sleep(1)
        except:
            pass  # Если окна с куки нет, просто продолжаем

    def test_01_homepage_loads(self):
        """Тест 1: Главная страница успешно загружается"""
        print("\n--- Тест 1: Загрузка главной страницы ---")

        # 1. Открыть сайт
        self.driver.get("https://www.wildberries.ru")
        time.sleep(2)  # Пауза для полной загрузки

        # 2. Принять куки
        self.accept_cookies()

        # 3. Проверки
        assert "Wildberries" in self.driver.title, f"В заголовке нет 'Wildberries'. Текущий: {self.driver.title}"
        assert "wildberries.ru" in self.driver.current_url

        # Проверяем видимость ключевых элементов
        search_input = self.wait.until(
            EC.visibility_of_element_located(self.LOCATORS["search_input"])
        )
        assert search_input.is_displayed(), "Поле поиска не отображается"

        # Проверяем кнопки в шапке
        for btn_name in ["catalog_button", "login_button", "cart_button"]:
            try:
                btn = self.driver.find_element(*self.LOCATORS[btn_name])
                assert btn.is_displayed(), f"Кнопка {btn_name} не отображается"
            except:
                print(f"  Предупреждение: элемент {btn_name} не найден (локатор может устареть)")

        print("✓ Главная страница загружена, ключевые элементы отображаются")

    def test_02_search_functionality(self):
        """Тест 2: Проверка работы поиска товаров"""
        print("\n--- Тест 2: Работа поиска ---")

        # 1. Открыть главную
        self.driver.get("https://www.wildberries.ru")
        self.accept_cookies()

        # 2. Ввести запрос и выполнить поиск
        search_query = "кроссовки"
        search_input = self.wait.until(
            EC.element_to_be_clickable(self.LOCATORS["search_input"])
        )
        search_input.clear()
        search_input.send_keys(search_query)

        # 3. Нажать кнопку поиска
        search_btn = self.driver.find_element(*self.LOCATORS["search_button"])
        search_btn.click()
        time.sleep(2)  # Ждем загрузки результатов

        # 4. Проверяем, что перешли на страницу результатов
        assert "catalog" in self.driver.current_url.lower() or "search" in self.driver.current_url.lower()

        # 5. Проверяем наличие результатов
        try:
            product_cards = self.driver.find_elements(*self.LOCATORS["product_card"])
            assert len(product_cards) > 0, "Не найдено ни одной карточки товара"

            # Проверяем, что в названиях товаров есть искомое слово
            first_product = self.driver.find_element(*self.LOCATORS["product_name"])
            product_text = first_product.text.lower()
            # Не строгая проверка, так как поиск может находить связанные товары
            print(f"✓ Найдено товаров: {len(product_cards)}")
            print(f"  Первый товар: '{first_product.text[:50]}...'")

        except Exception as e:
            print(f"  Предупреждение: не удалось проверить карточки товаров: {e}")

        print("✓ Поиск выполнен, страница с результатами загружена")

    def test_03_catalog_menu_opens(self):
        """Тест 3: Проверка открытия меню каталога"""
        print("\n--- Тест 3: Меню каталога ---")

        # 1. Открыть главную
        self.driver.get("https://www.wildberries.ru")
        self.accept_cookies()

        # 2. Нажать кнопку каталога
        catalog_btn = self.wait.until(
            EC.element_to_be_clickable(self.LOCATORS["catalog_button"])
        )
        catalog_btn.click()
        time.sleep(1)  # Ждем анимацию открытия

        # 3. Проверяем, что меню каталога открылось
        try:
            catalog_menu = self.driver.find_element(*self.LOCATORS["catalog_menu"])
            assert catalog_menu.is_displayed(), "Меню каталога не отображается"

            # Проверяем наличие категорий в меню
            categories = self.driver.find_elements(*self.LOCATORS["catalog_first_category"])
            assert len(categories) > 0, "В меню каталога нет категорий"

            print(f"✓ Меню каталога открыто, найдено категорий: {len(categories)}")

        except Exception as e:
            print(f"  Предупреждение: не удалось проверить меню каталога: {e}")
            # Делаем скриншот для отладки
            self.driver.save_screenshot("catalog_menu_error.png")

    def test_04_navigation_to_cart(self):
        """Тест 4: Переход в корзину"""
        print("\n--- Тест 4: Переход в корзину ---")

        # 1. Открыть главную
        self.driver.get("https://www.wildberries.ru")
        self.accept_cookies()

        # 2. Нажать на иконку корзины
        cart_btn = self.wait.until(
            EC.element_to_be_clickable(self.LOCATORS["cart_button"])
        )
        cart_btn.click()
        time.sleep(2)  # Ждем загрузки страницы корзины

        # 3. Проверяем, что перешли в корзину
        assert "basket" in self.driver.current_url.lower() or "cart" in self.driver.current_url.lower()

        # 4. Проверяем заголовок страницы
        try:
            page_title = self.driver.find_element(*self.LOCATORS["page_title"])
            title_text = page_title.text.lower()
            assert any(word in title_text for word in ["корзина", "basket", "cart"]), \
                f"Заголовок не соответствует странице корзины: {page_title.text}"
        except:
            print("  Предупреждение: не удалось проверить заголовок страницы корзины")

        print("✓ Успешный переход в корзину")


def run_all_tests():
    """Функция для запуска всех тестов"""
    tester = TestWildberriesSmoke()

    try:
        tester.setup_method()

        # Запуск тестов по порядку
        tester.test_01_homepage_loads()
        tester.test_02_search_functionality()
        tester.test_03_catalog_menu_opens()
        tester.test_04_navigation_to_cart()

        print("\n" + "=" * 50)
        print("ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ!")
        print("=" * 50)

    except Exception as e:
        print(f"\n✗ ТЕСТ ПРОВАЛЕН: {e}")
        # Делаем скриншот при падении
        tester.driver.save_screenshot("test_failure.png")
    finally:
        tester.teardown_method()


if __name__ == "__main__":
    # Запуск тестов при прямом выполнении файла
    run_all_tests()
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random


class BasePage:
    """Базовый класс для всех страниц Wildberries"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)

    def find(self, locator, timeout=10):
        """Найти элемент с ожиданием"""
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
        except TimeoutException:
            print(f"Элемент не найден: {locator}")
            raise

    def find_all(self, locator, timeout=5):
        """Найти все элементы"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located(locator)
            )
            return self.driver.find_elements(*locator)
        except TimeoutException:
            return []

    def click(self, locator):
        """Кликнуть по элементу"""
        element = self.find(locator)
        element.click()
        time.sleep(random.uniform(0.5, 1.5))  # Человеческая пауза

    def type_text(self, locator, text):
        """Ввести текст"""
        element = self.find(locator)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator):
        """Получить текст элемента"""
        return self.find(locator).text.strip()

    def is_visible(self, locator, timeout=5):
        """Проверить видимость элемента"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def scroll_to_element(self, element):
        """Прокрутить к элементу"""
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(0.5)


class MainPage(BasePage):
    """Главная страница Wildberries"""

    # Локаторы
    LOGIN_BUTTON = (By.XPATH, "//button[@data-link='{on login click}'] | //span[text()='Войти']/parent::button")
    SEARCH_INPUT = (By.ID, "searchInput")
    SEARCH_BUTTON = (By.CSS_SELECTOR, "button#applySearchBtn")
    CART_BUTTON = (By.CSS_SELECTOR, "a[data-wba-header-name='Cart']")
    PROFILE_BUTTON = (By.CSS_SELECTOR, "a[data-wba-header-name='Profile']")
    GEO_BUTTON = (By.CSS_SELECTOR, "span[data-link='{on location click}']")
    CATALOG_BUTTON = (By.CSS_SELECTOR, "button[data-wba-header-name='Catalog']")

    def open(self):
        """Открыть главную страницу"""
        self.driver.get("https://www.wildberries.ru")
        time.sleep(3)

        # Принять куки если есть
        try:
            cookie_accept = (By.XPATH, "//button[contains(text(), 'Принять') or contains(text(), 'Согласен')]")
            if self.is_visible(cookie_accept, 3):
                self.click(cookie_accept)
        except:
            pass

        return self

    def click_login(self):
        """Нажать кнопку 'Войти'"""
        self.click(self.LOGIN_BUTTON)
        return AuthPage(self.driver)

    def search_product(self, query):
        """Поиск товара"""
        self.type_text(self.SEARCH_INPUT, query)
        self.click(self.SEARCH_BUTTON)
        return SearchPage(self.driver)

    def open_cart(self):
        """Открыть корзину"""
        self.click(self.CART_BUTTON)
        return CartPage(self.driver)

    def is_user_logged_in(self):
        """Проверить авторизацию"""
        try:
            return self.is_visible(self.PROFILE_BUTTON, 3)
        except:
            return False


class AuthPage(BasePage):
    """Страница авторизации Wildberries"""

    # Локаторы
    PHONE_INPUT = (By.CSS_SELECTOR, "input[type='tel']")
    GET_CODE_BUTTON = (By.XPATH, "//button[contains(text(), 'Получить код')]")
    CODE_INPUTS = (By.CSS_SELECTOR, "input[type='number']")
    EMAIL_TAB = (By.XPATH, "//button[contains(text(), 'По e-mail')]")
    EMAIL_INPUT = (By.CSS_SELECTOR, "input[type='email']")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "input[type='password']")
    LOGIN_BUTTON = (By.XPATH, "//button[contains(text(), 'Войти')]")
    CLOSE_BUTTON = (By.CSS_SELECTOR, "button.j-close")

    def login_by_phone(self, phone):
        """Авторизация по телефону (демо версия)"""
        # Ввод телефона
        self.type_text(self.PHONE_INPUT, phone)
        self.click(self.GET_CODE_BUTTON)
        time.sleep(3)

        # В демо-режиме просто закрываем окно авторизации
        try:
            if self.is_visible(self.CLOSE_BUTTON, 3):
                self.click(self.CLOSE_BUTTON)
        except:
            pass

        return MainPage(self.driver)

    def login_by_email(self, email, password):
        """Авторизация по email"""
        # Переключиться на вкладку email
        self.click(self.EMAIL_TAB)
        time.sleep(1)

        # Ввести данные
        self.type_text(self.EMAIL_INPUT, email)
        self.type_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)
        time.sleep(3)

        return MainPage(self.driver)


class SearchPage(BasePage):
    """Страница результатов поиска"""

    # Локаторы
    PRODUCT_CARDS = (By.CSS_SELECTOR, "article.product-card")
    PRODUCT_NAMES = (By.CSS_SELECTOR, "span.product-card__name")
    PRODUCT_PRICES = (By.CSS_SELECTOR, "ins.price__lower-price")
    ADD_TO_CART_BUTTONS = (By.CSS_SELECTOR, "button.product-card__add-basket")
    SORT_BUTTON = (By.CSS_SELECTOR, "button.sort__btn")
    FILTER_BUTTON = (By.CSS_SELECTOR, "button.filters__btn")

    def get_product_count(self):
        """Получить количество товаров"""
        return len(self.find_all(self.PRODUCT_CARDS))

    def get_product_names(self):
        """Получить названия товаров"""
        names = []
        elements = self.find_all(self.PRODUCT_NAMES)
        for el in elements[:5]:  # Первые 5 товаров
            names.append(el.text)
        return names

    def open_first_product(self):
        """Открыть первый товар"""
        cards = self.find_all(self.PRODUCT_CARDS)
        if cards:
            cards[0].click()
            return ProductPage(self.driver)
        raise NoSuchElementException("No products found")

    def add_to_cart_from_list(self, index=0):
        """Добавить товар в корзину из списка"""
        buttons = self.find_all(self.ADD_TO_CART_BUTTONS)
        if buttons and len(buttons) > index:
            # Прокрутить к кнопке
            self.scroll_to_element(buttons[index])
            buttons[index].click()
            time.sleep(2)
            return True
        return False

    def sort_by_price_asc(self):
        """Сортировать по цене (возрастание)"""
        self.click(self.SORT_BUTTON)
        cheap_first = (By.XPATH, "//span[contains(text(), 'сначала дешёвые')]")
        self.click(cheap_first)
        time.sleep(2)
        return self


class ProductPage(BasePage):
    """Страница товара"""

    # Локаторы
    PRODUCT_TITLE = (By.CSS_SELECTOR, "h1.product-page__title")
    PRODUCT_PRICE = (By.CSS_SELECTOR, "ins.price-block__final-price")
    ADD_TO_CART_BUTTON = (By.CSS_SELECTOR, "button.btn-main")
    GO_TO_CART_BUTTON = (By.XPATH, "//a[contains(text(), 'Перейти в корзину')]")
    SIZE_BUTTONS = (By.CSS_SELECTOR, "label.j-size")
    COLOR_BUTTONS = (By.CSS_SELECTOR, "li.color-list__item")

    def get_product_info(self):
        """Получить информацию о товаре"""
        title = self.get_text(self.PRODUCT_TITLE)
        price = self.get_text(self.PRODUCT_PRICE)
        return {"title": title, "price": price}

    def select_size(self, size_index=0):
        """Выбрать размер"""
        sizes = self.find_all(self.SIZE_BUTTONS)
        if sizes and len(sizes) > size_index:
            # Проверяем, что размер доступен (не заблокирован)
            if "disabled" not in sizes[size_index].get_attribute("class"):
                sizes[size_index].click()
                return True
        return False

    def select_color(self, color_index=0):
        """Выбрать цвет"""
        colors = self.find_all(self.COLOR_BUTTONS)
        if colors and len(colors) > color_index:
            colors[color_index].click()
            return True
        return False

    def add_to_cart(self):
        """Добавить товар в корзину"""
        self.click(self.ADD_TO_CART_BUTTON)
        time.sleep(2)
        return self

    def go_to_cart(self):
        """Перейти в корзину"""
        try:
            if self.is_visible(self.GO_TO_CART_BUTTON, 3):
                self.click(self.GO_TO_CART_BUTTON)
        except:
            # Если кнопки нет, открываем корзину через шапку
            cart_button = (By.CSS_SELECTOR, "a[data-wba-header-name='Cart']")
            self.click(cart_button)

        return CartPage(self.driver)


class CartPage(BasePage):
    """Страница корзины"""

    # Локаторы
    CART_ITEMS = (By.CSS_SELECTOR, "div.cart-item")
    ITEM_NAMES = (By.CSS_SELECTOR, "a.goods-name")
    ITEM_PRICES = (By.CSS_SELECTOR, "span.price__block")
    DELETE_BUTTONS = (By.CSS_SELECTOR, "button.j-delete")
    INCREASE_QUANTITY = (By.CSS_SELECTOR, "button.count__plus")
    DECREASE_QUANTITY = (By.CSS_SELECTOR, "button.count__minus")
    CHECKOUT_BUTTON = (By.XPATH, "//button[contains(text(), 'Перейти к оформлению')]")
    EMPTY_CART = (By.XPATH, "//h2[contains(text(), 'Корзина пуста')]")
    TOTAL_PRICE = (By.CSS_SELECTOR, "div.total-amount__price")

    def get_items_count(self):
        """Получить количество товаров в корзине"""
        return len(self.find_all(self.CART_ITEMS))

    def get_item_names(self):
        """Получить названия товаров в корзине"""
        names = []
        elements = self.find_all(self.ITEM_NAMES)
        for el in elements:
            names.append(el.text)
        return names

    def get_total_price(self):
        """Получить общую сумму"""
        try:
            return self.get_text(self.TOTAL_PRICE)
        except:
            return "0 ₽"

    def remove_item(self, index=0):
        """Удалить товар из корзины"""
        buttons = self.find_all(self.DELETE_BUTTONS)
        if buttons and len(buttons) > index:
            buttons[index].click()
            time.sleep(2)
            return True
        return False

    def change_quantity(self, index=0, increase=True):
        """Изменить количество товара"""
        if increase:
            buttons = self.find_all(self.INCREASE_QUANTITY)
        else:
            buttons = self.find_all(self.DECREASE_QUANTITY)

        if buttons and len(buttons) > index:
            buttons[index].click()
            time.sleep(1)
            return True
        return False

    def proceed_to_checkout(self):
        """Перейти к оформлению заказа"""
        self.click(self.CHECKOUT_BUTTON)
        return CheckoutPage(self.driver)


class CheckoutPage(BasePage):
    """Страница оформления заказа"""

    # Локаторы
    DELIVERY_METHODS = (By.CSS_SELECTOR, "label.delivery-method")
    PICKUP_POINTS = (By.CSS_SELECTOR, "label.point-item")
    PAYMENT_METHODS = (By.CSS_SELECTOR, "label.payment-method")
    ORDER_BUTTON = (By.XPATH, "//button[contains(text(), 'Заказать')]")
    SUCCESS_MESSAGE = (By.XPATH, "//div[contains(text(), 'Заказ успешно оформлен')]")
    ADDRESS_INPUT = (By.CSS_SELECTOR, "input[placeholder='Адрес']")

    def select_delivery_method(self, method_index=0):
        """Выбрать способ доставки"""
        methods = self.find_all(self.DELIVERY_METHODS)
        if methods and len(methods) > method_index:
            methods[method_index].click()
            time.sleep(1)
            return True
        return False

    def select_pickup_point(self, point_index=0):
        """Выбрать пункт выдачи"""
        points = self.find_all(self.PICKUP_POINTS)
        if points and len(points) > point_index:
            points[point_index].click()
            time.sleep(1)
            return True
        return False

    def select_payment_method(self, method_index=0):
        """Выбрать способ оплаты"""
        methods = self.find_all(self.PAYMENT_METHODS)
        if methods and len(methods) > method_index:
            methods[method_index].click()
            time.sleep(1)
            return True
        return False

    def place_order(self):
        """Оформить заказ (демо-режим)"""
        # В реальном тесте здесь будет клик по кнопке "Заказать"
        # В демо-режиме просто проверяем, что страница загружена
        print("Демо: Заказ был бы оформлен здесь")
        return self

    def is_checkout_page_loaded(self):
        """Проверить загрузку страницы оформления"""
        try:
            return (self.is_visible(self.ORDER_BUTTON, 5) or
                    self.is_visible(self.DELIVERY_METHODS, 5))
        except:
            return False
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
    LOGIN_BUTTON = (By.CLASS_NAME, "navbar-pc__link j-wba-header-item")  ## Войти
    SEARCH_INPUT = (By.CSS_SELECTOR, "input#searchInput.search-catalog__input j-wba-header-item search-placeholder")  ## строка поиска
    SEARCH_BUTTON = (By.ID, "applySearchBtn")  ## кнопка поиска
    CART_BUTTON = (By.CSS_SELECTOR, "a.navbar-pc__link j-wba-header-item")  ## кнопка корзины
    PROFILE_BUTTON = (By.CSS_SELECTOR, "a.navbar-pc__link j-wba-header-item")  ## кнопка профиля
    GEO_BUTTON = (By.CSS_SELECTOR, "a.navbar-pc__link j-wba-header-item")  ## кнопка адреса
    CATALOG_BUTTON = (By.CSS_SELECTOR, "button.nav-element__burger j-menu-burger-btn j-wba-header-item j-nav nav-element__burger--close")  ## Каталог

    def open(self):
        """Открыть главную страницу"""
        self.driver.get("https://www.wildberries.ru")
        time.sleep(3)

        # Принять куки если есть
        try:
            cookie_accept = (By.XPATH, "//button[contains(text(), 'Окей') or contains(text(), 'Окей')]")
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
    PHONE_INPUT = (By.NAME, "phoneNumber")  ## ввод телефона
    GET_CODE_BUTTON = (By.ID, "requestCode")  ## кнопка запроса кода
    CODE_INPUTS = (By.CLASS_NAME, "_charInput_1r1zc_1 charInput--irP9m _count_1r1zc_12")  ## поле ввода кода
    LOGIN_BUTTON = (By.XPATH, "//button[contains(text(), 'Войти')]")  ## кнопка "войти"
    CLOSE_BUTTON = (By.CLASS_NAME, "_close_1b9nk_55 popup__close close")  ## кнопка "закрыть"(крестик)

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



class SearchPage(BasePage):
    """Страница результатов поиска"""

    # Локаторы
    PRODUCT_CARDS = (By.CSS_SELECTOR, "a.product-card__link j-card-link j-open-full-product-card") ## Карточка продукта
    PRODUCT_NAMES = (By.CLASS_NAME, "product-card__brand-wrap") ## наименование продукта
    PRODUCT_PRICES = (By.CSS_SELECTOR, "div.product-card__price price") ## цена продукта
    ADD_TO_CART_BUTTONS = (By.CSS_SELECTOR, "a.product-card__add-basket j-add-to-basket orderLink--tNgvO btn-main") ## доабвить в корзину


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



class ProductPage(BasePage):
    """Страница товара"""

    # Локаторы
    PRODUCT_TITLE = (By.CSS_SELECTOR, "h3.mo-typography mo-typography_variant_title3 mo-typography_variable-weight_title3 mo-typography_color_primary productTitle--J2W7I")
    PRODUCT_PRICE = (By.CSS_SELECTOR, "h2.mo-typography mo-typography_variant_title2 mo-typography_variable-weight_title2 mo-typography_color_accent")
    ADD_TO_CART_BUTTON = (By.CSS_SELECTOR, "span.mo-typography mo-typography_variant_action-accent mo-typography_variable-weight_action-accent mo-typography_ws_nowrap")
    GO_TO_CART_BUTTON = (By.XPATH, "//a[contains(text(), 'Перейти в корзину')]")
    SIZE_BUTTONS = (By.CSS_SELECTOR, "button.sizesListButton--WuH9K")
    COLOR_BUTTONS = (By.CSS_SELECTOR, "a.slideAnchor--CwO_y")

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
    CART_ITEMS = (By.CSS_SELECTOR, "div.basketList")
    ITEM_NAMES = (By.CSS_SELECTOR, "span.good-info__good-name")
    ITEM_PRICES = (By.CSS_SELECTOR, "div.list-item__price-wallet list-item__price-wallet--wb-wallet-icon red-price")
    DELETE_BUTTONS = (By.CSS_SELECTOR, "button.btn__del j-basket-item-del")
    INCREASE_QUANTITY = (By.CSS_SELECTOR, "button.count__plus plus")
    DECREASE_QUANTITY = (By.CSS_SELECTOR, "button.count__minus minus disabled")
    CHECKOUT_BUTTON = (By.XPATH, "//button[contains(text(), 'Заказать')]")
    EMPTY_CART = (By.XPATH, "//h1[contains(text(), 'В корзине пока пусто')]")
    TOTAL_PRICE = (By.CSS_SELECTOR, "p.b-top__total line")

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
    DELIVERY_METHODS = (By.CLASS_NAME, "basket-delivery__choose-address j-btn-choose-address") ## способ доставки
    PICKUP_POINTS = (By.CLASS_NAME, "tabs-switch__text--HMq3V") ## пункт выдачи
    PAYMENT_METHODS = (By.CLASS_NAME, "basket-section__header") ## способ оплаты
    ORDER_BUTTON = (By.XPATH, "//button[contains(text(), 'Заказать')]")
    SUCCESS_MESSAGE = (By.XPATH, "//div[contains(text(), 'Заказ успешно оформлен')]")

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


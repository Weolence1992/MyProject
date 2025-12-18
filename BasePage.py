from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time



class BasePage:
    """Базовый класс для всех страниц Wildberries"""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 15)



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
    LOGIN_BUTTON = (By.CLASS_NAME, "navbar-pc__link j-wba-header-item") ## Войти
    SEARCH_INPUT = (By.CSS_SELECTOR, "input#searchInput.search-catalog__input j-wba-header-item search-placeholder") ## строка поиска
    SEARCH_BUTTON = (By.ID, "applySearchBtn") ## кнопка поиска
    CART_BUTTON = (By.CSS_SELECTOR, "a.navbar-pc__link j-wba-header-item") ## кнопка корзины
    PROFILE_BUTTON = (By.CSS_SELECTOR, "a.navbar-pc__link j-wba-header-item") ## кнопка профиля
    CATALOG_BUTTON = (By.CSS_SELECTOR, "button.nav-element__burger j-menu-burger-btn j-wba-header-item j-nav nav-element__burger--close") ## Каталог

    def open(self):
        """Открыть главную страницу"""
        self.driver.get("https://www.wildberries.ru")
        time.sleep(3)


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
    PHONE_INPUT = (By.NAME, "phoneNumber")
    GET_CODE_BUTTON = (By.ID, "requestCode")
    CODE_INPUTS = (By.CLASS_NAME, "_charInput_1r1zc_1 charInput--irP9m _count_1r1zc_12")
    LOGIN_BUTTON = (By.XPATH, "//button[contains(text(), 'Войти')]")
    CLOSE_BUTTON = (By.CLASS_NAME, "_close_1b9nk_55 popup__close close")

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
    PRODUCT_CARDS = (By.CSS_SELECTOR, "div.product-card-list")
    PRODUCT_NAMES = (By.CLASS_NAME, "product-card j-card-item j-analitics-item")
    ADD_TO_CART_BUTTONS = (By.CSS_SELECTOR, "button.mo-button mo-button_view_fill mo-button_colors_brand mo-button_width_fill mo-button_size_large")


    def open_first_product(self):
        """Открыть первый товар"""
        cards = self.find_all(self.PRODUCT_CARDS)
        cards[0].click()


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


class CartPage(BasePage):
    """Страница корзины"""

    # Локаторы
    CART_ITEMS = (By.CLASS_NAME, "accordion__list")
    DELETE_BUTTONS = (By.CSS_SELECTOR, "button.btn__del j-basket-item-del")
    CHECKOUT_BUTTON = (By.XPATH, "//button[contains(text(), 'Заказать')]")

    def get_items_count(self, quantity=0):
        """Получить количество товаров в корзине"""
        return len(self.find_all(self.CART_ITEMS))


    def remove_item(self, index=0):
        """Удалить товар из корзины"""
        buttons = self.find_all(self.DELETE_BUTTONS)
        if buttons and len(buttons) > index:
            buttons[index].click()
            time.sleep(2)
            return True
        return False



    def proceed_to_checkout(self):
        """Перейти к оформлению заказа"""
        self.click(self.CHECKOUT_BUTTON)
        return CheckoutPage(self.driver)


class CheckoutPage(BasePage):
    """Страница оформления заказа"""

    # Локаторы
    DELIVERY_METHODS = (By.CLASS_NAME, "basket-delivery__choose-address j-btn-choose-address")
    PICKUP_POINTS = (By.CLASS_NAME, "tabs-switch__text--HMq3V")
    PAYMENT_METHODS = (By.CLASS_NAME, "basket-section__header")
    ORDER_BUTTON = (By.XPATH, "//button[contains(text(), 'Заказать')]")

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
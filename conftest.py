import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()
@pytest.fixture
def driver():

    options = webdriver.ChromeOptions()

    ## Указывает Chrome запускаться в полноэкранном режиме.
    options.add_argument("--start-maximized")

    ## Отключает уведомления браузера (всплывающие окна, оповещающие о новых сообщениях или обновлениях)
    options.add_argument("--disable-notifications")

    ## Предотвращает отображение в Chrome информации о том, что им управляет автоматизация (скрывает тот факт, что это бот).
    options.add_argument("--disable-blink-features=AutomationControlled")

    ## Исключает переключатель «enable-automation», чтобы еще больше скрыть наличие автоматизации в Chrome.
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    ## Отключает расширение, помогающее в автоматизации, что делает бота менее заметным.
    options.add_experimental_option('useAutomationExtension', False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)

    yield driver

    driver.quit()

@pytest.fixture
def test_data():
    """Тестовые данные"""
    return {
        "phone": os.getenv("WB_PHONE", "+79991234567"),
        "search_query": "кроссовки",
        "product_name": "Кроссовки",
        "city": "Москва",
    }
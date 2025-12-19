# Установка зависимостей
pip install -r requirements.txt

# Запуск всех тестов
pytest tests/ -v

# Запуск smoke тестов
pytest tests/ -v -m smoke

# Запуск тестов для конкретного модуля
pytest tests/test_pet.py -v
pytest tests/test_store.py -v
pytest tests/test_user.py -v

# Запуск с отчетом HTML
pytest tests/ -v --html=report.html

# Запуск с отчетом Allure
pytest tests/ -v --alluredir=allure-results
allure serve allure-results

# Запуск с параллельным выполнением
pytest tests/ -v -n auto
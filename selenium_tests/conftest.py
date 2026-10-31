# selenium_tests/conftest.py
import os
import pytest
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

load_dotenv()

@pytest.fixture
def driver():
    options = Options()
    # options.add_argument('--headless=new') # Для портфолио лучше оставить закомментированным, чтобы было видно, как браузер работает
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    driver.maximize_window()
    yield driver
    driver.quit()

@pytest.fixture(scope="session")
def credentials():
    """Возвращает валидные учётные данные из .env (или дефолты)."""
    return {
        "email": os.getenv("CUSTOMER_EMAIL", "user@phptravels.com"),
        "password": os.getenv("CUSTOMER_PASSWORD", "demouser"),
    }
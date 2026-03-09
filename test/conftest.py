import sys
import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configuration.configProvider import configProvider
from testdata.DataProvider import DataProvider
from page.MainPage import MainPage
from api.ProductApi import ProductApi


@pytest.fixture(scope="session")
def config():
    return configProvider()

@pytest.fixture
def api_client():
    base_url = os.environ.get("CHITAI_API_BASE_URL")
    token = os.environ.get("CHITAI_API_TOKEN")
    if not base_url or not token:
        pytest.skip("CHITAI_API_BASE_URL или CHITAI_API_TOKEN не заданы - пропуск API тестов")
    return ProductApi(base_url, token)

@pytest.fixture
def test_data():
    return DataProvider()


@pytest.fixture(scope="function")
def driver(config):
    """Фикстура для WebDriver"""
    timeout = int(config.get("ui", "timeout", "30"))
    browser_name = config.get("ui", "browser_name", "chrome")
    
    if browser_name == "chrome":
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless=new")  # раскомментируйте для headless
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    else:
        raise NotImplementedError("Only chrome is supported in this skeleton")

    driver.implicitly_wait(timeout)
    driver.maximize_window()
    
    yield driver
    
    # Делаем скриншот при падении теста
    if hasattr(driver, "_current_failure"):
        driver.save_screenshot("failure.png")
    
    driver.quit()


@pytest.fixture
def browser(driver):
    """Алиас для driver, для обратной совместимости"""
    return driver


@pytest.fixture
def login_via_cookie(browser, test_data, config):
    """
    Фикстура для входа через cookies.
    Использует метод login_with_cookies из BasePage через MainPage.
    """
    main_page = MainPage(browser)

@pytest.fixture
def cart_with_item(browser, login_via_cookie):
    """
    Фикстура: открываем главную страницу, добавляем в корзину первый товар
    и возвращаем объект MainPage для дальнейших действий в тесте.
    """
    page = MainPage(browser)
    page.go()  # открыть базовый URL
    page.add_first_product_to_cart()  # добавить товар в корзину
    return page
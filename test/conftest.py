import sys
import os
import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configuration.configProvider import configProvider
from testdata.DataProvider import DataProvider
from page.MainPage import MainPage


@pytest.fixture(scope="session")
def config():
    return configProvider()


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
    
    # Получаем токены из test_data
    refresh_token = test_data.get("refresh_token")
    access_token = test_data.get("access_token")
    
    if refresh_token and access_token and refresh_token != "auth_token_cookie_name":
        main_page.login_with_cookies(refresh_token=refresh_token, access_token=access_token)
    else:
        # Пробуем использовать переменные окружения
        main_page.login_with_cookies()
    
    # Задержка для визуального контроля
    wait_time = test_data.get("wait_after_actions")
    if wait_time:
        try:
            time.sleep(float(wait_time))
        except (ValueError, TypeError):
            time.sleep(1)
    
    return main_page
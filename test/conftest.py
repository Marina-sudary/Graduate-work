import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configuration.configProvider import configProvider

import pytest
import requests
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from configuration.configProvider import configProvider
from testdata.DataProvider import DataProvider
from page.MainPage import MainPage

@pytest.fixture(scope="session")
def config():
    return configProvider()

@pytest.fixture
def test_data():
    return DataProvider()

@pytest.fixture
def browser(config):
    timeout = int(config.get("ui", "timeout"))
    browser_name = config.get("ui", "browser_name")
    if browser_name == "chrome":
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless=new")  # раскомментируйте для headless
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    else:
        raise NotImplementedError("Only chrome is supported in this skeleton")

    driver.implicitly_wait(timeout)
    driver.maximize_window()
    yield driver
    driver.quit()

@pytest.fixture
def login_via_cookie(browser, test_data, config):
    """
    Если у вас есть токен авторизации (cookie), можно установить его напрямую и перейти на сайт.
    Заполните auth_token_value в test_data.json.
    """
    token_name = test_data.get("auth_token_cookie_name")
    token_value = test_data.get("auth_token_value")
    base = config.get("ui", "base_url").rstrip("/")
    browser.get(base)  # нужно сначала открыть домен, чтобы добавить cookie
    if token_name and token_value:
        cookie = {"name": token_name, "value": token_value, "path": "/", "domain": "www.chitai-gorod.ru"}
        try:
            browser.add_cookie(cookie)
            # после добавления куки обновим страницу, чтобы сессия подхватилась
            browser.refresh()
        except Exception:
            # иногда требуется подставить без domain
            cookie2 = {"name": token_name, "value": token_value}
            browser.add_cookie(cookie2)
            browser.refresh()
    yield
    # задержка для визуального контроля
    # Получаем значение и преобразуем в число
wait_time = test_data.get("wait_after_actions")
if wait_time:
    try:
        time.sleep(float(wait_time))
    except (ValueError, TypeError):
        time.sleep(1)  # значение по умолчанию, если не удалось преобразовать
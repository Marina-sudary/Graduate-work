import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from typing import Generator
import allure
from config.settings import Settings
from api.client import ChitaiGorodAPI


def pytest_addoption(parser):
    """Добавление командной строки опций."""
    parser.addoption(
        "--mode",
        action="store",
        default="all",
        help="Режим запуска тестов: ui, api, all"
    )


def pytest_collection_modifyitems(config, items):
    """Модификация сбора тестов в зависимости от режима."""
    run_mode = config.getoption("--mode")
    
    if run_mode == "ui":
        skip_api = pytest.mark.skip(reason="Запущен только UI режим")
        for item in items:
            if "api" in item.keywords:
                item.add_marker(skip_api)
    elif run_mode == "api":
        skip_ui = pytest.mark.skip(reason="Запущен только API режим")
        for item in items:
            if "ui" in item.keywords:
                item.add_marker(skip_ui)


@pytest.fixture(scope="class")
def driver() -> Generator[webdriver.Chrome, None, None]:
    """
    Фикстура для создания и закрытия веб-драйвера.
    scope="class" - драйвер создается один раз для всего класса тестов.
    """
    with allure.step("Инициализация веб-драйвера"):
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(Settings.DEFAULT_TIMEOUT)
        driver.set_page_load_timeout(Settings.PAGE_LOAD_TIMEOUT)
        
        # Открываем сайт один раз для всех тестов
        with allure.step("Открыть главную страницу"):
            driver.get(Settings.BASE_URL)
            WebDriverWait(driver, Settings.PAGE_LOAD_TIMEOUT).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        
        yield driver
        
        with allure.step("Закрытие веб-драйвера"):
            driver.quit()


@pytest.fixture(scope="session")
def api_client() -> ChitaiGorodAPI:
    """
    Фикстура для создания API клиента.
    
    Returns:
        ChitaiGorodAPI: Экземпляр API клиента
    """
    with allure.step("Инициализация API клиента"):
        return ChitaiGorodAPI()


# Добавляем WebDriverWait для использования в тестах
from selenium.webdriver.support.ui import WebDriverWait
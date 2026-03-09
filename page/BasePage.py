import allure
import os
from urllib.parse import unquote
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from configuration.configProvider import configProvider

class BasePage:
    def __init__(self, driver: WebDriver, timeout: int = 10):
        self.__driver = driver
        self.wait = WebDriverWait(driver, timeout)
        self.base_url = configProvider().get("ui", "base_url").rstrip("/")
    
    @allure.step("Открыть страницу")
    def open(self, url: str = None):
        """Открыть указанный URL или базовый URL"""
        if url:
            self.__driver.get(url)
        else:
            self.__driver.get(self.base_url)
    
    @allure.step("Получить текущий URL")
    def get_current_url(self) -> str:
        return self.__driver.current_url
    
    @allure.step("Обновить страницу")
    def refresh(self):
        self.__driver.refresh()
    
    @allure.step("Сделать скриншот")
    def take_screenshot(self, name: str = "screenshot"):
        """Сделать скриншот и прикрепить к Allure"""
        allure.attach(
            self.__driver.get_screenshot_as_png(),
            name=name,
            attachment_type=allure.attachment_type.PNG
        )
    
    @allure.step("Войти с использованием cookies")
    def login_with_cookies(self, refresh_token: str = None, access_token: str = None):
        """
        Вход в систему через установку cookies
        Токены можно передать напрямую или через переменные окружения:
        - CHITAI_REFRESH_TOKEN
        - CHITAI_ACCESS_TOKEN
        """
        if not refresh_token or not access_token:
            refresh_token = refresh_token or os.environ.get("CHITAI_REFRESH_TOKEN")
            access_token = access_token or os.environ.get("CHITAI_ACCESS_TOKEN")

        if not refresh_token or not access_token:
            raise ValueError("Tokens for login via cookies are not provided. Pass as args or set CHITAI_REFRESH_TOKEN and CHITAI_ACCESS_TOKEN.")

        # Декодируем URL-encoded access token если нужно
        access_token_decoded = unquote(access_token)

        # Открываем домен и добавляем cookies
        self.__driver.get(self.base_url)
        self.__driver.delete_all_cookies()

        cookies = [
            {"name": "refresh-token", "value": refresh_token, "path": "/", "domain": "www.chitai-gorod.ru", "secure": True},
            {"name": "access-token", "value": access_token_decoded, "path": "/", "domain": "www.chitai-gorod.ru", "secure": True},
        ]

        for cookie in cookies:
            try:
                self.__driver.add_cookie(cookie)
            except Exception:
                # Пробуем альтернативный домен
                cookie_alt = dict(cookie)
                cookie_alt["domain"] = ".chitai-gorod.ru"
                try:
                    self.__driver.add_cookie(cookie_alt)
                except Exception as e:
                    print(f"Не удалось установить cookie {cookie['name']}: {e}")

        self.__driver.refresh()
    
    @allure.step("Проверить наличие элемента")
    def is_element_present(self, by, selector: str, timeout: int = 5) -> bool:
        """Проверить, присутствует ли элемент на странице"""
        try:
            WebDriverWait(self.__driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return True
        except:
            return False
    
    @allure.step("Проверить видимость элемента")
    def is_element_visible(self, by, selector: str, timeout: int = 5) -> bool:
        """Проверить, видим ли элемент на странице"""
        try:
            WebDriverWait(self.__driver, timeout).until(
                EC.visibility_of_element_located((by, selector))
            )
            return True
        except:
            return False
    
    def find_element(self, by, selector: str):
        """Найти элемент"""
        return self.__driver.find_element(by, selector)
    
    def find_elements(self, by, selector: str):
        """Найти все элементы"""
        return self.__driver.find_elements(by, selector)
    
    def execute_script(self, script: str, *args):
        """Выполнить JavaScript"""
        return self.__driver.execute_script(script, *args)
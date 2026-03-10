import allure
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
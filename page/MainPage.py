import os
import sys
import allure
import time
from urllib.parse import unquote
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from configuration.configProvider import configProvider

class MainPage:
    def __init__(self, driver: WebDriver, timeout: int = 10) -> None:
        self.__driver = driver
        self.wait = WebDriverWait(driver, timeout)
        self.base = configProvider().get("ui", "base_url").rstrip("/")

    @allure.step("Открыть стартовую страницу")
    def go(self):
        self.__driver.get(self.base)

    @allure.step("Поиск и ввод фразы: {phrase}")
    def search(self, phrase: str):
        input_sel = "input#app-search"
        btn_sel = 'button[aria-label="Найти"]'
        inp = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, input_sel)))
        inp.clear()
        inp.send_keys(phrase)
        btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, btn_sel)))
        btn.click()

    @allure.step("Добавить первый найденный товар в корзину")
    def add_first_product_to_cart(self):
        selector = 'button[data-testid-button-mini-product-card="canBuy"]'
        try:
            wait = WebDriverWait(self.__driver, 5)

        # Найти все кнопки "Купить"
            btns = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
            if not btns:
                raise Exception("Кнопки 'Купить' не найдены")

        # Прокрутить к первой кнопке
            first_btn = btns[0]
            self.__driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", first_btn)

        # После прокрутки снова получить доступ к элементу и дождаться кликабельности
        # Это помогает избежать ошибок из-за устаревшей ссылки на элемент после прокрутки
            first_btn = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))[0]
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))

        # Клик по кнопке
            first_btn.click()
        except Exception:
        # Можно добавить логирование или повторную обработку ошибок здесь
            raise

    @allure.step("Открыть корзину")
    def open_cart(self):
        selector = 'button[aria-label="Корзина"][data-testid-button-header="cart"]'
        btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        btn.click()

    @allure.step("Увеличить количество первого товара в корзине")
    def increase_quantity_first_item(self):
        xpath = "//svg[contains(@class,'chg-ui-input-number__input-control--increment')]/ancestor::button[1]"
        btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        btn.click()

    @allure.step("Удалить первый товар из корзины")
    def delete_first_item_from_cart(self):
        selector = "button.cart-item__delete-button"
        btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        btn.click()

    @allure.step("Переключить закладку на первый товар")
    def toggle_favorite_on_first(self):
        selector = 'button[data-testid-fav-button-mini-product-card="inBookmark"]'
        btns = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
        if not btns:
            raise Exception("Кнопки 'В закладки' не найдены")
        btns[0].click()

    @allure.step("Войти с использованием cookies (refresh-token и access-token)")
    def login_with_cookies(self, refresh_token: str = None, access_token: str = None):
        """
        Вызов аналогичен AuthPage.login_with_cookies, tokens можно передавать сюда
        или через переменные окружения CHITAI_REFRESH_TOKEN и CHITAI_ACCESS_TOKEN.
        """
        if not refresh_token or not access_token:
            refresh_token = refresh_token or os.environ.get("CHITAI_REFRESH_TOKEN")
            access_token = access_token or os.environ.get("CHITAI_ACCESS_TOKEN")

        if not refresh_token or not access_token:
            raise ValueError("Tokens for cookies login not provided")

        access_token_decoded = unquote(access_token)

        base = configProvider().get("ui", "base_url").rstrip("/")

        self.__driver.get(base)
        self.__driver.delete_all_cookies()

        cookies = [
            {"name": "refresh-token", "value": refresh_token, "path": "/", "domain": "www.chitai-gorod.ru", "secure": True},
            {"name": "access-token", "value": access_token_decoded, "path": "/", "domain": "www.chitai-gorod.ru", "secure": True},
        ]

        for cookie in cookies:
            try:
                self.__driver.add_cookie(cookie)
            except Exception:
                cookie_alt = dict(cookie)
                cookie_alt["domain"] = ".chitai-gorod.ru"
                self.__driver.add_cookie(cookie_alt)

        self.__driver.refresh()

    def get_current_url(self):
        return self.__driver.current_url
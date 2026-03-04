from email.utils import unquote

import allure
import os
import sys 
from configuration.configProvider import configProvider
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from configuration.configProvider import configProvider

class AuthPage:
    def __init__(self, driver: WebDriver, timeout: int = 10) -> None:
        base = configProvider().get("ui", "base_url")
        self.__url = base.rstrip("/")
        self.__driver = driver
        self.wait = WebDriverWait(driver, timeout)

    @allure.step("Открыть стартовую страницу")
    def go(self):
        self.__driver.get(self.__url)

    @allure.step("Открыть окно авторизации (меню профиля / Войти)")
    def open_auth_modal(self):
        selector = 'button[aria-label="Меню профиля"][data-testid-button-header="profile"]'
        btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        btn.click()

    @allure.step("Ввести номер телефона для авторизации")
    def enter_phone(self, phone: str):
        selector = "span.chg-app-input__item input[type='tel'], span.chg-app-input__item input"
        inp = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
        inp.clear()
        inp.send_keys(str(phone))

    @allure.step("Нажать кнопку 'Получить код'")
    def click_get_code(self):
        selector = 'button[data-testid-button-auth-modal="getCode"]'
        btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        btn.click()

    @allure.step("Ввести OTP-код")
    def enter_otp(self, code: str):
        selector = 'input[automation-id="otp-input"], input[name="otp"], input[placeholder="••••"]'
        otp = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
        otp.clear()
        otp.send_keys(str(code))

    @allure.step("Заполнить регистрационные данные")
    def fill_registration(self, first_name: str, last_name: str, email: str, accept_age: bool = True):
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input#v-0-0"))).clear()
        self.__driver.find_element(By.CSS_SELECTOR, "input#v-0-0").send_keys(first_name)

        self.__driver.find_element(By.CSS_SELECTOR, "input#v-0-1").clear()
        self.__driver.find_element(By.CSS_SELECTOR, "input#v-0-1").send_keys(last_name)

        self.__driver.find_element(By.CSS_SELECTOR, "input#v-0-2").clear()
        self.__driver.find_element(By.CSS_SELECTOR, "input#v-0-2").send_keys(email)

        # Убрать/поставить галочку по возрасту (пример)
        checkbox_selector = "input[type='checkbox'][name='policy'], .chg-app-checkbox__input"
        checkbox = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, checkbox_selector)))
        is_checked = checkbox.is_selected()
        if accept_age and not is_checked:
            checkbox.click()
        if not accept_age and is_checked:
            checkbox.click()

    @allure.step("Нажать кнопку регистрация (Зарегистрироваться)")
    def click_register(self):
        xpath = "//button[.//div[contains(normalize-space(), 'Зарегистрироваться')]]"
        btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        btn.click()

    @allure.step("Войти с использованием cookies (refresh-token и access-token)")
    def login_with_cookies(self, refresh_token: str = None, access_token: str = None):
        """
        Простой способ войти по cookie. Токены можно передать напрямую или через переменные окружения:
        - CHITAI_REFRESH_TOKEN
        - CHITAI_ACCESS_TOKEN
        """
        if not refresh_token or not access_token:
            refresh_token = refresh_token or os.environ.get("CHITAI_REFRESH_TOKEN")
            access_token = access_token or os.environ.get("CHITAI_ACCESS_TOKEN")

        if not refresh_token or not access_token:
            raise ValueError("Tokens for login via cookies are not provided. Pass as args or set CHITAI_REFRESH_TOKEN and CHITAI_ACCESS_TOKEN.")

        # Decode возможную URL-encode части access-token
        access_token_decoded = unquote(access_token)

        base = configProvider().get("ui", "base_url").rstrip("/")

        # Откроем домен и добавим cookies
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
                # Фолбэк на альтернативный домен
                cookie_alt = dict(cookie)
                cookie_alt["domain"] = ".chitai-gorod.ru"
                self.__driver.add_cookie(cookie_alt)

        self.__driver.refresh()

    def get_current_url(self):
        return self.__driver.current_url
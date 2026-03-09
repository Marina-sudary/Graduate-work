
import allure
import sys
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from page.BasePage import BasePage

class MainPage(BasePage):
    def __init__(self, driver: WebDriver, timeout: int = 10) -> None:
        super().__init__(driver, timeout)
        # Метод login_with_cookies уже унаследован от BasePage!

    @allure.step("Открыть стартовую страницу")
    def go(self):
        self.open()  # Используем метод из BasePage

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
            # Найти все кнопки "Купить"
            btns = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))
            if not btns:
                raise Exception("Кнопки 'Купить' не найдены")

            # Прокрутить к первой кнопке
            first_btn = btns[0]
            self.execute_script("arguments[0].scrollIntoView({block: 'center'});", first_btn)

            # После прокрутки снова получить доступ к элементу
            first_btn = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector)))[0]
            self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))

            # Клик по кнопке
            first_btn.click()
            
        except Exception as e:
            self.take_screenshot("add_to_cart_error")
            raise Exception(f"Не удалось добавить товар в корзину: {e}")

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
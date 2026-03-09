import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

class TestCartUI:
    def test_clear_cart_ui(self, browser, cart_with_item):
        """
        Тест: удалить первый товар из корзины через UI.
        Без yield — только обычное выполнение и teardown внутри блока finally (при желании).
        """
        wait = WebDriverWait(browser, 15)

        try:
            browser.get("https://www.chitai-gorod.ru/cart")
            cart_with_item.delete_first_item_from_cart()

            # Ждем, пока корзина станет пустой
            wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "div.cart-item")) == 0)
        finally:
            # Здесь можно попытаться очистить корзину через API, если токены заданы
            pass

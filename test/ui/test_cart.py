import pytest
import allure
from page.MainPage import MainPage
from api.ProductApi import ProductApi
import os

BASE_URL = "https://web-agr.chitai-gorod.ru/web/api/v2/search/product"
TOKEN = os.environ.get("CHITAI_API_TOKEN", "eyJhbGc...")


@allure.epic("UI тестирование сайта Читай-город")
@allure.feature("Корзина")
class TestCartUI:
    
    @pytest.fixture
    def api_client(self):
        """Фикстура для API клиента"""
        return ProductApi(BASE_URL, TOKEN)
    
    @pytest.fixture
    def cart_with_item(self, browser, login_via_cookie, api_client):
        """
        Фикстура, которая гарантированно добавляет товар в корзину через API
        перед выполнением UI тестов
        """
        # Находим товар через API
        response = api_client.search_product("книга", limit=1)
        assert response.status_code == 200
        
        response_json = response.json()
        
        # Извлекаем ID товара (зависит от структуры ответа)
        product_id = None
        if 'included' in response_json:
            for item in response_json['included']:
                if item.get('type') == 'product':
                    product_id = item.get('id')
                    break
        
        if not product_id:
            pytest.fail("Не удалось получить ID товара для добавления в корзину")
        
        # Добавляем товар в корзину через API
        add_response = api_client.add_to_cart(product_id, quantity=1)
        assert add_response.status_code in [200, 201], "Не удалось добавить товар в корзину через API"
        
        # Возвращаем страницу для тестов
        main_page = MainPage(browser)
        return main_page
    
    @allure.title("Модификация количества товара в корзине")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_modify_quantity(self, browser, cart_with_item):
        """
        Тест проверяет возможность увеличения количества товара в корзине.
        Предусловие: товар уже добавлен в корзину через API
        """
        main_page = cart_with_item
        
        with allure.step("Открыть страницу корзины"):
            browser.get("https://www.chitai-gorod.ru/cart")
        
        with allure.step("Увеличить количество первого товара"):
            # Проверяем, что кнопка существует и активна
            main_page.increase_quantity_first_item()
        
        with allure.step("Проверить, что количество изменилось"):
            # Здесь нужно добавить проверку изменения количества
            # Например, проверить значение в инпуте количества
            pass
    
    @allure.title("Удаление товара из корзины")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_cart_delete_item(self, browser, cart_with_item):
        """
        Тест проверяет удаление товара из корзины.
        Предусловие: товар уже добавлен в корзину через API
        """
        main_page = cart_with_item
        
        with allure.step("Открыть страницу корзины"):
            browser.get("https://www.chitai-gorod.ru/cart")
        
        with allure.step("Удалить первый товар из корзины"):
            main_page.delete_first_item_from_cart()
        
        with allure.step("Проверить, что товар удален"):
            # Проверяем, что появилось сообщение о пустой корзине
            # или что элемент больше не отображается
            pass
    
    @allure.title("Очистка корзины через UI")
    @allure.severity(allure.severity_level.NORMAL)
    def test_clear_cart_ui(self, browser, cart_with_item):
        """
        Тест проверяет очистку корзины через UI.
        Предусловие: несколько товаров в корзине
        """
        main_page = cart_with_item
        
        with allure.step("Открыть страницу корзины"):
            browser.get("https://www.chitai-gorod.ru/cart")
        
        with allure.step("Удалить все товары из корзины"):
            # Пока удаляем только первый, в реальности нужно удалить все
            main_page.delete_first_item_from_cart()
        
        # Очистка после теста
        yield
        
        with allure.step("Очистить корзину через API после теста"):
            api_client = ProductApi(BASE_URL, TOKEN)
            api_client.clear_cart()
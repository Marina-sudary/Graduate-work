import allure
import pytest
import os
from api.ProductApi import ProductApi

BASE_URL = "https://web-agr.chitai-gorod.ru/web/api/v2"
TOKEN = os.environ.get("CHITAI_API_TOKEN", "eyJhbGc...")


@allure.epic("API тестирование сайта Читай-город")
@allure.feature("Корзина")
class TestCartAPI:
    
    @pytest.fixture(scope="class")
    def api_client(self):
        """Фикстура для создания API клиента"""
        client = ProductApi(f"{BASE_URL}/search/product", TOKEN)
        return client
    
    @pytest.fixture
    def first_product_id(self, api_client):
        """Фикстура для получения ID первого товара в поиске"""
        response = api_client.search_product("книга", limit=1)
        assert response.status_code == 200
        
        response_json = response.json()
        product_ids = api_client.extract_product_ids(response_json)
        
        if not product_ids:
            pytest.skip("Не удалось получить ID товара для теста")
        
        return product_ids[0]
    
    @allure.story("Добавление в корзину")
    @allure.title("Добавление товара в корзину через API")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_to_cart_api(self, api_client, first_product_id):
        """Проверка добавления товара в корзину через API"""
        
        with allure.step(f"Добавить товар {first_product_id} в корзину"):
            response = api_client.add_to_cart(first_product_id, quantity=1)
        
        with allure.step("Проверить успешность добавления"):
            assert response.status_code in [200, 201], f"Не удалось добавить товар: {response.status_code}"
    
    @allure.story("Получение корзины")
    @allure.title("Получение содержимого корзины через API")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_cart_api(self, api_client):
        """Проверка получения содержимого корзины через API"""
        
        response = api_client.get_cart()
        
        assert response.status_code == 200, f"Не удалось получить корзину: {response.status_code}"
        
        # Проверяем структуру ответа
        response_json = response.json()
        assert response_json is not None, "Пустой ответ от API корзины"
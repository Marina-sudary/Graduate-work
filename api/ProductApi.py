import requests
import allure
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin


class ProductApi:
    """
    Класс для работы с API Читай-города
    """
    
    def __init__(self, base_url: str, token: str = None):
        """
        Инициализация API клиента
        
        Args:
            base_url: Базовый URL API
            token: Токен авторизации (если требуется)
        """
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.session = requests.Session()
        self.session.headers.update(self._get_headers())
    
    def _get_headers(self) -> Dict[str, str]:
        """Формирование заголовков для запросов"""
        headers = {
            "Content-type": "application/json",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def _make_url(self, path: str) -> str:
        """Формирование полного URL"""
        return urljoin(self.base_url, path.lstrip('/'))
    
    @allure.step("API: Поиск продуктов по фразе: {phrase}")
    def search_product(self, phrase: str, customer_city_id: int = 54, limit: int = 20) -> requests.Response:
        """
        Поиск продуктов по поисковой фразе
        
        Args:
            phrase: Поисковый запрос
            customer_city_id: ID города
            limit: Количество результатов
            
        Returns:
            Response объект
        """
        params = {
            "customerCityId": customer_city_id,
            "phrase": phrase,
            "limit": limit
        }
        
        response = self.session.get(self.base_url, params=params)
        
        # Прикрепляем информацию к Allure
        allure.attach(
            f"URL: {response.url}\nStatus: {response.status_code}",
            name="Request Info",
            attachment_type=allure.attachment_type.TEXT
        )
        allure.attach(response.text, "Response Body", allure.attachment_type.JSON)
        
        return response
    
    @allure.step("API: Извлечение названий книг из ответа")
    def extract_book_titles(self, response_json: Dict) -> List[str]:
        """
        Извлечение названий книг из JSON ответа
        
        Args:
            response_json: JSON ответ от API
            
        Returns:
            Список названий книг
        """
        titles = []
        
        # Проверяем разные возможные структуры ответа
        if 'included' in response_json:
            # Формат: { "included": [ { "type": "product", "attributes": { "title": ... } } ] }
            titles = [
                item['attributes']['title'] 
                for item in response_json.get('included', []) 
                if item.get('type') == 'product' and 'attributes' in item
            ]
        elif 'data' in response_json:
            # Формат: { "data": [ { "attributes": { "title": ... } } ] }
            titles = [
                item['attributes']['title'] 
                for item in response_json.get('data', []) 
                if 'attributes' in item
            ]
        elif isinstance(response_json, list):
            # Формат: прямой список продуктов
            titles = [
                item.get('title') or item.get('attributes', {}).get('title')
                for item in response_json
                if item
            ]
        
        # Фильтруем None значения
        titles = [title for title in titles if title]
        
        allure.attach(
            "\n".join([f"{i+1}. {title}" for i, title in enumerate(titles[:10])]),
            name="Extracted Titles (first 10)",
            attachment_type=allure.attachment_type.TEXT
        )
        
        return titles
    
    @allure.step("API: Извлечение ID продуктов из ответа")
    def extract_product_ids(self, response_json: Dict) -> List[str]:
        """
        Извлечение ID продуктов из JSON ответа
        
        Args:
            response_json: JSON ответ от API
            
        Returns:
            Список ID продуктов
        """
        product_ids = []
        
        if 'included' in response_json:
            product_ids = [
                item['id'] 
                for item in response_json.get('included', []) 
                if item.get('type') == 'product'
            ]
        elif 'data' in response_json:
            product_ids = [
                item['id'] 
                for item in response_json.get('data', [])
            ]
        
        return product_ids
    
    @allure.step("API: Добавление товара в корзину")
    def add_to_cart(self, product_id: str, quantity: int = 1) -> requests.Response:
        """
        Добавление товара в корзину через API
        
        Args:
            product_id: ID товара
            quantity: Количество
            
        Returns:
            Response объект
        """
        # Предполагаемый эндпоинт для добавления в корзину
        cart_url = self._make_url("/web/api/v2/cart/add")
        
        payload = {
            "productId": product_id,
            "quantity": quantity
        }
        
        response = self.session.post(cart_url, json=payload)
        
        allure.attach(
            f"Product ID: {product_id}, Quantity: {quantity}",
            name="Add to cart payload",
            attachment_type=allure.attachment_type.TEXT
        )
        
        return response
    
    @allure.step("API: Получение содержимого корзины")
    def get_cart(self) -> requests.Response:
        """
        Получение содержимого корзины через API
        
        Returns:
            Response объект
        """
        cart_url = self._make_url("/web/api/v2/cart")
        response = self.session.get(cart_url)
        
        allure.attach(response.text, "Cart Contents", allure.attachment_type.JSON)
        
        return response
    
    @allure.step("API: Очистка корзины")
    def clear_cart(self) -> requests.Response:
        """
        Очистка корзины через API
        
        Returns:
            Response объект
        """
        clear_url = self._make_url("/web/api/v2/cart/clear")
        response = self.session.post(clear_url)
        
        return response
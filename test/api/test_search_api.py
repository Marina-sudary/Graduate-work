import allure
import pytest
from api.ProductApi import ProductApi
from configuration.configProvider import configProvider

config = configProvider()

BASE_URL = config.get("api","base_url")
TOKEN = config.get("api","token")


@allure.epic("API тестирование сайта Читай-город")
@allure.feature("Поиск книг")
class TestBookSearch:
    
    @pytest.fixture(scope="class")
    def api_client(self):
        """Фикстура для создания API клиента"""
        client = ProductApi(BASE_URL, TOKEN)
        return client
    
    @allure.story("Поиск по названию")
    @allure.title("Поиск книги по точному названию")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_book_by_exact_title(self, api_client):
        """Проверка поиска книги по точному названию"""
        search_query = "Капитанская дочка"
        
        with allure.step(f"Выполнить поиск по запросу: {search_query}"):
            response = api_client.search_product(search_query)
        
        with allure.step("Проверить статус ответа"):
            assert response.status_code == 200, f"Ожидался код 200, получен {response.status_code}"
        
        with allure.step("Проверить наличие книги в результатах"):
            response_json = response.json()
            book_titles = api_client.extract_book_titles(response_json)
            
            assert book_titles, "Список книг пуст"
            
            # Проверяем, что искомая книга есть в результатах
            found = any(search_query.lower() in title.lower() for title in book_titles)
            assert found, f"Книга '{search_query}' не найдена в результатах поиска"
    
    @allure.story("Поиск по названию")
    @allure.title("Поиск книги по части названия")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_book_by_partial_title(self, api_client):
        """Проверка поиска книги по части названия"""
        search_query = "капитанская"
        
        response = api_client.search_product(search_query)
        assert response.status_code == 200
        
        response_json = response.json()
        book_titles = api_client.extract_book_titles(response_json)
        
        # Проверяем, что хотя бы одна книга содержит часть названия
        found = any(search_query.lower() in title.lower() for title in book_titles)
        assert found, f"Книги с '{search_query}' в названии не найдены"
    
    @allure.story("Поиск по автору")
    @allure.title("Поиск книги по имени автора")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_book_by_author(self, api_client):
        """Проверка поиска книги по имени автора"""
        search_query = "Пушкин"
        
        response = api_client.search_product(search_query)
        assert response.status_code == 200
        
        response_json = response.json()
        book_titles = api_client.extract_book_titles(response_json)
        
        # Проверяем, что книги автора присутствуют
        assert book_titles, "Книги не найдены"
        
        # Дополнительно можно проверить, что в названиях есть упоминание автора
        # или что автор указан в метаданных (зависит от структуры ответа)
        allure.attach(
            f"Найдено книг: {len(book_titles)}",
            name="Search results count",
            attachment_type=allure.attachment_type.TEXT
        )
    
    @allure.story("Пустой поиск")
    @allure.title("Поиск с пустым запросом")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_with_empty_query(self, api_client):
        """Проверка поиска с пустым запросом"""
        response = api_client.search_product("")
        
        # Ожидаем либо 400 Bad Request, либо 200 с пустым результатом
        # Это зависит от реализации API
        assert response.status_code in [200, 400], f"Неожиданный статус код: {response.status_code}"
    
    @allure.story("Поиск с лимитом")
    @allure.title("Поиск с ограничением количества результатов")
    @allure.severity(allure.severity_level.NORMAL)
    def test_search_with_limit(self, api_client):
        """Проверка параметра limit в поиске"""
        search_query = "книга"
        limit = 5
        
        response = api_client.search_product(search_query, limit=limit)
        assert response.status_code == 200
        
        response_json = response.json()
        book_titles = api_client.extract_book_titles(response_json)
        
        # Проверяем, что количество результатов не превышает лимит
        assert len(book_titles) <= limit, f"Получено {len(book_titles)} результатов, хотя лимит {limit}"
        
        allure.attach(
            f"Запрошено: {limit}, получено: {len(book_titles)}",
            name="Results count",
            attachment_type=allure.attachment_type.TEXT
        )
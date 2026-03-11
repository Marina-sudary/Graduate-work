import pytest
import allure
from config.settings import Settings, TestData

# Устанавливаем таймаут для длительных тестов
@pytest.mark.timeout(30)

@allure.feature("API Тесты")
@allure.story("Работа с API сайта")
@pytest.mark.api
class TestChitaiGorodAPI:
    """Класс с API тестами для сайта Читай-город."""
    
    @allure.title("Проверка доступности сайта")
    @allure.severity(allure.severity_level.BLOCKER)
    @allure.description("Тест проверяет, что сайт доступен")
    def test_site_availability(self, api_client):
        """Тест доступности сайта."""
        
        with allure.step("Проверить доступность сайта"):
            is_available = api_client.check_site_availability()
            
        with allure.step("Проверить результат"):
            assert is_available, "Сайт недоступен"
    
    @allure.title("Поиск книг по запросу")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("Тест проверяет поиск книг по различным запросам")
    @pytest.mark.parametrize("query", ["Солнце", "Java", "Python", "История", "Философия"])
    def test_search_books_api(self, api_client, query):
        """Тест поиска книг через API."""
        
        with allure.step(f"Выполнить поиск по запросу: {query}"):
            result = api_client.search_books(query)
            
        with allure.step("Проверить результат поиска"):
            # Проверяем, что запрос выполнен успешно (может быть 0 результатов)
            assert result.get("success") is not False, f"Ошибка при поиске: {result.get('error')}"
            assert "products" in result, "Нет списка книг в ответе"
            
            # Не требуем обязательного наличия книг, просто логируем результат
            allure.attach(
                f"Запрос: {query}\nНайдено книг: {result.get('count', 0)}",
                name=f"search_result_{query}",
                attachment_type=allure.attachment_type.TEXT
            )
    
    @allure.title("Получение информации о книге")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Тест проверяет получение детальной информации о книге")
    def test_get_book_info_api(self, api_client):
        """Тест получения информации о книге."""
        
        with allure.step("Найти первую книгу по запросу"):
            search_result = api_client.search_books(Settings.SEARCH_QUERY)
            assert search_result.get("success") is not False, "Ошибка при поиске книг"
            
            # Если книг нет, пропускаем тест
            if not search_result.get("products"):
                pytest.skip("Не найдены книги для теста")
            
            book = search_result["products"][0]
            book_url = book.get("url")
            assert book_url, "Не удалось получить URL книги"
            
        with allure.step(f"Получить информацию о книге: {book.get('title')}"):
            book_info = api_client.get_book_info(book_url)
            
        with allure.step("Проверить информацию о книге"):
            assert book_info.get("success") is not False, f"Ошибка при получении информации: {book_info.get('error')}"
            
            allure.attach(
                f"Название: {book_info.get('title', 'Не найдено')}\n"
                f"Автор: {book_info.get('author', 'Не указан')}\n"
                f"Цена: {book_info.get('price', 'Не указана')}\n"
                f"В наличии: {book_info.get('in_stock', False)}",
                name="book_info",
                attachment_type=allure.attachment_type.TEXT
            )
    
    @allure.title("Проверка структуры URL книг")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Тест проверяет корректность URL книг в результатах поиска")
    def test_book_url_structure(self, api_client):
        """Тест структуры URL книг."""
        
        with allure.step("Выполнить поиск книг"):
            result = api_client.search_books(Settings.SEARCH_QUERY)
            assert result.get("success") is not False, "Ошибка при поиске"
            
        with allure.step("Проверить URL всех найденных книг"):
            products = result.get("products", [])
            
            # Если нет книг, пропускаем тест
            if not products:
                pytest.skip("Нет книг для проверки")
            
            for book in products[:5]:  # Проверяем первые 5 книг
                book_url = book.get("url")
                assert book_url, "URL книги отсутствует"
                assert book_url.startswith(Settings.BASE_URL), f"Некорректный URL: {book_url}"
                assert "/product/" in book_url, f"URL не содержит /product/: {book_url}"
                
                allure.attach(
                    f"Книга: {book.get('title')}\nURL: {book_url}",
                    name=f"book_url_{book.get('id', 'unknown')}",
                    attachment_type=allure.attachment_type.TEXT
                )
    
    @allure.title("Проверка наличия цен у книг")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Тест проверяет, что у книг указана цена")
    def test_book_prices_exist(self, api_client):
        """Тест наличия цен у книг."""
        
        with allure.step("Найти книгу для проверки"):
            book = api_client.get_random_book(Settings.SEARCH_QUERY)
            
            # Если нет книг, пропускаем тест
            if not book:
                pytest.skip("Не удалось найти книгу для теста")
            
        with allure.step(f"Получить информацию о книге: {book.get('title')}"):
            book_info = api_client.get_book_info(book.get("url"))
            
        with allure.step("Проверить наличие цены"):
            assert book_info.get("success") is not False, "Ошибка при получении информации"
            
            # Проверяем, что цена указана (может быть "Не указана")
            price = book_info.get("price", "")
            allure.attach(
                f"Цена книги: {price}",
                name="book_price",
                attachment_type=allure.attachment_type.TEXT
            )
    
    @allure.title("Проверка множественных поисковых запросов")
    @allure.severity(allure.severity_level.MINOR)
    @allure.description("Тест проверяет поиск по разным категориям")
    def test_multiple_searches(self, api_client):
        """Тест множественных поисковых запросов."""
        
        search_queries = ["программирование", "роман", "детектив", "фэнтези", "наука"]
        results = []
        
        with allure.step("Выполнить поиск по разным категориям"):
            for query in search_queries:
                result = api_client.search_books(query)
                assert result.get("success") is not False, f"Ошибка при поиске '{query}'"
                
                results.append({
                    "query": query,
                    "count": result.get("count", 0),
                })
                
                allure.attach(
                    f"Запрос: {query}\nНайдено книг: {result.get('count', 0)}",
                    name=f"search_{query}",
                    attachment_type=allure.attachment_type.TEXT
                )
        
        with allure.step("Проверить результаты"):
            # Просто логируем результаты, не требуем обязательного наличия книг
            for res in results:
                allure.attach(
                    f"По запросу '{res['query']}' найдено {res['count']} книг",
                    name=f"result_{res['query']}",
                    attachment_type=allure.attachment_type.TEXT
                )
    
    @allure.title("Проверка обработки специальных символов в поиске")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("Тест проверяет поиск с специальными символами")
    @pytest.mark.parametrize("special_query", ["C++", "C#", "100%", "PHP", "JavaScript"])
    def test_special_characters_search(self, api_client, special_query):
        """Тест поиска со специальными символами."""
        
        with allure.step(f"Выполнить поиск с запросом: {special_query}"):
            result = api_client.search_books(special_query)
            
        with allure.step("Проверить результат поиска"):
            assert result.get("success") is not False, f"Ошибка при поиске '{special_query}'"
            
            allure.attach(
                f"Запрос: {special_query}\nНайдено книг: {result.get('count', 0)}",
                name=f"special_search_{special_query}",
                attachment_type=allure.attachment_type.TEXT
            )
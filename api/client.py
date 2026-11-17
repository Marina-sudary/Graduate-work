import allure
import requests
import re
from typing import Dict, Optional, Any
from config.settings import Settings
import logging
import time

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChitaiGorodAPI:
    """API клиент для взаимодействия с сайтом Читай-город."""

    def __init__(self, base_url: str = Settings.BASE_URL):
        """
        Инициализация API клиента.
        Args:
            base_url: Базовый URL сайта
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
        })

        # Добавляем задержку между запросами
        self.last_request_time = 0
        self.request_delay = 1  # Задержка в секунду между запросами

    def _rate_limit(self):
        """Ограничение частоты запросов."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.request_delay:
            time.sleep(self.request_delay - time_since_last)
        self.last_request_time = time.time()

    @allure.step("Поиск книг по запросу: {query}")
    def search_books(self, query: str) -> Dict[str, Any]:
        """
        Поиск книг по запросу (через HTML парсинг).
        Args:
            query: Поисковый запрос
        Returns:
            Dict: Результаты поиска
        """
        # Ограничиваем частоту запросов
        self._rate_limit()

        try:
            # Выполняем поиск через GET запрос к основной странице
            url = f"{self.base_url}/search"
            params = {"phrase": query}

            logger.info(f"Поиск по URL: {url} с параметрами: {params}")

            # Добавляем таймаут
            response = self.session.get(
                url,
                params=params,
                timeout=10,  # Таймаут 10 секунд
                allow_redirects=True
            )
            response.raise_for_status()

            # Получаем HTML
            html = response.text

            # Прикрепляем HTML к отчету (только небольшой фрагмент)
            allure.attach(
                html[:2000],  # Только первые 2000 символов
                name=f"search_html_{query}",
                attachment_type=allure.attachment_type.HTML
            )

            # Упрощенный парсинг для скорости
            products = []

            # Простой поиск ссылок на товары (более быстрый)
            # Ищем все ссылки, содержащие /product/
            product_links = re.findall(r'href="(/product/\d+)"', html)
            product_titles = re.findall(r'<a[^>]*class="product-card__title"[^>]*>(.*?)</a>', html, re.DOTALL)

            # Ограничиваем количество результатов для скорости
            max_results = min(10, len(product_links))
            seen_ids = set()

            for i in range(max_results):
                if i < len(product_links):
                    link = product_links[i]
                    product_id_match = re.search(r'/product/(\d+)', link)
                    if product_id_match:
                        product_id = product_id_match.group(1)
                        if product_id not in seen_ids:
                            seen_ids.add(product_id)

                            # Получаем название
                            title = f"Книга {i+1}"
                            if i < len(product_titles):
                                title = re.sub(r'<[^>]+>', '', product_titles[i]).strip()

                            products.append({
                                "id": product_id,
                                "title": title,
                                "url": f"{self.base_url}{link}"
                            })

            # Если не нашли через простой метод, пробуем расширенный
            if not products:
                # Ищем карточки товаров
                product_pattern = r'data-product-id="(\d+)"'
                product_ids = re.findall(product_pattern, html)

                for i, product_id in enumerate(product_ids[:10]):
                    products.append({
                        "id": product_id,
                        "title": f"Книга {i+1}",
                        "url": f"{self.base_url}/product/{product_id}"
                    })

            logger.info(f"Найдено продуктов: {len(products)}")

            return {
                "success": True,
                "query": query,
                "products": products,
                "count": len(products)
            }

        except requests.exceptions.Timeout:
            logger.error(f"Таймаут при поиске: {query}")
            allure.attach(
                f"Timeout for query: {query}",
                name="Timeout Error",
                attachment_type=allure.attachment_type.TEXT
            )
            return {
                "success": False,
                "error": "Request timeout",
                "products": []
            }
        except requests.exceptions.ConnectionError:
            logger.error(f"Ошибка соединения при поиске: {query}")
            return {
                "success": False,
                "error": "Connection error",
                "products": []
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при поиске: {e}")
            allure.attach(
                str(e)[:200],
                name="API Error",
                attachment_type=allure.attachment_type.TEXT
            )
            return {
                "success": False,
                "error": str(e)[:100],
                "products": []
            }
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}")
            return {
                "success": False,
                "error": f"Unexpected error",
                "products": []
            }

    @allure.step("Получение информации о книге по URL: {book_url}")
    def get_book_info(self, book_url: str) -> Dict[str, Any]:
        """
        Получение информации о конкретной книге.
        Args:
            book_url: URL книги
            Returns:
            Dict: Информация о книге
        """
        # Ограничиваем частоту запросов
        self._rate_limit()

        try:
            logger.info(f"Получение информации о книге: {book_url}")

            response = self.session.get(book_url, timeout=10)
            response.raise_for_status()

            html = response.text

            # Упрощенный парсинг
            # Название
            title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
            title = title_match.group(1).strip() if title_match else "Не найдено"
            title = re.sub(r'<[^>]+>', '', title)[:100]  # Ограничиваем длину

            # Цена (упрощенно)
            price_match = re.search(r'(\d+[ \d]*[₽руб]+)', html)
            price = price_match.group(1).strip() if price_match else "Не указана"

            # Наличие
            in_stock = "В корзину" in html or "Купить" in html

            result = {
                "success": True,
                "url": book_url,
                "title": title,
                "price": price,
                "in_stock": in_stock
            }

            logger.info(f"Информация о книге получена")
            return result

        except requests.exceptions.Timeout:
            logger.error(f"Таймаут при получении информации о книге")
            return {
                "success": False,
                "error": "Request timeout"
            }
        except Exception as e:
            logger.error(f"Ошибка при получении информации о книге: {e}")
            return {
                "success": False,
                "error": str(e)[:100]
            }

    @allure.step("Проверка доступности сайта")
    def check_site_availability(self) -> bool:
        """
        Проверка доступности сайта.
        Returns:
            bool: Доступен ли сайт
        """
        try:
            response = self.session.get(self.base_url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Сайт недоступен: {e}")
            return False

    @allure.step("Получение случайной книги из результатов поиска")
    def get_random_book(self, query: str = "книга") -> Optional[Dict[str, Any]]:
        """
        Получение случайной книги из результатов поиска.
        Args:
            query: Поисковый запрос
        Returns:
            Optional[Dict]: Информация о книге или None
        """
        search_result = self.search_books(query)

        if search_result.get("success") and search_result.get("products"):
            import random
            products = search_result["products"]
            if products:
                return random.choice(products)

        return None

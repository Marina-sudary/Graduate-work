import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import pytest
from selenium import webdriver
import allure
from page.search_page import SearchPage

from time import sleep


@pytest.fixture(scope="session")
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    yield driver
    driver.quit()


@pytest.fixture
def search_page(driver):
    page = SearchPage(driver)
    page.open("https://www.chitai-gorod.ru/")
    sleep(5)
    return page


@allure.epic("UI тестирование сайта Читай-город")
@allure.feature("Поиск")
class TestSearchUI:
    
    @allure.title("Поиск книги по названию")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_book_by_title(self, search_page):
        with allure.step("Ввести запрос на поиск книги по названию"):
            search_page.enter_search_query("Капитанская дочка")
            sleep(5)
        with allure.step("Нажать кнопку поиска"):
            search_page.click_search_button()
        with allure.step("Получить заголовки книг"):
            product_titles = search_page.get_product_titles()
        assert any("Капитанская дочка" in title for title in product_titles), \
            "Название книги не найдено в списке книг"

    @allure.title("Поиск книги по автору")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_search_book_by_author(self, search_page):
        with allure.step("Ввести запрос на поиск книги по имени автора"):
            search_page.enter_search_query("Пушкин")
            sleep(5)
        with allure.step("Нажать кнопку поиска"):
            search_page.click_search_button()
        with allure.step("Получить заголовки книг"):
            product_titles = search_page.get_product_titles()
        assert any("Пушкин" in title for title in product_titles), \
            "Название книги не найдено в списке книг"
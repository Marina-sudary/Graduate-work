from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
import allure
from page.BasePage import BasePage


class SearchPage(BasePage):
    def __init__(self, driver: WebDriver, timeout: int = 10) -> None:
        super().__init__(driver, timeout)
        self.__url = self.base_url

    @allure.step("Открыть стартовую страницу")
    def go(self):
        self.__driver.get(self.__url)

    @allure.step("Ввод поискового запроса '{query}'")
    def enter_search_query(self, query):
        """Ввод текстового сообщения в поле поиска
           Args: query(str): запрос для поиска"""
        search_input = self.wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".search-form__input")))
        search_input.send_keys(query)

    @allure.step("Нажатие кнопки поиска")
    def click_search_button(self):
        """Нажатие на кнопку поиска"""
        search_button = self.wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".search-form__icon-search")))
        search_button.click()

    @allure.step("Получение названий книг")
    def get_product_titles(self):
        """Получение названий всех книг на странице результатов поиска
           Returns list: список названий книг"""
        self.wait.until(EC.visibility_of_all_elements_located(
            (By.CSS_SELECTOR, ".product-card__title")))
        product_elements = self.driver.find_elements(By.CSS_SELECTOR,
                                                     ".product-card__title")
        return [product.text.strip() for product in product_elements]

    @allure.step("Получение названий авторов")
    def get_author_titles(self):
        """Получение имён всех авторов на странице результатов поиска
            Returns list: список имён авторов"""
        self.wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, ".product-card__subtitle")))
        author_elements = self.driver.find_elements(By.CSS_SELECTOR,
                                                    ".product-card__subtitle")
        return [author.text.strip() for author in author_elements]

    @allure.step("Проверка сообщения об отсутствии результатов")
    def check_no_result_message(self):
        """Проверить и вернуть сообщение об отсутствии результатов поиска
                    Returns(str): сообщение об отсутствии результатов"""
        self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".catalog-stub__description")))
        no_results_message = self.driver.find_element(
            By.CSS_SELECTOR, ".catalog-stub__description")
        return no_results_message.text
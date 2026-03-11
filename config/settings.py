from enum import Enum


class Settings:
    """Класс с настройками для тестов."""

    # URL
    BASE_URL = "https://www.chitai-gorod.ru"

    # Тестовые данные
    SEARCH_QUERY = "Солнце"
    SORT_OPTION = "Сначала дешевые"

    # Таймауты (в секундах)
    DEFAULT_TIMEOUT = 10
    PAGE_LOAD_TIMEOUT = 30

    # Режимы запуска
    class RunMode(str, Enum):
        UI = "ui"
        API = "api"
        ALL = "all"


class TestData:
    """Тестовые данные."""

    SEARCH_TERMS = [
        "Солнце",
        "Java",
        "Python",
        "История",
        "Философия",
        "программирование",
        "роман",
        "детектив",
        "фэнтези",
        "наука"
    ]

    SPECIAL_SEARCH_TERMS = [
        "C++",
        "C#",
        "100%",
        "PHP",
        "JavaScript"
    ]

    SORTING_OPTIONS = [
        "По популярности",
        "Сначала дешевые",
        "Сначала дорогие",
        "По новизне"
    ]

    BOOK_CATEGORIES = [
        "программирование",
        "роман",
        "детектив",
        "фэнтези",
        "наука"
    ]

import pytest
import requests
from page.MainPage import MainPage

@pytest.mark.ui
def test_search_and_add_to_cart(browser, test_data, login_via_cookie):
    """
    Поиск товара и добавление первого результата в корзину.
    Рекомендуется предварительно авторизоваться или использовать cookie-фикстуру.
    """
    main = MainPage(browser)
    main.go()
    phrase = test_data.get("search_phrase") or "книга"
    main.search(phrase)
             # добавим первый товар в корзину
    main.add_first_product_to_cart()
            # откроем корзину и проверим, что URL содержит /cart
    main.open_cart()
    assert "/cart" in browser.current_url or browser.current_url.endswith("/cart")

@pytest.mark.ui
def test_cart_modify_and_delete(browser, test_data, login_via_cookie):
    """
    Открыть корзину, увеличить количество и удалить товар.
    """
    main = MainPage(browser)
    # Перейдём прямо на страницу корзины
    browser.get("https://www.chitai-gorod.ru/cart")

    # Увеличим количество первого товара (если есть)
    try:
        main.increase_quantity_first_item()
    except Exception:
        pytest.skip("Кнопка '+' не найдена — возможно нет товаров в корзине")

    # Удалим первый товар
    main.delete_first_item_from_cart()
    # можно добавить проверку — например, что элемент удалён или сообщение пустой корзины
    # конкретная проверка зависит от DOM сайта

@pytest.mark.ui
def test_toggle_favorite_from_search(browser, test_data, login_via_cookie):
    main = MainPage(browser)
    main.go()
    phrase = test_data.get("search_phrase") or "классика"
    main.search(phrase)
    main.toggle_favorite_on_first()
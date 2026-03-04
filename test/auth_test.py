import pytest
from page.AuthPage import AuthPage
from page.MainPage import MainPage

@pytest.mark.ui
def test_ui_login_flow_using_otp(browser, test_data):
    """
    Полный UI сценарий: открыть модал, ввести телефон, получить код (нажать кнопку),
    ввести OTP, при необходимости заполнить регистрацию.
    Если у вас нет живого OTP, используйте test_login_using_cookie.
    """
    auth = AuthPage(browser)
    auth.go()
    auth.open_auth_modal()

    phone = test_data.get("telephone")
    if not phone:
        pytest.skip("Telephone not provided in test data")

    auth.enter_phone(phone)
    auth.click_get_code()

    otp = test_data.get("otp")
    if not otp:
        pytest.skip("OTP not provided in test data; use cookie login instead")

    auth.enter_otp(otp)

    # Если после ввода OTP требуется регистрация — можно заполнить:
    first = test_data.get("first_name")
    last = test_data.get("last_name")
    mail = test_data.get("email")
    if first and last and mail:
        auth.fill_registration(first, last, mail, accept_age=True)
        auth.click_register()

    main = MainPage(browser)
    # Проверка: после входа можно открыть меню или профиль
    main.go()
    # простая проверка — текущий URL содержит базовый домен (или другое ожидание).
    assert browser.current_url.startswith("https://www.chitai-gorod.ru")

@pytest.mark.ui
def test_login_using_cookie(browser, login_via_cookie):
    """
    Альтернативный способ: если у вас есть токен, подставьте cookie в test_data.json и используйте этот тест.
    """
    main = MainPage(browser)
    main.go()
    # Можно открыть меню профиля или корзину как проверку авторизации
    main.open_cart()
    # проверка — открылась страница корзины или показан попап
    assert "cart" in browser.current_url or "/cart" in browser.current_url
# Дипломная работа

## План работы

### Шаги

1. Склонировать проект `git clone https://github.com/Marina-sudary/Diplom`.
2. Установить зависимости `pip install > -r requirements.txt`.
3. Запустить тесты `pytest`:
    - при авторизации вписать телефон и полученный из смс код.
4. Сгенерировать отчет `allure generate allure-files -o allure-report`.
5. Открыть отчет `allure open allure-report`.

### Стек

- pytest
- selenium
- webdriver manager
- requests
- _sqlalchemy_
- allure
- configparser
- json

### Структура

- ./test - тесты
- ./pages - описание страниц
- ./api - хелперы для работы с API
- ./configuration - провайдер настроек
  - test_config.ini - настройки для тестов
- ./testdata - провайдер тестовых данных
  - test_data.json

### Полезные ссылки

- [Подсказка по markdown](https://www.markdownguide.org/basic-syntax/)
- [Подсказка  по ./gitignore](https://www.toptal.com/developers/gitignore)
- [Про configparser](https://docs.python.org/3/library/configparser.html#modul-configparser)
- [Про pip freeze](https://pip.pypa.io/en/stable/cli/pip_freeze/)

#### Подсказки

- при авторизации указать реальные данные пользователя
- ввести полученный при авторизации код

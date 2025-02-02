from selenium import webdriver
from datetime import datetime
import typing
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import time

# Web драйвер
global driver
# Контенер, где находятся все игры (div class="container") (для сокращения времени поиска)
global container

# Получить DOM дерево страницы
def get_page(url: str) -> None:
    global driver
    # Опции оптимизации загрузки
    options = webdriver.ChromeOptions()
    options.add_argument('-no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument("disable-infobars")
    options.add_argument('-disable-dev-shm-usage')
    options.add_argument("--disable-extensions")
    # options.add_argument("--start-maximized")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_experimental_option('excludeSwitches', ['disable-popup-blocking'])
    options.add_experimental_option("prefs", {
        "profile.managed_default_content_settings.images": 2,
        'media_stream': 2,
    })
    driver = webdriver.Chrome(options)

    driver.maximize_window() # Полноэкранный режим
    time.sleep(1)  # Время доп. ожидания загрузки, сек
    driver.get(url) # Запрос получения страниц

    print('Страница получена')

# Проячем окно уведомления и кукисов
def close_dialogs() -> None:
    # Кнопка куки
    cookie_buttons = driver.find_elements(By.CLASS_NAME, 'cookie-modal__button')
    if len(cookie_buttons) > 0: cookie_buttons[0].click()
    # Кнопка уведомленния
    confirm_buttons = driver.find_elements(By.CLASS_NAME, 'push-confirm__button')
    if len(confirm_buttons) > 0: confirm_buttons[0].click()

    time.sleep(0.5)

    print('Диалоги закрыты')

# Очистка текста
def clean_text(value: str) -> str:
    return value.strip().replace('\n', ' ').replace('  ', ' ').replace('  ', ' ')

# Имя сохраняемых файлов
def get_filename() -> str:
    current_date_time = datetime.now()
    time_stamp = current_date_time.strftime('%m.%d.%y %H.%M.%S')
    return 'result_' + time_stamp

# Парсинг строк таблицы блока
def get_rows(element: WebElement, block_name: str) -> typing.List[str]:
    rows = []
    print('  - ' + block_name)

    # Поиск заголовка
    header = element.find_element(By.XPATH, "//span[text()='" + block_name + "']")
    if header is None:
        print('Пусто')
        return rows

    # Поиск списка строк
    block = header.find_element(By.XPATH, '..//..')
    table = block.find_elements(By.CLASS_NAME, 'dops-item-row__section')

    # Считываем строки
    for row in table:
        row_text = (clean_text(row.text)
                    .replace(' (', '(')
                    .replace('Не забьет', 'Незабьет')
                    .replace('Не будет', 'Небудет')
                    .replace('Нет голов', 'Нетголов'))

        # Если заголовок состоит из двух колонок (например, Тотал)
        # То их объединяем
        cols = row_text.split(' ')
        try:
            float(cols[1])
        except ValueError:
            cols[0] = cols[0] + cols[1]
            del cols[1]

        # 1 колонка
        header1 = cols[0]
        value1 = cols[1]
        rows.append(header1)
        rows.append(value1)
        print_value = header1 + ': ' + value1

        # 2 колонка
        if len(cols) > 3:
            header2 = cols[2]
            value2 = cols[3]
            rows.append(header2)
            rows.append(value2)
            print_value = print_value + ' | ' + header2 + ': ' + value2

        # 3 колонка
        if len(cols) > 5:
            header3 = cols[4]
            value3 = cols[5]
            rows.append(header3)
            rows.append(value3)
            print_value = print_value + ' | ' + header3 + ': ' + value3

        print('     ' + print_value)

    return rows

# Значение в строке по названию
def get_value(rows: typing.List[str], name: str) -> str:
    cell_index = rows.index(name)
    return rows[cell_index + 1]

# Клик по элементу
def click(element: WebElement) -> None:
    driver.execute_script("arguments[0].click();", element)

# Контейнер игр
def get_container() -> None:
    global container
    container = driver.find_element(By.CLASS_NAME, 'container')
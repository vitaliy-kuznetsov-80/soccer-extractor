from selenium import webdriver
from selenium.webdriver import Chrome
from datetime import datetime
import typing
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

# Получить DOM дерево страницы
def get_page(url: str, is_screenshot: bool, filename: str) -> Chrome:
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
    driver.implicitly_wait(5)  # Время доп. ожидания загрузки, сек
    driver.get(url) # Запрос получения страниц

    print('Страница получена')

    # Скриншот
    if is_screenshot:
        driver.save_screenshot(filename + '.png')

    return driver

# Проячем окно уведомления и кукисов
def close_dialogs(driver: Chrome) -> None:
    # Кнопка куки
    cookie_button = driver.find_elements(By.CLASS_NAME, 'cookie-modal__button')[0]
    cookie_button.click()
    # Кнопка уведомленния
    confirm_button = driver.find_elements(By.CLASS_NAME, 'push-confirm__button')[0]
    confirm_button.click()

# Очистка текста
def clean_text(value: str) -> str:
    return value.strip().replace('\n', ' ').replace('  ', ' ').replace('  ', ' ')

# Имя сохраняемых файлов
def get_filename() -> str:
    current_date_time = datetime.now()
    time_stamp = current_date_time.strftime('%m.%d.%y %H.%M.%S')
    return 'result_' + time_stamp

# Парсинг строк таблицы блока
def get_rows(driver: Chrome, block_name: str) -> typing.List[str]:
    rows = []
    print('---' + block_name + '---')

    # Поиск заголовка
    header = driver.find_element(By.XPATH, "//span[starts-with(., '" + block_name + "')]")
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

        print(print_value)

    return rows

# Значение в строке по названию
def get_value(rows: typing.List[str], name: str) -> str:
    cell_index = rows.index(name)
    return rows[cell_index + 1]

# Клик по элементу
def click(driver: Chrome, element: WebElement) -> None:
    driver.execute_script("arguments[0].click();", element)
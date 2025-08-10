"""Утилитные функции"""

import time
import re
from datetime import datetime
from typing import Union
import typing
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.ie.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Web драйвер
driver: Union[WebDriver, None] = None
# Контенер, где находятся все игры (div class="container") (для сокращения времени поиска)
container: Union[WebElement, None] = None

def get_page(url: str) -> None:
    """Получить DOM дерево страницы"""
    global driver
    # Опции оптимизации загрузки
    options = webdriver.ChromeOptions()
    options.add_argument('-no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument("disable-infobars")
    options.add_argument('-disable-dev-shm-usage')
    options.add_argument("--disable-extensions")
    options.add_argument("--blink-settings=imagesEnabled=false")
    options.add_experimental_option('excludeSwitches', ['disable-popup-blocking'])
    options.add_experimental_option("prefs", {
        "profile.managed_default_content_settings.images": 2,
        'media_stream': 2,
    })
    driver = webdriver.Chrome(options)
    driver.maximize_window() # Полноэкранный режим

    driver.set_page_load_timeout(10) # Тамаут принудительной оставновки загрузки
    try:
        driver.get(url) # Запрос получения страниц
    except TimeoutException:
        print('Принудительная остановка')
        driver.execute_script("window.stop();")
    print('Страница получена')

def close_dialogs() -> None:
    """Прячем окно уведомления и кукисов"""
    # Кнопка куки
    try:
        cookie_buttons = driver.find_elements(By.CLASS_NAME, 'cookie-modal__button')
        if len(cookie_buttons) > 0:
            cookie_buttons[0].click()
    except NoSuchElementException:
        print('Кнопка куки не найдена')

    # Кнопка уведомленния
    try:
        confirm_buttons = driver.find_elements(By.CLASS_NAME, 'push-confirm__button')
        if len(confirm_buttons) > 0:
            confirm_buttons[0].click()
    except NoSuchElementException:
        print('Кнопка уведомленния не найдена')

    time.sleep(0.5)
    print('Диалоги закрыты')

def clean_text(value: str) -> str:
    """Очистка текста"""
    return value.strip().replace('\n', ' ').replace('  ', ' ').replace('  ', ' ')

def get_filename() -> str:
    """Имя сохраняемых файлов"""
    current_date_time = datetime.now()
    time_stamp = current_date_time.strftime('%m.%d.%y %H.%M.%S')
    return '_' + time_stamp

def get_rows(element: WebElement, block_name: str, col_count: int, block_column: str = '') -> typing.List[str]:
    """Парсинг строк таблицы блока"""
    rows = []
    print('  - ' + block_name)

    # Поиск заголовка
    try:
        header = element.find_element(By.XPATH, "//span[text()='" + block_name + "']")
    except NoSuchElementException:
        print('Таблица "' + block_name + '" не найдена')
        return rows

    block: WebElement = header.find_element(By.XPATH, '..//..')

    # Если строки объедены в блоки (напрмиер, Исходы по таймам)
    if block_column != '':
        try:
            path_prefix = "//div[contains(@class, 'dops-item-row')]//div[contains(@class, 'dops-item-row__title')]"
            path = path_prefix + "//span[contains(text(),'" + block_column + "')]"
            table_column = block.find_element(By.XPATH, path)
            block = table_column.find_element(By.XPATH, '..//..')
        except NoSuchElementException:
            print('Блок "' + block_column + '" в таблице "' + block_name + '" не найден')
            return rows

    # Поиск списка строк
    table = block.find_elements(By.CLASS_NAME, 'dops-item-row__section')

    # Считываем строки
    for row in table:
        row_text = (clean_text(row.text.strip())
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
        # Должна быть 2 колонка, но её нет
        if len(cols) < 3 and col_count == 2:
            header2 = ''
            value2 = ''
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
        # Должна быть 2 колонка, но её нет
        if len(cols) < 5 and col_count == 3:
            header3 = ''
            value3 = ''
            rows.append(header3)
            rows.append(value3)
            print_value = print_value + ' | ' + header3 + ': ' + value3

        print('     ' + print_value)

    return rows

def get_value(rows: typing.List[str], name: str) -> str:
    """Значение в строке по названию"""
    if name in rows:
        cell_index = rows.index(name)
        return rows[cell_index + 1]
    return ''

def click(element: WebElement) -> None:
    """Клик по элементу"""
    driver.execute_script("arguments[0].click();", element)

def get_container() -> None:
    """Контейнер игр"""
    global container
    container = driver.find_element(By.CLASS_NAME, 'container')

def get_id(tag: WebElement) -> str:
    """Последний Id в тэге - a"""
    a_tag = tag.get_attribute('href')
    return re.search('/ru/line/soccer/(.*)ts=24', a_tag).group(1)[:-1].strip()
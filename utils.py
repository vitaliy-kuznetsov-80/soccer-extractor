from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
import typing

base_url = 'https://betcity.ru/ru/line/soccer'

# Получить DOM дерево страницы
def get_page(line_game_id: str, is_screenshot: bool, filename: str) -> BeautifulSoup:
    # Опции оптимизации загрузки
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
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

    # Запрос
    url = base_url + '/' + line_game_id
    driver.get(url)

    print('Страница получена')

    # Скриншот
    if is_screenshot:
        driver.save_screenshot(filename + '.png')

    # Получение содержимого (DOM дерева)
    page_source = driver.page_source
    driver.quit()

    print('Страница распарсена')

    # Парсинг в объект
    return BeautifulSoup(page_source, 'html.parser')

# Очистка текста
def clean_text(value: str) -> str:
    return value.strip().replace('  ', ' ').replace('  ', ' ')

# Имя сохраняемых файлов
def get_filename(line_game_id: str) -> str:
    current_date_time = datetime.now()
    time_stamp = current_date_time.strftime('%m.%d.%y %H.%M.%S')
    return 'result_' + line_game_id.replace('/', '_') + '_' + time_stamp

# Парсинг строк таблицы блока
def get_rows(dom_tree: BeautifulSoup, block_name: str) -> typing.List[str]:
    rows = []
    print('---' + block_name + '---')

    # Поиск заголовка
    header = dom_tree.find('span', string=block_name)
    if header is None:
        print('Пусто')
        return rows

    # Поиск списка строк
    block = header.parent.parent
    table = block.find_all('div', class_="dops-item-row__section")

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
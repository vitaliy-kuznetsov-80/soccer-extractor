from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from xlrd import open_workbook
from xlutils.copy import copy
from datetime import datetime

import time
import re

from xlwt import Workbook, Worksheet

import utils as u
import params as p

# Список фраз - исключений
def get_ignore_list():
    file = open('ignore-soccer.txt', encoding='utf-8')
    ignore_list = file.read().splitlines()
    file.close()
    return ignore_list

# Пометка строк для получения игр
def mark_lines(limit_count):
    # Таблица парсинга. Берём только левую (СОБЫТИЯ)
    tables = u.container.find_elements(By.CLASS_NAME, 'champs__sport')[0]

    # Список строк линий
    rows = tables.find_elements(By.CLASS_NAME, 'champs__champ')
    print('Найдено линий: ' + str(len(rows)))

    # Фильтрация строк
    print('Фильтрованные линии: ')
    count = 0
    ignore_list = get_ignore_list() # Читаем слова-исключения из файла
    for row in rows:
        # Ограничние линий
        if 0 < limit_count < count: break

        # Ссылка на линию с названием
        a = row.find_element(By.CLASS_NAME, 'champs__champ-name')
        line_text = a.text.strip()

        # Игнор
        is_ignore = False
        for item in ignore_list:
            if line_text.find(item) > -1:
                is_ignore = True
                break
        if is_ignore:
            print('  - ' + line_text)
            continue

        print('  ' + line_text)

        # Пометка линии через щелчок по checkbox
        checkbox = row.find_element(By.CLASS_NAME, 'checkbox__mark')
        u.click(checkbox)

        count = count + 1
    print('Фильтрованых линий: ' + str(count))

# Загрузка игр для выбранных линий
def load_games():
    # Жмём "Показать" для отображения игр
    button_find = u.container.find_element(By.CLASS_NAME, 'line__controls-button')
    u.click(button_find)

    # Ждём загрузки игр
    WebDriverWait(u.driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, "line-event")))

# Парсинг игр
def parce_games(filename: str, game_limit: int, only_id: str):
    # Открытие шаблона Excel и создание копии
    rb = open_workbook("template.xls", formatting_info=True)
    wb: Workbook = copy(rb)
    sheet: Worksheet = wb.get_sheet(0)  # Первая книга
    excel_row_index = 2 # Первый индекс строки в Excel

    # Строки игр
    rows = u.container.find_elements(By.CLASS_NAME, 'line-event')
    row_count = len(rows)
    print('\nИгр в обработке: ' + str(row_count))

    button_prev_play = None  # Запоминаем предыдущую кнопку для закрытия, перед открытием нового
    count = 0
    for row in rows:
        # Ограничние игр
        if 0 < game_limit < count: break

        # Получение Id игры (для лога и отладки)
        a_elems = row.find_elements(By.TAG_NAME, 'a')
        id_href = a_elems[0].get_attribute('href')
        game_id = re.search('/ru/line/soccer/(.*)ts=24', id_href).group(1)[:-1]
        # Поиск конкртеной игры, если есть
        if only_id != '':
            if id_href.find(only_id) == -1: continue

        # Закрывем предыдущй
        if button_prev_play is not None:
            u.click(button_prev_play)
            time.sleep(1)

        write_left_header(excel_row_index, game_id, row, sheet)

        # Кнопка раскрытия игры
        button_play = row.find_element(By.CLASS_NAME, 'line-event__dops-toggle')
        if button_play.tag_name != 'button': continue  # Игнор не кнопок
        # Клик по раскрывашке (правая колонка)
        u.click(button_play)
        # Ожидаем прогрузки по названию таблицы нижней части коэффициентов (должна быть всегда)
        waiting_path = "//span[starts-with(., 'Тотал')]"
        WebDriverWait(u.driver, 10).until(ec.presence_of_element_located((By.XPATH, waiting_path)))

        # Парсинг игры
        header_line = p.get_header_params(row)

        # Получение и запись коэффициентов
        row_area = row.find_element(By.XPATH, '..')
        p.save_to_excel(row_area, header_line, sheet, excel_row_index)

        button_prev_play = button_play  # Запоминаем кнопку раскрытия
        excel_row_index = excel_row_index + 1
        count = count + 1

    wb.save('results/' + filename + '.xls')

# Левая шапка. Прлучение и запись в Excel
def write_left_header(excel_row_index: int, game_id: str, row: WebElement, sheet: Worksheet):
    # Время
    time_game = row.find_element(By.CLASS_NAME, 'line-event__time-static').text.strip()

    # Команды
    teams_block = row.find_element(By.CLASS_NAME, 'line-event__name-teams')
    teams = teams_block.find_elements(By.XPATH, './/*')
    team1 = teams[0].text.strip()
    team2 = teams[1].text.strip()

    # Блок игр по странам
    country_block: WebElement = row.find_element(By.XPATH, '..//..')

    # Игра
    game = (country_block.find_element(By.CLASS_NAME, 'line-champ__header-link').text
            .replace('Футбол.', '').strip())

    # Дата, Д/Н
    date_parce = country_block.find_element(By.CLASS_NAME, 'line-champ__date').text.strip()
    date_parce_list = date_parce.split(' ')
    date_number = int(date_parce_list[0].strip())
    months = ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']
    dws = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
    date_month = months.index(date_parce_list[1].strip()[:3].lower()) + 1
    date_year = datetime.now().year
    date_obj = datetime(date_year, date_month, date_number)
    # Если полученая дата > текущей даты, то это прошлый год (стык декабрь / январь)
    if date_obj > datetime.now():
        date_obj = datetime(date_year - 1, date_month, date_number)
    date_game = date_obj.strftime('%d.%m.%Y')  # Дата для отчёта
    dw = dws[date_obj.weekday()]  # День недели

    print('\n' + str(excel_row_index - 1) + ': ' +
          date_obj.strftime('%d.%m.%y') + ' ' + time_game + ': ' +
          game + ': ' + team1 + ' / ' + team2 + ': ' + game_id)

    # Сохранение в Excel
    sheet.write(excel_row_index, 0, date_game)
    sheet.write(excel_row_index, 1, dw)
    sheet.write(excel_row_index, 2, time_game)
    sheet.write(excel_row_index, 3, game)
    sheet.write(excel_row_index, 4, team1)
    sheet.write(excel_row_index, 5, team2)

# Выбор часового пояса МСК
def set_msk() -> None:
    # Кнопка настроек
    button_settings = u.driver.find_element(By.CLASS_NAME, 'sub-header__icon-settings')
    u.click(button_settings)

    # Ждём загрузки окна
    WebDriverWait(u.driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, "settings__body")))

    # Выбираем Москву
    body = u.driver.find_element(By.CLASS_NAME, 'settings__body')
    drop_down_item = body.find_element(By.XPATH, "//span[@class='select-dropdown__item' and contains(text(),'Москва')]")
    u.click(drop_down_item)
    time.sleep(1)

    # Сохраняем
    button_save = u.driver.find_element(By.CLASS_NAME, 'settings-footer-button_save')
    u.click(button_save)

    # Ждём загрузки контейнера
    time.sleep(1)
    WebDriverWait(u.driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, "container")))

    print('Выбран часовой пояс МСК')
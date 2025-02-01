from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver import Chrome

from xlrd import open_workbook
from xlutils.copy import copy
from datetime import datetime
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
def mark_lines(driver: Chrome):
    # Таблица парсинга. Берём только левую (СОБЫТИЯ)
    tables = driver.find_elements(By.CLASS_NAME, 'champs__sport')[0]

    # Список строк линий
    rows = tables.find_elements(By.CLASS_NAME, 'champs__champ')
    print('Найдено линий: ' + str(len(rows)))

    # Фильтрация строк
    print('Фильтрованные линии: ')
    count = 0
    ignore_list = get_ignore_list() # Читаем слова-исключения из файла
    for row in rows:
        # Ограничние линий
        if count > 1: break

        # Ссылка на линию с названием
        a = row.find_element(By.CLASS_NAME, 'champs__champ-name')
        line_text = a.text

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
        u.click(driver, checkbox)

        count = count + 1
    print('Фильтрованых линий: ' + str(count))

# Загрузка игр для выбранных линий
def load_games(driver: Chrome):
    # Жмём "Показать" для отображения игр
    find_button = driver.find_element(By.CLASS_NAME, 'line__controls-button')
    u.click(driver, find_button)

    # Ждём загрузки игр
    WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, "line-event")))

# Парсинг игр
def parce_games(driver: Chrome, filename: str):
    # Открытие шаблона Excel и создание копии
    rb = open_workbook("template.xls", formatting_info=True)
    wb: Workbook = copy(rb)
    sheet: Worksheet = wb.get_sheet(0)  # Первая книга
    excel_row_index = 2 # Первый индекс строки в Excel

    # Поиск конкретной игры
    only_id = '445/17570753'

    # Строки игр
    rows = driver.find_elements(By.CLASS_NAME, 'line-event')
    prev_play_button = None  # Запоминаем предыдущую кнопку для закрытия, перед открытием нового
    for row in rows:
        a_elems = row.find_elements(By.TAG_NAME, 'a')
        id_href = a_elems[0].get_attribute('href')
        id = re.search('/ru/line/soccer/(.*)\?ts=24', id_href).group(1)
        # if id_href.find(only_id) == -1: continue

        # Закрывем предыдущй
        if prev_play_button is not None:
            u.click(driver, prev_play_button)
            driver.implicitly_wait(1)

        # Левая шапка
        # Время
        time = row.find_element(By.CLASS_NAME, 'line-event__time-static').text.strip()
        # Команды
        teams_block = row.find_element(By.CLASS_NAME, 'line-event__name-teams')
        teams = teams_block.find_elements(By.XPATH, './/*')
        team1 = teams[0].text.strip()
        team2 = teams[1].text.strip()
        # Блок игр по странам
        row_country: WebElement = row.find_element(By.XPATH, '..//..')
        # Дата, Д/Н
        date_parce = row_country.find_element(By.CLASS_NAME, 'line-champ__date').text
        date_parce_list = date_parce.split(' ')
        date_number = int(date_parce_list[0].strip())
        months = ['янв', 'фев', 'мар', 'апр', 'май', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']
        dws = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
        date_month = months.index(date_parce_list[1].strip()[:3].lower()) + 1
        date_year = datetime.now().year
        date_orig = datetime(date_year, date_month, date_number)
        # Если полученая дата > текущей даты, то это прошлый год (стык декабрь / январь)
        if date_orig > datetime.now():
            date_orig = datetime(date_year - 1, date_month, date_number)
        date = date_orig.strftime('%d.%m.%Y') # Дата для отчёта
        dw = dws[date_orig.weekday()] # День недели
        # Игра
        game = row_country.find_element(By.CLASS_NAME, 'line-champ__header-link').text
        print('\n-- ' + game + ' : ' + team1 + ' / ' + team2 + ' (' + id + ')')
        # Сохранение левой шапки в Excel
        sheet.write(excel_row_index, 0, date)
        sheet.write(excel_row_index, 1, dw)
        sheet.write(excel_row_index, 2, time)
        sheet.write(excel_row_index, 3, game)
        sheet.write(excel_row_index, 4, team1)
        sheet.write(excel_row_index, 5, team2)

        # Кнопка раскрытия игры
        play_button = row.find_element(By.CLASS_NAME, 'line-event__dops-toggle')
        if play_button.tag_name != 'button': continue  # Игнор не кнопок
        # Клик по раскрывашке (правая колонка)
        u.click(driver, play_button)
        # Ожидаем прогрузки по названию таблицы нижней части коэффициентов (должна быть всегда)
        waiting_path = "//span[starts-with(., 'Цифра в итоговом счете')]"
        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, waiting_path)))

        # Парсинг игры
        header_line = p.get_header_params(row)

        # Получение и запись коэффициентов
        row_area = row.find_element(By.XPATH, '..')
        p.save_to_excel(row_area, header_line, sheet, excel_row_index)

        prev_play_button = play_button  # Запоминаем кнопку раскрытия
        excel_row_index = excel_row_index + 1

    wb.save('results/' + filename + '.xls')
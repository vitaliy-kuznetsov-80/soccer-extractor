# Параметры игры

from selenium.webdriver import Chrome
from xlrd import open_workbook
from xlutils.copy import copy
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

import utils as u
import typing as t

# Параметры заголовка игры
def get_header_params(row: WebElement):
    # Линия заголовка. Массив значений
    div_line_div = row.find_element(By.CLASS_NAME, "line-event__main-bets")
    # Парсинг заголовка
    header_line = u.clean_text(div_line_div.text).split(' ')

    return {
        'outcome_1': header_line[0],
        'outcome_X': header_line[1],
        'outcome_2': header_line[2],
        'fora1_0_key': header_line[3],
        'fora1_0_value': header_line[4],
        'fora2_0_key': header_line[5],
        'fora2_0_value': header_line[6],
        'total_key': header_line[7],
        'total_m_value': header_line[8],
        'total_b_value': header_line[9],
    }

# Исходы
def get_outcome(header_line):
    return {
        '1': header_line['outcome_1'],
        'X': header_line['outcome_X'],
        '2': header_line['outcome_2']
    }

# Фора 0
def get_fora_0(driver: Chrome, header_line):
    fora_1 = header_line['fora1_0_value']
    fora_2 = header_line['fora2_0_value']

    # Если берём из таблицы
    f1_in_table = header_line['fora1_0_key'] != 0
    f2_in_table = header_line['fora2_0_key'] != 0
    if f1_in_table or f2_in_table:
        rows = u.get_rows(driver, 'Фора')
        if f1_in_table: fora_1 = u.get_value(rows, 'Ф1(0)')
        if f2_in_table: fora_2 = u.get_value(rows, 'Ф2(0)')

    return { '1': fora_1, '2': fora_2 }

# Дв. исход
def get_double_outcome(driver: Chrome):
    rows = u.get_rows(driver, 'Двойной исход')
    return {
        '1X': u.get_value(rows, '1X'),
        'X2': u.get_value(rows, 'X2')
    }

# Голы
def get_goals(driver: Chrome):
    rows = u.get_rows(driver, 'Голы')
    return {
        '1': u.get_value(rows, 'К1Забьет'),
        '2': u.get_value(rows, 'К2Забьет')
    }

# Обе забьют
def get_both_will_score(driver: Chrome):
    rows = u.get_rows(driver, 'Обе забьют')
    return {
        'yes': u.get_value(rows, 'Да'),
        'no': u.get_value(rows, 'Нет')
    }

# Тотал
def get_total(driver: Chrome):
    col_total = u.get_rows(driver, 'Тотал')

    def get_total_mb(value):
        try:
            index = col_total.index(value)
        except:
            return { 'm': '', 'b': '' }
        m = col_total[index + 1]
        b = col_total[index + 3]
        return { 'm': m, 'b': b }

    return {
        '1.5': get_total_mb('1.5Мен'),
        '2': get_total_mb('2Мен'),
        '2.5': get_total_mb('2.5Мен'),
        '3': get_total_mb('3Мен'),
        '3.5': get_total_mb('3.5Мен'),
        '4': get_total_mb('4Мен'),
        '4.5': get_total_mb('4.5Мен')
    }

# Исходы по таймам
def get_outcome_by_time(driver: Chrome):
 rows = u.get_rows(driver, 'Исходы по таймам')

# Доп. тоталы 1-й тайм
def get_total_1time_extra(driver: Chrome):
    rows = u.get_rows(driver, 'Доп. тоталы 1-й тайм')

# 1-й тайм забьет
def get_will_score_1_time(driver: Chrome):
    rows = u.get_rows(driver, '1-й тайм забьет')

# Сохранение параметров в Excel
def save_to_excel(driver: Chrome, header_line: t.List[str], filename: str):
    outcome = get_outcome(header_line)
    fora_0 = get_fora_0(driver, header_line)
    double_result = get_double_outcome(driver)
    goals = get_goals(driver)
    both_will_score = get_both_will_score(driver)
    total = get_total(driver)

    col_index = 0

    def write(value):
        global col_index
        # Если не вещественное число, то прочерк
        try:
            float(value)
            sheet.write(2, col_index, float(value))
        except ValueError:
            sheet.write(2, col_index, '-')
        col_index = col_index + 1

    # Открытие шаблона и создание копии
    rb = open_workbook("template.xls", formatting_info=True)
    wb = copy(rb)
    sheet = wb.get_sheet(0)  # Первая книга

    write(outcome['1'])
    write(outcome['X'])
    write(outcome['2'])
    write(fora_0['1'])
    write(fora_0['2'])
    write(double_result['1X'])
    write(double_result['X2'])
    write(goals['1'])
    write(goals['2'])
    write(both_will_score['yes'])
    write(both_will_score['no'])
    write(total['1.5']['m'])
    write(total['1.5']['b'])
    write(total['2']['m'])
    write(total['2']['b'])
    write(total['2.5']['m'])
    write(total['2.5']['b'])
    write(total['3']['m'])
    write(total['3']['b'])
    write(total['3.5']['m'])
    write(total['3.5']['b'])
    write(total['4']['m'])
    write(total['4']['b'])
    write(total['4.5']['m'])
    write(total['4.5']['b'])

    wb.save(filename + '.xls')
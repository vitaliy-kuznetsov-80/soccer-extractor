"""Методы парсинга"""

import typing as t

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import xlwt

import utils as u

def get_header_params(row: WebElement):
    """Параметры заголовка игры"""
    # Линия заголовка. Массив значений
    div_line_div = row.find_element(By.CLASS_NAME, "line-event__main-bets")
    # Парсинг заголовка
    header_list = div_line_div.find_elements(By.XPATH, './/*')
    header_line = []
    for item in header_list:
        header_line.append(u.clean_text(item.text))

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

def get_outcome(header_line):
    """Исходы"""
    return {
        '1': header_line['outcome_1'],
        'X': header_line['outcome_X'],
        '2': header_line['outcome_2']
    }

def get_fora_0(element: WebElement, header_line):
    """Фора 0"""
    fora_1 = header_line['fora1_0_value']
    fora_2 = header_line['fora2_0_value']

    # Если берём из таблицы
    f1_in_table = header_line['fora1_0_key'] != '0'
    f2_in_table = header_line['fora2_0_key'] != '0'
    if f1_in_table or f2_in_table:
        rows = u.get_rows(element, 'Фора', 2)
        if f1_in_table:
            fora_1 = u.get_value(rows, 'Ф1(0)')
        if f2_in_table:
            fora_2 = u.get_value(rows, 'Ф2(0)')

    return { '1': fora_1, '2': fora_2 }

def get_double_outcome(element: WebElement):
    """Двойной исход"""
    rows = u.get_rows(element, 'Двойной исход', 2)
    value_1x = u.get_value(rows, '1X')
    value_x2 = u.get_value(rows, 'X2')
    return { '1X': value_1x, 'X2': value_x2 }

def get_goals(element: WebElement):
    """Голы"""
    rows = u.get_rows(element, 'Голы', 2)
    g1 = u.get_value(rows, 'К1Забьет')
    g2 = u.get_value(rows, 'К2Забьет')
    return { '1': g1, '2': g2 }

def get_both_will_score(element: WebElement):
    """Обе забьют"""
    rows = u.get_rows(element, 'Обе забьют', 2)
    return {
        'yes': u.get_value(rows, 'Да'),
        'no': u.get_value(rows, 'Нет')
    }

def get_mb(rows: t.List[str], value: str):
    """Получить M, B"""
    try:
        index = rows.index(value)
    except ValueError:
        return { 'm': '', 'b': '' }
    m = rows[index + 1]
    b = rows[index + 3]
    return { 'm': m, 'b': b }

def get_total(element: WebElement, header_line):
    """Тотал"""
    rows = u.get_rows(element, 'Тотал', 2)

    result = {
        '1.5': get_mb(rows, '1.5Мен'),
        '2': get_mb(rows, '2Мен'),
        '2.5': get_mb(rows, '2.5Мен'),
        '3': get_mb(rows, '3Мен'),
        '3.5': get_mb(rows, '3.5Мен'),
        '4': get_mb(rows, '4Мен'),
        '4.5': get_mb(rows, '4.5Мен')
    }

    # Добавляем из заголовка
    total_header = header_line['total_key']
    total_header_m = header_line['total_m_value']
    total_header_b = header_line['total_b_value']
    result[total_header] = { 'm': total_header_m, 'b': total_header_b }
    print('     ' + total_header + 'Мен: ' + total_header_m + ' | Бол: ' + total_header_b + ' [Заг]')

    return result

def get_outcome_by_time_1t(element: WebElement):
    """Исходы по таймам (1т, ТБ 1, 1.5)"""
    rows = u.get_rows(element, 'Исходы по таймам', 2, '1-й тайм')
    tb1 = get_mb(rows, 'ТБ(1)')['m']
    tb1_5 = get_mb(rows, 'ТБ(1.5)')['m']
    return { '1': tb1, '1.5': tb1_5 }

def get_total_1time_extra(element: WebElement):
    """Доп. тоталы 1-й тайм"""
    rows = u.get_rows(element, 'Доп. тоталы 1-й тайм', 2)
    value_1b = get_mb(rows, '1Мен')['b']
    value_2b = get_mb(rows, '2Мен')['b']
    return {'1': value_1b, '2': value_2b}

def get_total_1time(element: WebElement):
    """get total 1 time"""
    total_1time_extra = get_total_1time_extra(element)
    outcome_by_time_1t = get_outcome_by_time_1t(element)

    t1 = total_1time_extra['1']
    if t1 == '':
        t1 = outcome_by_time_1t['1']

    t1_5 = outcome_by_time_1t['1.5']
    t2 = total_1time_extra['2']
    return {'1': t1, '1.5': t1_5, '2': t2}

def get_will_score_1_time(element: WebElement):
    """1-й тайм забьет"""
    rows = u.get_rows(element, '1-й тайм забьет', 2)
    k1 = u.get_value(rows, 'K1Да')
    k2 = u.get_value(rows, 'K2Да')
    return {'1': k1, '2': k2}

def save_to_excel(element: WebElement, header_line: t.List[str], sheet: xlwt.Worksheet, row_index: int):
    """Сохранение параметров в Excel"""
    outcome = get_outcome(header_line)
    total = get_total(element, header_line)
    double_result = get_double_outcome(element)
    fora_0 = get_fora_0(element, header_line)
    goals = get_goals(element)
    both_will_score = get_both_will_score(element)
    will_score_1_time = get_will_score_1_time(element)
    total_1time = get_total_1time(element)

    col_index = 6

    def write(value):
        nonlocal col_index
        # Если не вещественное число, то прочерк
        try:
            float(value)
            sheet.write(row_index, col_index, float(value))
        except ValueError:
            style = xlwt.easyxf('pattern: pattern solid, fore_colour empty_color')
            sheet.write(row_index, col_index, '', style)
        col_index = col_index + 1

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

    write(total_1time['1'])
    write(total_1time['1.5'])
    write(total_1time['2'])

    write(will_score_1_time['1'])
    write(will_score_1_time['2'])

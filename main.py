from xlrd import open_workbook
from xlutils.copy import copy
import utils

# Id линии и игры
line_game_id = '101509/17873474'
# Делать скриншот?
is_screenshot = False

# ---
print('Старт')

filename = utils.get_filename(line_game_id)
dom_tree = utils.get_page(line_game_id, is_screenshot, filename)

# Линия заголовка. Массив значений
header_line = utils.clean_text(dom_tree.find('div', class_="line-event__main-bets").text).split(' ')

# Исходы
def get_results():
    return {
        '1': header_line[0],
        'X': header_line[1],
        '2': header_line[2]
    }

# Фора 0
def get_fora_0():
    if header_line[3] == '0':
        fora_1 = header_line[4]
        fora_2 = header_line[6]
    else:
        rows = utils.get_rows(dom_tree, 'Фора')
        fora_1 = utils.get_value(rows, 'Ф1(0)')
        fora_2 = utils.get_value(rows, 'Ф2(0)')
    return { '1': fora_1, '2': fora_2 }

# Дв. исход
def get_double_result():
    rows = utils.get_rows(dom_tree, 'Двойной исход')
    return {
        '1X': utils.get_value(rows, '1X'),
        'X2': utils.get_value(rows, 'X2')
    }

# Голы
def get_goals():
    rows = utils.get_rows(dom_tree, 'Голы')
    return {
        '1': utils.get_value(rows, 'К1Забьет'),
        '2': utils.get_value(rows, 'К2Забьет')
    }

# Обе забьют
def get_both_will_score():
    rows = utils.get_rows(dom_tree, 'Обе забьют')
    return {
        'yes': utils.get_value(rows, 'Да'),
        'no': utils.get_value(rows, 'Нет')
    }

# Тотал
def get_total():
    col_total = utils.get_rows(dom_tree, 'Тотал')

    def get_total_mb(value):
        try:
            index = col_total.index(value)
        except:
            return { 'm': '', 'b': '' }
        m = col_total[index + 1]
        b = col_total[index + 3]
        return { 'm': m, 'b': b }

    return {
        '0.5': get_total_mb('0.5Мен'),
        '1': get_total_mb('1Мен'),
        '1.5': get_total_mb('1.5Мен'),
        '2': get_total_mb('2Мен'),
        '2.5': get_total_mb('2.5Мен'),
        '3': get_total_mb('3Мен'),
        '3.5': get_total_mb('3.5Мен'),
        '4': get_total_mb('4Мен'),
        '4.5': get_total_mb('4.5Мен')
    }

result_by_time = utils.get_rows(dom_tree, 'Исходы по таймам')
total_1time_extra = utils.get_rows(dom_tree, 'Доп. тоталы 1-й тайм')
will_score_1_time = utils.get_rows(dom_tree, '1-й тайм забьет')

# Получение коэффициентов
result = get_results()
fora_0 = get_fora_0()
double_result = get_double_result()
goals = get_goals()
both_will_score = get_both_will_score()
total = get_total()

# Сохранение в Excel
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
sheet = wb.get_sheet(0) # Первая книга

write(result['1'])
write(result['X'])
write(result['2'])
write(fora_0['1'])
write(fora_0['2'])
write(double_result['1X'])
write(double_result['X2'])
write(goals['1'])
write(goals['2'])
write(both_will_score['yes'])
write(both_will_score['no'])
write(total['0.5']['m'])
write(total['0.5']['b'])
write(total['1']['m'])
write(total['1']['b'])
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

print('Конец')
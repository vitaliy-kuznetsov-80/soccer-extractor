"""Основная программа"""

from datetime import datetime
import sys
import time
import traceback

import utils as u
import workflow as w

# Отладочные константы
LOG_IN_CONSOLE = False
LINES_LIMIT = 0 # Лимит линий. 0 - безлимит
GAMES_LIMIT = 0 # Лимит обработки игр. 0 - безлимит
ONLY_LINE_ID = '' # Поиск конкретной линии по Id. Пустая строка - отключено
ONLY_GAME_ID = '' # Поиск конкретной игры по Id. Пустая строка - отключено

BASE_URL = 'https://betcity.ru/ru/line/soccer?ts=24' # Url списка линий
filename = u.get_filename() # Имя фалйла скрина и Excel

if not LOG_IN_CONSOLE:
    sys.stdout = open('results/log' + filename + '.log', 'w', encoding='utf-8') # Вывод консоли в файл

print('Старт')
start_time = datetime.now()

try:
    u.get_page(BASE_URL)  # Получение страницы
    loaded_time = datetime.now()
    u.close_dialogs()  # Закрытие диалогов

    w.set_msk()  # Выбор часового пояса МСК

    u.get_container()  # Получение контенера для игр

    w.mark_lines(LINES_LIMIT, ONLY_LINE_ID)  # Пометка строк для получения игр
    w.load_games()  # Загрузка игр для выбранных линий
    w.parce_games(filename, GAMES_LIMIT, ONLY_GAME_ID)  # Парсинг игр

    time.sleep(1)
    u.driver.close()

    end_time = datetime.now()
    print(f"Время получения страницы: {loaded_time - start_time}")
    print(f'Время парсинга: {end_time - loaded_time}')
    print(f'Время работы всего: {end_time - start_time}')
    print('Финиш')
except BaseException as e:
    print("\nERROR")

    ex_type, ex_value, ex_traceback = sys.exc_info()
    trace_back = traceback.extract_tb(ex_traceback)

    print(f"Type: {ex_type.__name__}")
    print(f"Message: {ex_value}")

    for trace in trace_back:
        print(f"File: {trace[0]}, Line: {trace[1]:d}, Func.Name: {trace[2]}, Message: {trace[3]}")
finally:
    sys.stdout.close()

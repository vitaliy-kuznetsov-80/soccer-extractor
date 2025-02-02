import utils as u
import workflow as w
from datetime import datetime
import sys
import time

# Отладочные константы
log_in_console = False
lines_limit = 0 # Лимит линий. 0 - безлимит
games_limit = 0 # Лимит обработки игр. 0 - безлимит
only_id = '' # Поиск конкретной игры. Пустая строка - отключено

base_url = 'https://betcity.ru/ru/line/soccer?ts=24' # Url списка линий
filename = u.get_filename() # Имя фалйла скрина и Excel

if not log_in_console:
    sys.stdout = open('results/log_' + filename, 'w', encoding='utf-8') # Вывод консоли в файл

print('Старт')
start_time = datetime.now()

u.get_page(base_url) # Получение страницы
loaded_time = datetime.now()
u.close_dialogs() # Закрытие диалогов

w.set_msk() # Выбор часового пояса МСК

u.get_container() # Получение контенера для игр

w.mark_lines(lines_limit) # Пометка строк для получения игр
w.load_games() # Загрузка игр для выбранных линий
w.parce_games(filename, games_limit, only_id) # Парсинг игр

time.sleep(1)
u.driver.close()

end_time = datetime.now()
print('Время получения страницы: {}'.format(loaded_time - start_time))
print('Время парсинга: {}'.format(end_time - loaded_time))
print('Время работы всего: {}'.format(end_time - start_time))
print('Финиш')

sys.stdout.close()
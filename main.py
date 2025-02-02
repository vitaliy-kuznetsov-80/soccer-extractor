import utils as u
import workflow as w
from datetime import datetime
import sys

is_screenshot = False # Делать ли скрин

base_url = 'https://betcity.ru/ru/line/soccer?ts=24' # Url списка линий
filename = u.get_filename() # Имя фалйла скрина и Excel

# sys.stdout = open('results/log_' + filename, 'w', encoding='utf-8') # Вывод консоли в файл

print('Старт')
start_time = datetime.now()

u.get_page(base_url) # Получение страницы
u.close_dialogs() # Закрытие диалогов

w.set_msk() # Выбор часового пояса МСК

u.get_container() # Получение контенера для игр

w.mark_lines() # Пометка строк для получения игр
w.load_games() # Загрузка игр для выбранных линий
w.parce_games(filename) # Парсинг игр

u.driver.close()
print('Финиш')

end_time = datetime.now()
print('Время работы: {}'.format(end_time - start_time))

# sys.stdout.close()
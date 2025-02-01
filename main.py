import utils as u
import workflow as w
from datetime import datetime
import sys

is_screenshot = False # Делать ли скрин

base_url = 'https://betcity.ru/ru/line/soccer?ts=24' # Url списка линий
filename = u.get_filename() # Имя фалйла скрина и Excel

sys.stdout = open('results/log_' + filename, 'w', encoding='utf-8')
print('Старт')
start_time = datetime.now()

driver = u.get_page(base_url) # Получение страницы
u.close_dialogs(driver) # Закрытие диалогов

w.mark_lines(driver) # Пометка строк для получения игр
w.load_games(driver) # Загрузка игр для выбранных линий
w.parce_games(driver, filename) # Парсинг игр

driver.close()
print('Финиш')

end_time = datetime.now()
print('Время работы: {}'.format(end_time - start_time))
sys.stdout.close()
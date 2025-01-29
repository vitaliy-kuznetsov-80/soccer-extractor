import utils as u
import workflow as w

is_screenshot = False # Делать ли скрин

print('Старт')

base_url = 'https://betcity.ru/ru/line/soccer?ts=24' # Url списка линий
filename = u.get_filename() # Имя фалйла скрина и Excel
driver = u.get_page(base_url, is_screenshot, filename) # Получение страницы
u.close_dialogs(driver) # Закрытие диалогов

w.mark_lines(driver) # Пометка строк для получения игр
w.load_games(driver) # Загрузка игр для выбранных линий
w.parce_games(driver, filename) # Парсинг игр

print('Финиш')
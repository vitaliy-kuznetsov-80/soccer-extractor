"""Основная программа"""

from datetime import datetime
import sys
import time
import traceback

from page import Page
from src.parcer.games_loader import GamesLoader
from src.parcer.games_parcer import GamesParcer
from src.utils.config import Config
from src.utils.logger import Logger

# Url списка линий
BASE_URL: str = 'https://betcity.ru/ru/line/soccer?ts=24'

# Конфиг
conf = Config()

# Настройка логера
log = Logger(conf.log_in_console)

log.print('Старт')
start_time = datetime.now()

try:
    # Получение страницы
    page = Page(BASE_URL, conf, log)
    page.init()

    loaded_time = datetime.now()

    page.close_dialogs()  # Закрытие диалогов
    page.set_msk()  # Выбор часового пояса МСК
    page.get_container()  # Получение контенера для игр

    game_loader = GamesLoader(page, log)
    # Пометка строк для получения игр
    game_loader.mark_lines(conf.lines_limit, conf.only_line_id)
    # Загрузка игр для выбранных линий
    game_loader.load_games()

    # Парсинг игр
    parceGames = GamesParcer(page, log)
    parceGames.parce(conf.only_game_id)

    time.sleep(1)
    page.close()

    end_time = datetime.now()
    log.print("Время получения страницы: " + str(loaded_time - start_time))
    log.print('Время парсинга: ' + str(end_time - loaded_time))
    log.print('Время работы всего: ' + str(end_time - start_time))
    log.print('Финиш')
except Exception as e: # pylint: disable=broad-except
    log.print('\nERROR')

    ex_type, ex_value, ex_traceback = sys.exc_info()
    trace_back = traceback.extract_tb(ex_traceback)

    log.print('Type: ' + str(ex_type.__name__))
    log.print('Message: ' + str(ex_value))

    for trace in trace_back:
        log.print('File: {}, Line: {:d}, Func.Name: {}, Message: {}'.format(trace[0], trace[1], trace[0], trace[3]))

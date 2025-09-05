"""Основная программа"""
from datetime import datetime
import sys
import time
import traceback

from src.page import Page
from src.utils import Config
from src.utils import Logger
from src.parcer import GamesLoader
from src.parcer import GamesParcer

# Url списка линий
URL: str = 'https://betcity.ru/ru/line/soccer?ts=24'

# Конфиг
conf = Config()

# Настройка логера
log = Logger(conf.log_in_console)

log.print('Старт')
start_time = datetime.now()

try:
    # Получение страницы
    page = Page(URL, conf, log)

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
    log.print('Время работы: ' + str(end_time - start_time))
    log.print('Финиш')
except Exception as e: # pylint: disable=broad-except
    log.print('\nERROR')

    _, ex_value, ex_traceback = sys.exc_info()
    trace_back = traceback.extract_tb(ex_traceback)

    log.print('Message: ' + str(ex_value))

    for trace in trace_back:
        log.print('File: {}, Line: {:d}, Func.Name: {}, Message: {}'.format(trace[0], trace[1], trace[0], trace[3]))

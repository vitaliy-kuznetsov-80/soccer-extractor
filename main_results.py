"""Основная программа"""
from datetime import datetime
import sys
import traceback

from src.page import Page
from src.parcer.results_parser import ResultParser
from src.utils import Config, Utils
from src.utils import Logger

# Url результата
URL: str = 'results/soccer'

# Конфиг
conf = Config()

# Настройка логера
log = Logger(conf.log_in_console, '_results')

log.print('Старт')
start_time = datetime.now()

def parce_results(url: str) -> None:
    page = Page(url, conf, log, 'results-champ')

    rp = ResultParser(log)
    rp.parce_results(page)
    rp.save()

    page.close()

try:
    url_yesterday = URL + '?date=' + Utils.get_url_date(Utils.get_yesterday()) # Url вчерашнего дня
    url_today = URL + '?date=' + Utils.get_url_date(datetime.now()) # Url сегодняшнего дня

    parce_results(url_yesterday) # Парсинг вчера
    parce_results(url_today) # Парсинг сегодня

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

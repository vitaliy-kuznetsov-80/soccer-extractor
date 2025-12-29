"""Основная программа"""
from datetime import datetime
import sys
import traceback

from src import ExcelManager
from src.page import Page
from src.parcer.results_parser import ResultParser
from src.utils import Config, Utils
from src.utils import Logger

# Url результата
url: str = 'results/soccer'

class Results:
    """Основной класс программы для сбора результвтов матчей"""
    __conf: Config
    __log: Logger

    def __init__(self):
        # Конфиг
        self.__conf = Config()
        # Настройка логера
        self.__log = Logger(self.__conf, 'results')

    def run(self):
        print(f"Старт сбора результатов: {datetime.now()}")

        # Получение имени файла и проверка наличия вечрашнего дня
        excel_filename = ExcelManager.get_yesterday_filename()
        if not excel_filename:
            self.__log.print("Файл вчерашнего дня не найден")
            print("Файл вчерашнего дня не найден")
            return

        self.__log.print('Старт')
        start_time = datetime.now()

        def parce_results(_url: str) -> None:
            page = Page(_url, self.__conf, self.__log, 'results-champ')

            rp = ResultParser(self.__log)
            rp.parce_results(page)
            rp.save()

            page.close()

        try:
            url_yesterday = url + '?date=' + Utils.get_url_date(Utils.get_yesterday()) # Url вчерашнего дня
            url_today = url + '?date=' + Utils.get_url_date(datetime.now()) # Url сегодняшнего дня

            parce_results(url_yesterday) # Парсинг вчера
            parce_results(url_today) # Парсинг сегодня

            end_time = datetime.now()
            self.__log.print('Время работы: ' + str(end_time - start_time))
            self.__log.print('Финиш')
        except Exception as e: # pylint: disable=broad-except
            self.__print_error()
        finally:
            self.__log.close_file()

    def __print_error(self):
        self.__log.print('\nERROR')

        _, ex_value, ex_traceback = sys.exc_info()
        trace_back = traceback.extract_tb(ex_traceback)

        self.__log.print('Message: ' + str(ex_value))

        for trace in trace_back:
            self.__log.print(
                'File: {}, Line: {:d}, Func.Name: {}, Message: {}'.format(trace[0], trace[1], trace[0], trace[3]))


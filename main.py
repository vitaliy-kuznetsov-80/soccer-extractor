"""Основная программа"""
from datetime import datetime
import sys
import time
import traceback

from src.page import Page
from src.utils import Config
from src.utils import Logger
from src.utils import Region
from src.parcer import LinesParser
from src.parcer import GamesParser

# Url списка линий
url: str = 'line/soccer?ts=24'

class Main:
    """Основной класс программы"""
    __page: Page
    __conf: Config
    __region: Region
    __log: Logger
    __region_name: str

    def __init__(self, region: Region):
        self.__region = region
        self.__region_name = str(self.__region.value)
        self.__conf = Config()
        self.__log = Logger(self.__conf.log_in_console, self.__region_name)

    def run(self, ):
        print('Старт парсинга для региона: ' + self.__region_name.capitalize() + f" в {datetime.now()}")
        self.__log.print('Старт для региона: ' + self.__region_name.capitalize())
        start_time = datetime.now()

        try:
            # Получение страницы
            self.__page = Page(url, self.__conf, self.__log, 'champs__sport')

            game_loader = LinesParser(self.__page, self.__log)
            game_loader.lost_lines() # Потеряные игры для всех регионов

            # Пометка строк для получения игр
            game_loader.mark_lines(self.__conf.lines_limit, self.__conf.only_line_id, self.__region)
            # Загрузка игр для выбранных линий
            game_loader.load_games()

            # Парсинг игр
            parce_games = GamesParser(self.__page, self.__region_name, self.__log)
            parce_games.parce(self.__conf.only_game_id)

            time.sleep(1)

            end_time = datetime.now()
            self.__log.print('Время работы: ' + str(end_time - start_time))
            self.__log.print('Финиш')
        except Exception as e: # pylint: disable=broad-except
            self.__print_error()
        finally:
            self.__page.close()
            self.__log.close_file()

    def __print_error(self):
        self.__log.print('\n - ОШИБКА - ')

        _, ex_value, ex_traceback = sys.exc_info()
        trace_back = traceback.extract_tb(ex_traceback)

        self.__log.print('Сообщение: ' + str(ex_value))

        for trace in trace_back:
            self.__log.print(
                'File: {}, Line: {:d}, Func.Name: {}, Message: {}'.format(trace[0], trace[1], trace[0], trace[3]))
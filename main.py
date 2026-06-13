"""Основная программа"""
import os
from datetime import datetime
import sys
import time
import traceback

# from src.dto.k_matrix_gold_dto import MatrixGoldRegionDto, load_from_json
from src.dto.parce_results_dto import ParceResultsDto
from src.dto.region_enum import RegionEnum
from src.page.page import Page
from src.utils import Config, get_filename
from src.utils import Logger
from src.parcer import LinesParser
from src.parcer import GamesParser
from src.utils.logger import LOGS_FOLDER_NAME

# Url списка линий
url: str = 'line/soccer?ts=24'

class Main:
    """Основной класс программы"""
    __page: Page
    __conf: Config
    __region: RegionEnum
    __log: Logger
    __region_name: str
    __start_time: datetime

    def __init__(self, region: RegionEnum):
        self.__region = region
        self.__region_name = str(self.__region.value)
        self.__conf = Config()
        self.__log = Logger(self.__conf, self.__region_name)

    def run(self, ):
        self.__log.print('Старт: ' + self.__region_name.capitalize()  + f" в {datetime.now()}", True)
        self.__start_time = datetime.now()

        try:
            # k_matrix_gold = load_from_json(self.__region, "assets/europe.json")

            # Получение страницы
            self.__page = Page(url, self.__conf, self.__log)
            self.__page.init('champs__sport')

            parce_result = ParceResultsDto(self.__region, self.__region_name, self.__page, self.__log, self.__conf, self.__page.container)

            game_loader = LinesParser(parce_result)
            game_loader.lost_lines() # Потерянные игры для всех регионов

            # Пометка строк для получения игр
            game_loader.mark_lines(self.__conf.lines_limit, self.__conf.only_line_id, self.__region)
            # Загрузка игр для выбранных линий
            game_loader.load_games_with_wait()

            # Дополнение объекта результата, линиями игр
            parce_result = game_loader.parce_result

            # Парсинг игр
            parce_games = GamesParser(parce_result)
            parce_games.parce(self.__conf.only_game_id)

            # Дополнение объекта результата коэффициентами игр
            # parce_result = parce_games.parce_result
            # print(parce_result)
            # parce_result.save('')

            time.sleep(1)
        except Exception: # pylint: disable=broad-except
            self.__print_error()
            filename = os.path.join(LOGS_FOLDER_NAME, get_filename() + '_error_screen.png')
            self.__page.get_screenshot(filename)
            raise
        finally:
            self.__page.close()
            self.__log.close_file()
            end_time = datetime.now()
            self.__log.print('Конец: ' + self.__region_name.capitalize() + f" в {datetime.now()}", True)
            self.__log.print('Время работы: ' + str(end_time - self.__start_time), True)

    def __print_error(self):
        self.__log.print('\n- ОШИБКА - ', True)

        exc_type, ex_value, ex_traceback = sys.exc_info()
        trace_back = traceback.extract_tb(ex_traceback)

        self.__log.print('Сообщение ошибки: (' + str(exc_type) + ') - '+ str(ex_value), True)

        for trace in trace_back:
            self.__log.print(
                'File: {}, Line: {:d}, Func.Name: {}, Message: {}'.format(trace[0], trace[1], trace[2], trace[3]))
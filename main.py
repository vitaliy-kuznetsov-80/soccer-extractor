"""Основная программа"""
from datetime import datetime
import sys
import time
import traceback

from src.parce_results_dto import Region, ParceResultsDto
from src.page import Page
from src.utils import Config
from src.utils import Logger
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
    __start_time: datetime

    def __init__(self, region: Region):
        self.__region = region
        self.__region_name = str(self.__region.value)
        self.__conf = Config()
        self.__log = Logger(self.__conf, self.__region_name)

    def run(self, ):
        self.__log.print('Старт: ' + self.__region_name.capitalize()  + f" в {datetime.now()}", True)
        self.__start_time = datetime.now()

        try:
            # Чтение золотых коэффициентов
            # with open("assets/ks.json", 'r', encoding='utf-8') as file_content:
            #     data = json.load(file_content)
            #     gold_matrix_list: list[GoldKMatrix] = data.get(self.__region_name, {})

            # Получение страницы
            self.__page = Page(url, self.__conf, self.__log, 'champs__sport')

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
            parce_result = parce_games.parce_result
            # json_parce_result = parce_result.to_json()

            time.sleep(1)
        except Exception as e: # pylint: disable=broad-except
            self.__print_error()
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
                'File: {}, Line: {:d}, Func.Name: {}, Message: {}'.format(trace[0], trace[1], trace[0], trace[3]))
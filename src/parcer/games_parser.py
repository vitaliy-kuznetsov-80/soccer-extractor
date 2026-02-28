"""Методы парсинга"""

from datetime import date
import time

from selenium.common import NoSuchElementException, TimeoutException, WebDriverException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from .Header import HeaderLine
from .params_parser import SaveResultDto, ParamsParser
from src.dto.game_dto import GameDto
from ..dto import ParceResultsDto
from ..utils import Logger
from ..utils import Utils
from ..utils import ExcelManager
from ..page import Page

months = ['янв', 'фев', 'мар', 'апр', 'мая', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']
dws = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']

class GamesParser:
    """Парсинг игр"""
    __parce_result: ParceResultsDto
    __page: Page
    __container: WebElement
    __log: Logger
    __region_name: str
    __first_row: int
    __em: ExcelManager

    def __init__(self, parce_result: ParceResultsDto):
        self.__parce_result = parce_result
        self.__page = parce_result.page
        self.__container = parce_result.page.container
        self.__region_name = parce_result.region_name
        self.__log = parce_result.log
        self.__em = ExcelManager()
        self.__first_row = 0

    @property
    def parce_result(self) -> ParceResultsDto:
        return self.__parce_result

    def parce(self,  only_id: str) -> None:
        """Парсинг игр"""

        self.init_excel_file(self.__page.conf.day_offset)

        self._get_game_count()

        # Запоминаем предыдущую кнопку для закрытия, перед открытием нового
        button_prev_play = None

        # Группы по линиям
        lines = self.__container.find_elements(By.CLASS_NAME, 'line__champ')
        for line in lines:
            date1, date2, game_id_date2 = self._get_game_date(line)

            # Строки игр в линии
            rows = line.find_elements(By.CLASS_NAME, 'line-event')

            # Цикл по играм
            game_date = date1
            for row in rows:
                # Получение полного Id игры (для лога и отладки)
                game_full_id = Utils.get_id(row.find_element(By.TAG_NAME, 'a'), 'ts=24')
                # Поиск конкретной игры, если есть
                if only_id and game_full_id != only_id: continue

                # Закрываем предыдущий
                if button_prev_play is not None:
                    self.__page.click(button_prev_play)
                    time.sleep(1)

                # Смена даты
                if game_id_date2 == game_full_id: game_date = date2

                # Игра (из заголовка линии)
                game_name = (line.find_element(By.CLASS_NAME, 'line-champ__header-link').text
                             .replace('Футбол.', '').strip())

                # Парсим и записываем левый заголовок
                self._write_left_header(game_full_id, game_name, game_date, self.__first_row, row)

                # Кнопка раскрытия игры
                button_play = row.find_element(By.CLASS_NAME, 'line-event__dops-toggle')
                if button_play.tag_name != 'button': continue  # Игнор не кнопок

                # Клик по раскрывашке (правая колонка)
                self.__page.click(button_play)
                is_exist = True
                try:
                    # Ожидаем прогрузки по названию таблицы нижней части коэффициентов (должна быть всегда)
                    self.__page.wait(By.XPATH, "//span[starts-with(., 'Тотал')]")
                except (NoSuchElementException, StaleElementReferenceException, TimeoutException, WebDriverException):
                    is_exist = False
                    self.__log.print("Игра отсутствует. Таймаут")

                # Парсим и сохраняем игру
                if is_exist:
                    line_full_id_list = game_full_id.split('/')
                    line_id = line_full_id_list[0]
                    game_id = line_full_id_list[1]
                    pp = ParamsParser(self.__parce_result, line_id, game_id)
                    save_result_dto = self._parse_game(row)
                    pp.save_to_excel(save_result_dto, self.__em)

                button_prev_play = button_play  # Запоминаем кнопку раскрытия
                self.__first_row = self.__first_row + 1

        self.__em.save()

    def init_excel_file(self, day_offset: int = 0):
        """Если есть файл Excel С датой сегодняшнего дня, то дописываем в него, иначе создаём новый"""
        excel_filename = self.__em.get_today_filename(day_offset)
        if excel_filename:
            self.__em.load_excel(excel_filename)
            self.__first_row = self.__em.get_row_count()
        else:
            self.__em.init_excel('template.xls', day_offset)
            self.__first_row = 2

    # Private

    def _get_game_count(self) -> int:
        """Кол-во игр всего"""
        all_games = self.__container.find_elements(By.CLASS_NAME, 'line-event')
        row_count = len(all_games)
        self.__log.print('\nИгр в обработке: ' + str(row_count))
        return row_count

    @staticmethod
    def _get_game_date(line:  WebElement) -> tuple[str, str, str]:
        """Дата в формате: {Дата} {Название месяца}. Например: 9 февраля"""
        date_list = line.find_elements(By.CLASS_NAME, 'line-champ__date')
        date1 = date_list[0].text.strip()  # Дата 1 есть всегда
        date2 = ''  # Дата 2 встречается после 00:00
        game_id_date2 = ''  # id игры, начиная с которой, меняется дата
        if len(date_list) == 2:
            date2 = date_list[1].text.strip()
            # смотрим следующий тэг
            first_row_date2 = date_list[1].find_element(By.XPATH, 'following-sibling::*[1]')
            # Id игры после смены даты
            a_tag = first_row_date2.find_element(By.CLASS_NAME, 'line-event__name')
            game_id_date2 = Utils.get_id(a_tag, 'ts=24')
        return date1, date2, game_id_date2

    def _parse_game(self, row: WebElement) -> SaveResultDto:
        """Парсинг игры"""
        header_line = HeaderLine.parse(row)
        # Получение и запись коэффициентов
        row_area = row.find_element(By.XPATH, '..')
        save_result_dto = SaveResultDto(row_area, header_line, self.__first_row)
        return save_result_dto

    def _write_left_header(self, line_full_id: str, game_name: str, date_parce: str, excel_row_index: int, row: WebElement) -> None:
        """Левая шапка. Получение и запись в Excel"""

        # Время игры
        time_game = row.find_element(By.CLASS_NAME, 'line-event__time-static').text.strip()

        # Команды
        teams_block = row.find_element(By.CLASS_NAME, 'line-event__name-teams')
        teams = teams_block.find_elements(By.XPATH, './/*')
        team1 = teams[0].text.strip()
        team2 = teams[1].text.strip()

        # Дата в формате: dd.mm
        date_current: date = date.today()  # Текущая дата без времени
        year_current: int = date_current.year  # Текущий год
        date_parce_list = date_parce.split(' ')
        date_number: int = int(date_parce_list[0].strip())  # Номер даты
        date_month: int = months.index(date_parce_list[1].strip()[:3].lower()) + 1  # Номер месяца
        date_game: date = date(year_current, date_month, date_number)  # Текущая дата (полная)
        date_game_report: str = date_game.strftime('%d.%m.%Y')  # Дата для отчёта
        index_weekday: int = date_game.weekday()
        weekday = dws[index_weekday]  # День недели

        self.__log.print('\n' + str(excel_row_index - 1) + ': ' +
                         date_game.strftime('%d.%m.%y') + ' ' + time_game + ': ' +
                         game_name + ': ' + team1 + ' / ' + team2 + ': ' + line_full_id)

        # Сохранение левой шапки в Excel
        self.__em.write(excel_row_index, 0, line_full_id)
        self.__em.write(excel_row_index, 1, self.__region_name)
        self.__em.write(excel_row_index, 2, date_game_report)
        self.__em.write(excel_row_index, 3, weekday)
        self.__em.write(excel_row_index, 4, time_game)
        self.__em.write(excel_row_index, 5, game_name)
        self.__em.write(excel_row_index, 6, team1)
        self.__em.write(excel_row_index, 7, team2)

        line_full_id_list = line_full_id.split('/')
        line_id = line_full_id_list[0]
        game_id = line_full_id_list[1]

        line_dto = self.__parce_result.lines[line_id]
        game_dto = GameDto(line_full_id, game_id, game_name, date_game_report, time_game, weekday, team1, team2)
        line_dto.games[game_id] = game_dto

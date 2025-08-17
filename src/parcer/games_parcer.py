"""Методы парсинга"""

from datetime import date
import time
from dataclasses import dataclass
from src.utils.logger import Logger

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.ie.webdriver import WebDriver

from src.utils import utils as u
from src.parcer.params_parcer import ParamsParcer, SaveResultDto
from src.utils.excel_manager import ExcelManager
from src.page import Page

@dataclass
class _LeftHeaderDto:
    """Dto левого заголовка"""
    line:  WebElement
    date_parce: str
    excel_row_index: int
    game_id: str
    row: WebElement

months = ['янв', 'фев', 'мар', 'апр', 'мая', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя', 'дек']
dws = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
date_current: date = date.today() # Текущая дата без времени
year_current: int = date_current.year # Текущий год

class GamesParcer:
    """Парсинг игр"""
    page: Page
    drv: WebDriver
    container: WebElement
    log: Logger
    em: ExcelManager

    def __init__(self, page: Page, log: Logger):
        self.page = page
        self.drv = page.drv
        self.container = page.conteiner
        self.log = log
        self.em = ExcelManager()

    def parce(self,  only_id: str) -> None:
        """Парсинг игр"""

        self.em.init_excel()
        self._get_all_games()

        excel_row_index = 2  # Первый индекс строки в Excel

        # Запоминаем предыдущую кнопку для закрытия, перед открытием нового
        button_prev_play = None

        # Группы по линиям
        lines = self.container.find_elements(By.CLASS_NAME, 'line__champ')
        for line in lines:
            date1, date2, game_id_date2 = self._get_game_dates(line)

            # Строки игр в линии
            rows = line.find_elements(By.CLASS_NAME, 'line-event')

            # Цикл по играм
            game_date = date1
            for row in rows:
                # Получение Id игры (для лога и отладки)
                game_id = u.get_id(row.find_element(By.TAG_NAME, 'a'))
                # Поиск конкртеной игры, если есть
                if only_id and game_id != only_id: continue

                # Закрывем предыдущй
                if button_prev_play is not None:
                    self.page.click(button_prev_play)
                    time.sleep(1)

                # Смена даты
                if game_id_date2 == game_id: game_date = date2

                # Парсим и записываем левый заголвоок
                self._write_left_header(_LeftHeaderDto(line, game_date, excel_row_index, game_id, row))

                # Кнопка раскрытия игры
                button_play = row.find_element(By.CLASS_NAME, 'line-event__dops-toggle')
                if button_play.tag_name != 'button': continue  # Игнор не кнопок

                # Клик по раскрывашке (правая колонка)
                self.page.click(button_play)
                is_exist = True
                try:
                    # Ожидаем прогрузки по названию таблицы нижней части коэффициентов (должна быть всегда)
                    self.page.wait(By.XPATH, "//span[starts-with(., 'Тотал')]")
                except NoSuchElementException:
                    is_exist = False
                    self.log.print("Игра отсутствует. Таймаут")

                # Парсим и сохраняем игру
                if is_exist:
                    pp = ParamsParcer(self.log)
                    save_result_dto = self._parce_game(excel_row_index, row, pp)
                    pp.save_to_excel(save_result_dto, self.em)

                button_prev_play = button_play  # Запоминаем кнопку раскрытия
                excel_row_index = excel_row_index + 1

        filename = u.get_filename()  # Имя фалйла скрина и Excel
        self.em.save(filename)

    # Private

    def _get_all_games(self) -> None:
        """Кол-во игр всего"""
        all_games = self.container.find_elements(By.CLASS_NAME, 'line-event')
        row_count = len(all_games)
        self.log.print('\nИгр в обработке: ' + str(row_count))

    @staticmethod
    def _get_game_dates(line:  WebElement) -> tuple[str, str, str]:
        """Дата в формате: {Дата} {Название месяца}. Например: 9 февраля"""
        date_list = line.find_elements(By.CLASS_NAME, 'line-champ__date')
        date1 = date_list[0].text.strip()  # Дата 1 есть всегда
        date2 = ''  # Дата 2 встерчается после 00:00
        game_id_date2 = ''  # id игры, начиная с которой, меняется дата
        if len(date_list) == 2:
            date2 = date_list[1].text.strip()
            # смотрим следующий тэг
            first_row_date2 = date_list[1].find_element(By.XPATH,
                                                        'following-sibling::*[1]')
            # Id игры после смены даты
            a_tag = first_row_date2.find_element(By.CLASS_NAME, 'line-event__name')
            game_id_date2 = u.get_id(a_tag)
        return date1, date2, game_id_date2

    @staticmethod
    def _parce_game(excel_row_index, row: WebElement, pp: ParamsParcer):
        """Парсинг игры"""
        header_line = pp.get_header_params(row)
        # Получение и запись коэффициентов
        row_area = row.find_element(By.XPATH, '..')
        save_result_dto = SaveResultDto(row_area, header_line, excel_row_index)
        return save_result_dto

    def _write_left_header(self, dto: _LeftHeaderDto):
        """Левая шапка. Получение и запись в Excel"""

        # Игра (из заголвока линии)
        game_name = (dto.line.find_element(By.CLASS_NAME, 'line-champ__header-link').text
                     .replace('Футбол.', '').strip())

        # Время игры
        time_game = dto.row.find_element(By.CLASS_NAME, 'line-event__time-static').text.strip()

        # Команды
        teams_block = dto.row.find_element(By.CLASS_NAME, 'line-event__name-teams')
        teams = teams_block.find_elements(By.XPATH, './/*')
        team1 = teams[0].text.strip()
        team2 = teams[1].text.strip()

        # Дата в формате: dd.mm
        date_parce_list = dto.date_parce.split(' ')
        date_number: int = int(date_parce_list[0].strip())  # Номер даты
        date_month: int = months.index(date_parce_list[1].strip()[:3].lower()) + 1  # Номер месяца
        date_game: date = date(year_current, date_month, date_number)  # Текущая дата (полная)
        date_game_report: str = date_game.strftime('%d.%m.%Y')  # Дата для отчёта
        weekday = dws[date_game.weekday()]  # День недели

        self.log.print('\n' + str(dto.excel_row_index - 1) + ': ' +
              date_game.strftime('%d.%m.%y') + ' ' + time_game + ': ' +
              game_name + ': ' + team1 + ' / ' + team2 + ': ' + dto.game_id)

        # Сохранение в Excel
        self.em.write(dto.excel_row_index, 0, date_game_report)
        self.em.write(dto.excel_row_index, 1, weekday)
        self.em.write(dto.excel_row_index, 2, time_game)
        self.em.write(dto.excel_row_index, 3, game_name)
        self.em.write(dto.excel_row_index, 4, team1)
        self.em.write(dto.excel_row_index, 5, team2)

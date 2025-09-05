"""Парсинг результатов игр"""
import os
from dataclasses import dataclass

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from ..utils import Logger
from ..utils import Utils
from ..utils import ExcelManager
from ..page import Page
from ..utils.excel_manager import RESULTS_FOLDER_NAME

@dataclass
class _ResultDto:
    id:  str
    time: str
    team_1: str
    team_2: str
    first_time: str
    total: str

    def __init__(self) -> None:
        self.id = ''
        self.time = ''
        self.team_1 = ''
        self.team_2 = ''
        self.first_time = ''
        self.total = ''

class ResultParcer:
    """Парсинг игр"""
    log: Logger
    em: ExcelManager
    rows: list[tuple[int, str]]

    def __init__(self, log: Logger) -> None:
        self.log = log
        self.em = ExcelManager()
        self.set_exist_data()

    def parce_resuls(self, page: Page):
        for row in self.rows:
            row_index, row_id = row
            target_a: WebElement  # type: ignore
            try:
                target_a = page.conteiner.find_element(By.XPATH, "//a[contains(@href, '" + row_id + "')]")
            except NoSuchElementException:
                self.em.write_empty_cell(row_index, 37)
                self.em.write_empty_cell(row_index, 38)
                self.em.write(row_index, 39, 'Не найден')
                self.log.print(row_id + ' - не найден: ')
                continue

            row_container = target_a.find_element(By.XPATH, '..//..') # Контейнер строки (назад на 2 родителя)
            result = _ResultDto()
            result.id = Utils.get_id(target_a).strip()
            result.time = row_container.find_element(By.CLASS_NAME, 'results-event__time').text.strip()
            teams = target_a.text.split(' — ')
            result.team_1 = teams[0].strip()
            result.team_2 = teams[1].strip()
            score = row_container.find_element(By.CLASS_NAME, 'results-event__score').text.strip()

            # Есть результаты
            if ':' in score:
                sp = score.split(' (')
                # Оба счёта
                if len(sp) > 1:
                    result.total = sp[0].strip()
                    result.first_time = sp[1].strip()[:-1]
                else:
                    # Только финальный
                    result.total = score.strip()

            # если нет результата, то отмена
            if not result.total and not result.first_time:
                self.em.write(row_index, 39, 'Отмена')

            self.em.write(row_index, 37, result.first_time)
            self.em.write(row_index, 38, result.total)
            self.em.write(row_index, 39, '-')

            self.log.print(row_id + ' | ' + result.time + ' | ' +
                      result.team_1 + ' | ' + result.team_2 + ' | ' +
                      result.first_time + ' | ' + result.total)

    def save(self) -> None:
        self.em.save()

    # --- Private

    def _get_yesterday_filename(self) -> str:
        files = os.listdir(RESULTS_FOLDER_NAME)

        # Файл коэффициентов прошлого дня (берем первый со вчерашней датой)
        date_stamp = Utils.get_date_stamp_by_date(Utils.get_yesterday())

        # Поиск файла вчерашнего
        filename = ''
        for file in files:
            if file.startswith(date_stamp): filename = file

        if not filename:
            self.log.print('Вчерашний файл матчей не найден')
            raise SystemExit

        self.log.print('Файл матчей найден: ' + filename)
        return filename

    def set_exist_data(self) -> None:
        """ Список Id на проверку"""
        # Чтение Excel
        excel_filename = self._get_yesterday_filename()
        self.em.load_excel(excel_filename)

        self.rows = self.em.get_rows()
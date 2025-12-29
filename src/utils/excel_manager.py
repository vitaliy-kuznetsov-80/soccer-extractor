from pathlib import Path
import os
from datetime import datetime, timedelta

from xlrd import open_workbook, Book
from xlrd.sheet import Sheet
from xlutils.copy import copy
from xlwt import Workbook, Worksheet, add_palette_colour, easyxf

from . import Utils

add_palette_colour("empty_color", 0x21)
add_palette_colour("gold_color", 0x22)
style_empty_cell = easyxf('pattern: pattern solid, fore_colour empty_color')
style_gold_cell = easyxf('pattern: pattern solid, fore_colour gold_color')
style_def = easyxf('font: name Calibri')

RESULTS_FOLDER_NAME = 'results'

class ExcelManager:
    __filename: str
    __sheet: Worksheet
    __wb_sheet: Sheet
    __wb: Workbook
    __rb: Book

    def init_excel(self, filename: str, day_offset: int = 0) -> None:
        """Создание нового Excel на основе шаблона"""
        # Создание папки результатов, если нет
        Path(RESULTS_FOLDER_NAME).mkdir(parents=True, exist_ok=True)

        # Имя сохраняемого файла
        self.__filename = self._get_result_filename(day_offset)
        # Удаляем файл лога, если с таким-же именем
        if os.path.exists(self.__filename): os.remove(self.__filename)

        """Открытие шаблона Excel и создание копии"""
        self.__rb: Book = open_workbook('assets/' + filename, formatting_info=True)
        self.__wb = copy(self.__rb)
        self.__wb.set_colour_RGB(0x21, 255, 150, 150)
        self.__wb.set_colour_RGB(0x22, 255, 204, 102)
        self.__sheet = self.__wb.get_sheet(0)  # Первая книга

    def load_excel(self, filename: str):
        """Открытие Excel"""
        self.__filename = os.path.join(RESULTS_FOLDER_NAME, filename)
        self.__rb: Book = open_workbook(self.__filename, formatting_info=True)
        self.__wb_sheet = self.__rb.sheet_by_index(0)
        self.__wb = copy(self.__rb)
        self.__sheet = self.__wb.get_sheet(0)  # Первая книга

    def get_row_count(self) -> int:
        return len(self.__sheet.get_rows())

    def get_rows(self) -> list[tuple[int, str]]:
        rows: list[tuple[int, str]] = []
        for row_index in range(self.get_row_count()):
            if row_index < 2: continue
            game_id = str(self.__wb_sheet.cell_value(row_index, 0))
            result_1 = str(self.__wb_sheet.cell_value(row_index, 37))
            result_2 = str(self.__wb_sheet.cell_value(row_index, 38))
            # Добавляем, если нет результатов
            if game_id and (not result_1 or not result_2): rows.append((row_index, game_id))
        return rows

    def save(self):
        self.__wb.save(self.__filename)

    def write_empty_cell(self, row: int, col:int):
        """Запись пустой ячейки"""
        self.__sheet.write(row, col, '', style_empty_cell)

    def write(self, row: int, col:int, value: str):
        if value:
            self.__sheet.write(row, col, value, style_def)
        else:
            self.write_empty_cell(row, col)

    def write_float(self, row: int, col:int, value: str, is_gold: bool = False):
        """Запись числа с точкой в ячейку"""
        if value:
            style = style_gold_cell if is_gold else style_def
            self.__sheet.write(row, col, float(value), style)
        else:
            self.write_empty_cell(row, col)

    @staticmethod
    def get_filename_by_date(date: datetime) -> str:
        """Получает имя файла с результатами вчерашнего дня
        Returns:
            Имя файла с результатами
        """
        files = os.listdir(RESULTS_FOLDER_NAME)

        # Файл коэффициентов прошлого дня (берем первый со вчерашней датой)
        date_stamp = Utils.get_date_stamp_by_date(date)

        # Поиск файла вчерашнего
        filename = ''
        for file in files:
            if file.startswith(date_stamp): filename = file

        return filename

    @staticmethod
    def get_yesterday_filename() -> str:
        return ExcelManager.get_filename_by_date(Utils.get_yesterday())

    @staticmethod
    def get_today_filename(day_offset: int = 0) -> str:
        time_delta = timedelta(hours=day_offset)
        current_date_time = datetime.now() + time_delta

        return ExcelManager.get_filename_by_date(current_date_time)

    @staticmethod
    def _get_result_filename(day_offset: int = 0) -> str:
        filename = Utils.get_filename(day_offset)
        return os.path.join(RESULTS_FOLDER_NAME, filename + '.xls')
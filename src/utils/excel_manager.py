from pathlib import Path
import os

from xlrd import open_workbook, biffh, Book
from xlrd.sheet import Sheet
from xlutils.copy import copy
from xlwt import Workbook, Worksheet, add_palette_colour, easyxf, Row

from . import Utils

add_palette_colour("empty_color", 0x21)
style_empty_cell = easyxf('pattern: pattern solid, fore_colour empty_color')
style_def = easyxf('font: name Calibri')

RESULTS_FOLDER_NAME = 'results'

class ExcelManager:
    filename: str
    sheet: Worksheet
    wb_sheet: Sheet
    wb: Workbook
    rb: Book

    def init_excel(self, filename: str) -> None:
        # Создание папки результатов, если нет
        Path(RESULTS_FOLDER_NAME).mkdir(parents=True, exist_ok=True)

        # Имя сохраняемого файла
        self.filename = self._get_result_filename()
        # Удаляем файл лога, если с таким-же именем
        if os.path.exists(self.filename): os.remove(self.filename)

        """Открытие шаблона Excel и создание копии"""
        self.rb: Book = open_workbook('assets/' + filename, formatting_info=True)
        self.wb = copy(self.rb)
        self.wb.set_colour_RGB(0x21, 255, 150, 150)
        self.sheet = self.wb.get_sheet(0)  # Первая книга

    def load_excel(self, filename: str):
        """Открытие Excel """
        self.filename = os.path.join(RESULTS_FOLDER_NAME, filename)
        self.rb: Book = open_workbook(self.filename, formatting_info=True)
        self.wb_sheet = self.rb.sheet_by_index(0)
        self.wb = copy(self.rb)
        self.sheet = self.wb.get_sheet(0)  # Первая книга

    def get_ids(self) -> list[str]:
        all_data: list[str] = []
        for row_index in range(len(self.sheet.rows)):
            if row_index < 2: continue
            row_values = self.wb_sheet.cell_value(row_index, 0)
            all_data.append(row_values)
        return all_data

    def save(self):
        self.wb.save(self.filename)

    def write_empty_cell(self, row: int, col:int):
        self.sheet.write(row, col, '', style_empty_cell)

    def write(self, row: int, col:int, value: str):
        if value:
            self.sheet.write(row, col, value, style_def)
        else:
            self.write_empty_cell(row, col)

    def write_float(self, row: int, col:int, value: str):
        if value:
            self.sheet.write(row, col, float(value), style_def)
        else:
            self.write_empty_cell(row, col)

    @staticmethod
    def _get_result_filename():
        filename = Utils.get_filename()
        return os.path.join(RESULTS_FOLDER_NAME, filename + '.xls')
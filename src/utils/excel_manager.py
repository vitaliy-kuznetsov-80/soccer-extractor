from pathlib import Path
import os

from xlrd import open_workbook
from xlutils.copy import copy
from xlwt import Workbook, Worksheet, add_palette_colour, easyxf

from . import Utils

add_palette_colour("empty_color", 0x21)
style_empty_cell = easyxf('pattern: pattern solid, fore_colour empty_color')
style_def = easyxf('font: name Calibri')

RESULTS_FOLDER_NAME = 'results'

class ExcelManager:
    filename: str
    sheet: Worksheet
    wb: Workbook

    def init_excel(self) -> None:
        # Создание папки результатов, если нет
        Path(RESULTS_FOLDER_NAME).mkdir(parents=True, exist_ok=True)

        # Имя сохраняемого файла
        self.filename = self._get_result_filename()
        # Удаляем файл лога, если с таким-же именем
        if os.path.exists(self.filename): os.remove(self.filename)

        """Открытие шаблона Excel и создание копии"""
        rb = open_workbook("assets/template.xls", formatting_info=True)
        self.wb = copy(rb)
        self.wb.set_colour_RGB(0x21, 255, 150, 150)
        self.sheet = self.wb.get_sheet(0)  # Первая книга

    def save(self):
        self.wb.save(self.filename)

    def write_empty_cell(self, row: int, col:int):
        self.sheet.write(row, col, '', style_empty_cell)

    def write(self, row: int, col:int, value: str):
        self.sheet.write(row, col, value, style_def)

    def write_float(self, row: int, col:int, value: str):
        self.sheet.write(row, col, float(value), style_def)

    @staticmethod
    def _get_result_filename():
        filename = Utils.get_filename()
        return os.path.join(RESULTS_FOLDER_NAME, 'result' + filename + '.xls')
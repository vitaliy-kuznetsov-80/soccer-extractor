from xlrd import open_workbook
from xlutils.copy import copy
from xlwt import Workbook, Worksheet, add_palette_colour, easyxf

add_palette_colour("empty_color", 0x21)
style_empty_cell = easyxf('pattern: pattern solid, fore_colour empty_color')
style_def = easyxf('font: name Calibri')

class ExcelManager:
    sheet: Worksheet
    wb: Workbook

    def init_excel(self) -> None:
        """Открытие шаблона Excel и создание копии"""
        rb = open_workbook("assets/template.xls", formatting_info=True)
        self.wb = copy(rb)
        self.wb.set_colour_RGB(0x21, 255, 150, 150)
        self.sheet = self.wb.get_sheet(0)  # Первая книга

    def save(self, filename: str):
        self.wb.save('results/result' + filename + '.xls')

    def write_empty_cell(self, row: int, col:int):
        self.sheet.write(row, col, '', style_empty_cell)

    def write(self, row: int, col:int, value: str):
        self.sheet.write(row, col, value, style_def)

    def write_float(self, row: int, col:int, value: str):
        self.sheet.write(row, col, float(value), style_def)
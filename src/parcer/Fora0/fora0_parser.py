"""Фора 0"""

from dataclasses import dataclass

from ..parcer_utils import ParserUtils
from src import Logger
from src.parce_results_dto import GameRowsDto
from src.parcer.Header import HeaderLine

from selenium.webdriver.remote.webelement import WebElement

@dataclass
class Fora0:
    k_1: float | None = None
    k_2: float | None = None

    @staticmethod
    def parse(elem: WebElement, hl: HeaderLine, log: Logger) -> Fora0:
        # Берём из заголовка
        fora_1 = hl.fora1_0_value
        fora_2 = hl.fora2_0_value

        # Берём из таблицы, если в заголовке нет Фор равных нулю
        f1_in_table = hl.fora1_0_key != '0'
        f2_in_table = hl.fora2_0_key != '0'
        if f1_in_table or f2_in_table:
            dto = GameRowsDto(elem, 'Фора', 2)
            rows = ParserUtils.get_rows(dto, log)
            if f1_in_table:
                fora_1 = ParserUtils.get_value(rows, 'Ф1(0)')
            if f2_in_table:
                fora_2 = ParserUtils.get_value(rows, 'Ф2(0)')

        return Fora0(fora_1, fora_2)
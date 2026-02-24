"""Индивидуальный тотал"""

from dataclasses import dataclass

from ..parcer_utils import ParserUtils
from src.parce_results_dto import GameRowsDto
from src import Logger

from selenium.webdriver.remote.webelement import WebElement

@dataclass
class IndividualTotal:
    k1_1_b: str | None = None
    k2_1_b: str | None = None

    @staticmethod
    def parse(elem: WebElement, log: Logger) -> IndividualTotal:
        dto = GameRowsDto(elem, 'Индивидуальный тотал', 2)
        rows = ParserUtils.get_rows(dto, log)

        it1_1 = ParserUtils.get_mb(rows, 'ИТ1(1)Мен')
        it2_1 = ParserUtils.get_mb(rows, 'ИТ2(1)Мен')

        result = IndividualTotal(it1_1.b, it2_1.b)

        return result
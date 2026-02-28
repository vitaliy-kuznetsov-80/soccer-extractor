"""Двойной исход"""

from dataclasses import dataclass

from src import Logger
from ...dto.game_row_dto import GameRowsDto
from ..parcer_utils import ParserUtils
from selenium.webdriver.remote.webelement import WebElement

@dataclass
class DoubleOutcome:
    k_1x: float | None = None
    k_x2: float | None = None

    @staticmethod
    def parse(element: WebElement, log: Logger) -> DoubleOutcome:
        dto = GameRowsDto(element, 'Двойной исход', 2)
        rows = ParserUtils.get_rows(dto, log)

        value_1x = ParserUtils.get_value(rows, '1X')
        value_x2 = ParserUtils.get_value(rows, 'X2')

        return DoubleOutcome(value_1x, value_x2)
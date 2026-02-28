"""Голы"""

from dataclasses import dataclass

from ..parcer_utils import ParserUtils
from ...dto.game_row_dto import GameRowsDto
from src import Logger

from selenium.webdriver.remote.webelement import WebElement

@dataclass
class Goals:
    k_1: float | None = None
    k_2: float | None = None

    @staticmethod
    def parse(element: WebElement, log: Logger) -> Goals:
        dto = GameRowsDto(element, 'Голы', 2)
        rows = ParserUtils.get_rows(dto, log)
        g1 = ParserUtils.get_value(rows, 'К1Забьет')
        g2 = ParserUtils.get_value(rows, 'К2Забьет')

        return Goals(g1, g2)
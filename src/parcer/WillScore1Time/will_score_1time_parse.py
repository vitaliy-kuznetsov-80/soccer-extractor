"""1-й тайм забьет"""

from dataclasses import dataclass

from src import Logger
from ...dto.game_row_dto import GameRowsDto
from ..parcer_utils import ParserUtils
from selenium.webdriver.remote.webelement import WebElement

@dataclass
class WillScore1Time:
    k_1_yes: float | None = None
    k_2_yes: float | None = None

    @staticmethod
    def parse( element: WebElement, log: Logger) -> WillScore1Time:
        dto = GameRowsDto(element, '1-й тайм забьет', 2)
        rows = ParserUtils.get_rows(dto, log)

        k1_yes = ParserUtils.get_value(rows, 'K1Да')
        k2_yes = ParserUtils.get_value(rows, 'K2Да')

        return WillScore1Time(k1_yes, k2_yes)

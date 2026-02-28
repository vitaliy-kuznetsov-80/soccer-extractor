"""Обе забьют"""

from dataclasses import dataclass

from ..parcer_utils import ParserUtils
from src import Logger
from ...dto.game_row_dto import GameRowsDto

from selenium.webdriver.remote.webelement import WebElement

@dataclass
class BothWillScore:
    yes: float | None = None
    no: float | None = None

    @staticmethod
    def parse(element: WebElement, log: Logger) -> BothWillScore:
        dto = GameRowsDto(element, 'Обе забьют', 2)
        rows = ParserUtils.get_rows(dto, log)

        k_yes = ParserUtils.get_value(rows, 'Да')
        k_no = ParserUtils.get_value(rows, 'Нет')

        return BothWillScore(k_yes, k_no)
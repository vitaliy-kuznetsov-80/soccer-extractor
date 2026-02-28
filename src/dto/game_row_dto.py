from dataclasses import dataclass

from selenium.webdriver.remote.webelement import WebElement


@dataclass
class GameRowsDto:
    """Dto строки игры"""
    element: WebElement
    block_name: str
    col_count: int
    block_column: str = ''

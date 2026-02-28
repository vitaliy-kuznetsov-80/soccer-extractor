import json
from dataclasses import dataclass, field

from selenium.webdriver.remote.webelement import WebElement

from .k_matrix_gold_dto import MatrixGoldRegionDto
from .line_dto import LineDto
from .region_enum import RegionEnum
from src.utils import Logger, Config
from src.page import Page

@dataclass
class ParceResultsDto:
    """Информационный класс с результатами парсинга"""
    region: RegionEnum
    region_name: str
    page: Page
    log: Logger
    conf: Config
    container: WebElement
    k_matrix_gold: MatrixGoldRegionDto | None = None
    lines:  dict[str, LineDto] = field(default_factory=dict)

    def save(self, filename: str) -> None:
        """Конвертирует объект в JSON, исключая указанные поля"""
        obj_dict = {
            'region_name': self.region_name,
            # 'gold_k_matrix': self.gold_matrix_list,
            'lines': self.lines,
        }

        with open(filename, "w") as file:
            json.dumps(obj_dict, file=file, default=str, indent=4)
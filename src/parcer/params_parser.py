"""Методы парсинга"""

from dataclasses import dataclass

from selenium.webdriver.remote.webelement import WebElement

from .Header import HeaderLine
# from ..KMatrix import KMatrix
from ..parce_results_dto import ParceResultsDto
from ..utils import Logger
from ..utils import ExcelManager

from .Outcome import Outcome
from .Total import Total
from .DoubleOutcome import DoubleOutcome
from .Fora0 import Fora0
from .Goals import Goals
from .BothWillScore import BothWillScore
from .WillScore1Time import WillScore1Time
from .Total1Time import Total1Time
from .IndividualTotal import IndividualTotal

@dataclass
class SaveResultDto:
    """Dto сохранения"""
    element: WebElement
    header_line: HeaderLine
    row_index: int

class ParamsParser:
    __log: Logger
    __parce_result: ParceResultsDto
    __line_id: str
    __game_id: str

    def __init__(self, parce_result: ParceResultsDto, line_id: str, game_id: str):
        self.__parce_result = parce_result
        self.__log = parce_result.log
        self.__line_id = line_id
        self.__game_id = game_id

    def save_to_excel(self, dto: SaveResultDto, em: ExcelManager):
        """Сохранение параметров в Excel"""

        # Парсинг коэффициентов
        outcome = Outcome.parse(dto.header_line)
        total = Total.parse(dto.element, dto.header_line, self.__log)
        double_result = DoubleOutcome.parse(dto.element, self.__log)
        fora_0 = Fora0.parse(dto.element, dto.header_line, self.__log)
        goals = Goals.parse(dto.element, self.__log)
        both_will_score = BothWillScore.parse(dto.element, self.__log)
        will_score_1_time = WillScore1Time.parse(dto.element, self.__log)
        total_1time = Total1Time.parse(dto.element, self.__log)
        individual_total = IndividualTotal.parse(dto.element, self.__log)

        # Заполнение матрицы
        # game_k_matrix = KMatrix()
        # game_k_matrix.outcome = outcome
        # game_k_matrix.double_result = double_result
        # game_k_matrix.fora_0 = fora_0
        # game_k_matrix.goals = goals
        # game_k_matrix.both_will_score = both_will_score
        # game_k_matrix.will_score_1_time = will_score_1_time
        # game_k_matrix.total_1time = total_1time
        # game_k_matrix.total = total
        # game_k_matrix.individual_total = individual_total
        # self.__parce_result.lines[self.__line_id].games[self.__game_id].k_matrix = game_k_matrix

        # Индекс колонки, начиная с котрой заполняются коэффициенты
        col_index = 8

        def write(value: str | None = None):
            nonlocal col_index

            is_gold = False
            # Если None, то прочерк
            if value is not None:
                em.write_float(dto.row_index, col_index, value, is_gold)
            else:
                em.write_empty_cell(dto.row_index, col_index)
            col_index = col_index + 1

        # gold = self.__parce_result.gold_matrix_list

        write(outcome.k_1)
        write(outcome.k_x)
        write(outcome.k_2)

        write(fora_0.k_1)
        write(fora_0.k_2)

        write(double_result.k_1x)
        write(double_result.k_x2)

        write(goals.k_1)
        write(goals.k_2)

        write(both_will_score.yes)
        write(both_will_score.no)

        write(total.k_1_5.m)
        write(total.k_1_5.b)
        write(total.k_2.m)
        write(total.k_2.b)
        write(total.k_2_5.m)
        write(total.k_2_5.b)
        write(total.k_3.m)
        write(total.k_3.b)
        write(total.k_3_5.m)
        write(total.k_3_5.b)
        write(total.k_4.m)
        write(total.k_4.b)
        write(total.k_4_5.m)
        write(total.k_4_5.b)

        write(individual_total.k1_1_b)
        write(individual_total.k2_1_b)

        write(total_1time.k_1b)
        write(total_1time.k_1_5m)
        write(total_1time.k_2b)

        write(will_score_1_time.k_1_yes)
        write(will_score_1_time.k_2_yes)

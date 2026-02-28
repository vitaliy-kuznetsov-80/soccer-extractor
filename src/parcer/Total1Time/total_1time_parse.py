"""Тотал 1 Тайм"""
from dataclasses import dataclass

from src import Logger
from ..parcer_utils import ParserUtils
from ...dto.game_row_dto import GameRowsDto

from selenium.webdriver.remote.webelement import WebElement

@dataclass
class Total1TimeExtra:
    k_1b: float | None = None
    k_2b: float | None = None

@dataclass
class OutcomeByTime1t:
    k_1b: float | None = None
    k_1_5b: float | None = None

@dataclass
class Total1Time:
    k_1b: float | None = None
    k_1_5m: float | None = None
    k_2b: float | None = None

    @staticmethod
    def parse(el: WebElement, log: Logger) -> Total1Time:
        total_1time_extra = Total1Time.get_total_1time_extra(el, log)
        outcome_by_time_1t = Total1Time.get_outcome_by_time_1t(el, log)

        t1_b = total_1time_extra.k_1b
        if t1_b == '':
            t1_b = outcome_by_time_1t.k_1b

        t1_5_b = outcome_by_time_1t.k_1_5b
        t2_b = total_1time_extra.k_2b
        return Total1Time(t1_b, t1_5_b, t2_b)

    @staticmethod
    def get_outcome_by_time_1t(el: WebElement, log: Logger) -> OutcomeByTime1t:
        """Исходы по таймам (1т, ТБ 1, 1.5)"""
        dto = GameRowsDto(el, 'Исходы по таймам', 2, '1-й тайм')
        rows = ParserUtils.get_rows(dto, log)
        tb1 = ParserUtils.get_mb(rows, 'ТБ(1)')
        tb1_5 = ParserUtils.get_mb(rows, 'ТБ(1.5)')
        return OutcomeByTime1t(tb1.m, tb1_5.m)

    @staticmethod
    def get_total_1time_extra(el: WebElement, log: Logger) -> Total1TimeExtra:
        """Доп. тоталы 1-й тайм"""
        dto = GameRowsDto(el, 'Доп. тоталы 1-й тайм', 2)
        rows = ParserUtils.get_rows(dto, log)
        value_1 = ParserUtils.get_mb(rows, '1Мен')
        value_2 = ParserUtils.get_mb(rows, '2Мен')
        return Total1TimeExtra(value_1.b, value_2.b)
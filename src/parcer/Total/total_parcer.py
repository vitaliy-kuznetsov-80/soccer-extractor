from dataclasses import dataclass

from src import Logger
from src.parce_results_dto import MB, GameRowsDto
from ..parcer_utils import ParserUtils
from src.parcer.Header import HeaderLine
from selenium.webdriver.remote.webelement import WebElement

@dataclass
class Total:
    k_1_5: MB | None = None
    k_2: MB | None = None
    k_2_5: MB | None = None
    k_3: MB | None = None
    k_3_5: MB | None = None
    k_4: MB | None = None
    k_4_5: MB | None = None

    @staticmethod
    def parse(elem: WebElement, hl: HeaderLine, log: Logger) -> Total:
        """Тотал. Берется из таблицы тотал. Недостающие коэффициенты добавляются из заголовка"""
        dto = GameRowsDto(elem, 'Тотал', 2)
        rows = ParserUtils.get_rows(dto, log)

        k_1_5 = ParserUtils.get_mb(rows, '1.5Мен')
        k_2 = ParserUtils.get_mb(rows, '2Мен')
        k_2_5 = ParserUtils.get_mb(rows, '2.5Мен')
        k_3 = ParserUtils.get_mb(rows, '3Мен')
        k_3_5 = ParserUtils.get_mb(rows, '3.5Мен')
        k_4 = ParserUtils.get_mb(rows, '4Мен')
        k_4_5 = ParserUtils.get_mb(rows, '4.5Мен')

        result = Total(k_1_5, k_2, k_2_5, k_3, k_3_5, k_4, k_4_5)

        # Добавляем из заголовка, если коэффициента в заголовке нет в таблице
        if hl.total_key:
            header_total_key = 'k_' + hl.total_key.replace('.', '_') # приводим к виду ключа Dto
            setattr(result, header_total_key, MB(hl.total_m_value, hl.total_b_value))
            log.print('     ' + hl.total_key + 'Мен: ' + str(hl.total_m_value) + ' | Бол: ' + str(hl.total_b_value) + ' [Заг]')

        return result
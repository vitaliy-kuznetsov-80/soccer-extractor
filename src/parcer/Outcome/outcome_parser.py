"""Исходы. Берутся из заголовка"""

from dataclasses import dataclass

from src.parcer.Header import HeaderLine

@dataclass
class Outcome:
    k_1: float | None = None
    k_x: float | None = None
    k_2: float | None = None

    @staticmethod
    def parse(header_line: HeaderLine) -> Outcome:
        return Outcome(header_line.outcome_1, header_line.outcome_x, header_line.outcome_2)
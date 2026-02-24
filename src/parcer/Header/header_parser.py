"""Параметры заголовка игры"""

from dataclasses import dataclass

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from src import Utils

@dataclass
class HeaderLine:
    outcome_1: str | None = None
    outcome_x: str | None = None
    outcome_2: str | None = None

    fora1_0_key: str | None = None
    fora1_0_value: str | None = None

    fora2_0_key: str | None = None
    fora2_0_value: str | None = None

    total_key: str | None = None
    total_m_value: str | None = None
    total_b_value: str | None = None

    @staticmethod
    def parse(row: WebElement) -> HeaderLine:
        # Div линии заголовка
        div_line_div = row.find_element(By.CLASS_NAME, "line-event__main-bets")

        # Список тэгов внутри Div
        header_list = div_line_div.find_elements(By.XPATH, './/*')
        # Извлечения текста из списка тэгов
        header_line = []
        for item in header_list:
            header_line.append(Utils.clean_text(item.text))


        return HeaderLine(
            header_line[0], header_line[1], header_line[2],
            header_line[3], header_line[4],
            header_line[5], header_line[6],
            header_line[7], header_line[8], header_line[9]
        )

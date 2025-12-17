"""Методы парсинга"""

import typing as t
from dataclasses import dataclass

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common import NoSuchElementException

from ..utils import Logger
from ..utils import ExcelManager

@dataclass
class SaveResultDto:
    """Dto сохранения"""
    element: WebElement
    header_line: t.List[str]
    row_index: int

@dataclass
class GameRowsDto:
    """Dto строки игры"""
    element: WebElement
    block_name: str
    col_count: int
    block_column: str = ''

class ParamsParser:
    __log: Logger

    def __init__(self, log: Logger):
        self.__log = log

    def get_header_params(self, row: WebElement):
        """Параметры заголовка игры"""
        # Линия заголовка. Массив значений
        div_line_div = row.find_element(By.CLASS_NAME, "line-event__main-bets")
        # Парсинг заголовка
        header_list = div_line_div.find_elements(By.XPATH, './/*')
        header_line = []
        for item in header_list:
            header_line.append(self._clean_text(item.text))

        return {
            'outcome_1': header_line[0],
            'outcome_X': header_line[1],
            'outcome_2': header_line[2],
            'fora1_0_key': header_line[3],
            'fora1_0_value': header_line[4],
            'fora2_0_key': header_line[5],
            'fora2_0_value': header_line[6],
            'total_key': header_line[7],
            'total_m_value': header_line[8],
            'total_b_value': header_line[9],
        }

    def save_to_excel(self, dto: SaveResultDto, em: ExcelManager):
        """Сохранение параметров в Excel"""
        outcome = self.get_outcome(dto.header_line)
        total = self.get_total(dto.element, dto.header_line)
        double_result = self.get_double_outcome(dto.element)
        fora_0 = self.get_fora_0(dto.element, dto.header_line)
        goals = self.get_goals(dto.element)
        both_will_score = self.get_both_will_score(dto.element)
        will_score_1_time = self.get_will_score_1_time(dto.element)
        total_1time = self.get_total_1time(dto.element)

        # Индекс колонки, начиная с котрой заполняются коэффициенты
        col_index = 8

        def write(value):
            nonlocal col_index
            # Если не вещественное число, то прочерк
            try:
                float(value)
                em.write_float(dto.row_index, col_index, value)
            except ValueError:
                em.write_empty_cell(dto.row_index, col_index)
            col_index = col_index + 1

        write(outcome['1'])
        write(outcome['X'])
        write(outcome['2'])

        write(fora_0['1'])
        write(fora_0['2'])

        write(double_result['1X'])
        write(double_result['X2'])

        write(goals['1'])
        write(goals['2'])

        write(both_will_score['yes'])
        write(both_will_score['no'])

        write(total['1.5']['m'])
        write(total['1.5']['b'])
        write(total['2']['m'])
        write(total['2']['b'])
        write(total['2.5']['m'])
        write(total['2.5']['b'])
        write(total['3']['m'])
        write(total['3']['b'])
        write(total['3.5']['m'])
        write(total['3.5']['b'])
        write(total['4']['m'])
        write(total['4']['b'])
        write(total['4.5']['m'])
        write(total['4.5']['b'])

        write(total_1time['1'])
        write(total_1time['1.5'])
        write(total_1time['2'])

        write(will_score_1_time['1'])
        write(will_score_1_time['2'])

    # Методы парсинга конкретных таблиц

    @staticmethod
    def get_outcome(header_line):
        """Исходы"""
        return {
            '1': header_line['outcome_1'],
            'X': header_line['outcome_X'],
            '2': header_line['outcome_2']
        }

    def get_fora_0(self, element: WebElement, header_line):
        """Фора 0"""
        fora_1 = header_line['fora1_0_value']
        fora_2 = header_line['fora2_0_value']

        # Если берём из таблицы
        f1_in_table = header_line['fora1_0_key'] != '0'
        f2_in_table = header_line['fora2_0_key'] != '0'
        if f1_in_table or f2_in_table:
            dto = GameRowsDto(element, 'Фора', 2)
            rows = self._get_rows(dto)
            if f1_in_table:
                fora_1 = self._get_value(rows, 'Ф1(0)')
            if f2_in_table:
                fora_2 = self._get_value(rows, 'Ф2(0)')

        return { '1': fora_1, '2': fora_2 }

    def get_double_outcome(self, element: WebElement):
        """Двойной исход"""
        dto = GameRowsDto(element, 'Двойной исход', 2)
        rows = self._get_rows(dto)
        value_1x = self._get_value(rows, '1X')
        value_x2 = self._get_value(rows, 'X2')
        return { '1X': value_1x, 'X2': value_x2 }

    def get_goals(self, element: WebElement):
        """Голы"""
        dto = GameRowsDto(element, 'Голы', 2)
        rows = self._get_rows(dto)
        g1 = self._get_value(rows, 'К1Забьет')
        g2 = self._get_value(rows, 'К2Забьет')
        return { '1': g1, '2': g2 }

    def get_both_will_score(self, element: WebElement):
        """Обе забьют"""
        dto = GameRowsDto(element, 'Обе забьют', 2)
        rows = self._get_rows(dto)
        return {
            'yes': self._get_value(rows, 'Да'),
            'no': self._get_value(rows, 'Нет')
        }

    def get_total(self, element: WebElement, header_line):
        """Тотал"""
        dto = GameRowsDto(element, 'Тотал', 2)
        rows = self._get_rows(dto)

        result = {
            '1.5': self._get_mb(rows, '1.5Мен'),
            '2': self._get_mb(rows, '2Мен'),
            '2.5': self._get_mb(rows, '2.5Мен'),
            '3': self._get_mb(rows, '3Мен'),
            '3.5': self._get_mb(rows, '3.5Мен'),
            '4': self._get_mb(rows, '4Мен'),
            '4.5': self._get_mb(rows, '4.5Мен')
        }

        # Добавляем из заголовка
        total_header = header_line['total_key']
        total_header_m = header_line['total_m_value']
        total_header_b = header_line['total_b_value']
        result[total_header] = { 'm': total_header_m, 'b': total_header_b }
        self.__log.print('     ' + total_header + 'Мен: ' + total_header_m + ' | Бол: ' + total_header_b + ' [Заг]')

        return result

    def get_outcome_by_time_1t(self, element: WebElement):
        """Исходы по таймам (1т, ТБ 1, 1.5)"""
        dto = GameRowsDto(element, 'Исходы по таймам', 2, '1-й тайм')
        rows = self._get_rows(dto)
        tb1 = self._get_mb(rows, 'ТБ(1)')['m']
        tb1_5 = self._get_mb(rows, 'ТБ(1.5)')['m']
        return { '1': tb1, '1.5': tb1_5 }

    def get_total_1time_extra(self, element: WebElement):
        """Доп. тоталы 1-й тайм"""
        dto = GameRowsDto(element, 'Доп. тоталы 1-й тайм', 2)
        rows = self._get_rows(dto)
        value_1b = self._get_mb(rows, '1Мен')['b']
        value_2b = self._get_mb(rows, '2Мен')['b']
        return {'1': value_1b, '2': value_2b}

    def get_total_1time(self, element: WebElement):
        """get total 1 time"""
        total_1time_extra = self.get_total_1time_extra(element)
        outcome_by_time_1t = self.get_outcome_by_time_1t(element)

        t1 = total_1time_extra['1']
        if t1 == '':
            t1 = outcome_by_time_1t['1']

        t1_5 = outcome_by_time_1t['1.5']
        t2 = total_1time_extra['2']
        return {'1': t1, '1.5': t1_5, '2': t2}

    def get_will_score_1_time(self, element: WebElement):
        """1-й тайм забьет"""
        dto = GameRowsDto(element, '1-й тайм забьет', 2)
        rows = self._get_rows(dto)
        k1 = self._get_value(rows, 'K1Да')
        k2 = self._get_value(rows, 'K2Да')
        return {'1': k1, '2': k2}

    # Private

    def _get_rows(self, dto: GameRowsDto) -> t.List[str]:
        """Парсинг строк таблицы блока"""
        rows: list[str] = []
        self.__log.print('  - ' + dto.block_name)

        # Поиск заголовка
        try:
            header = dto.element.find_element(By.XPATH, "//span[text()='" + dto.block_name + "']")
        except NoSuchElementException:
            self.__log.print('Таблица "' + dto.block_name + '" не найдена')
            return rows

        block: WebElement = header.find_element(By.XPATH, '..//..')

        # Если строки объедены в блоки (например, Исходы по таймам)
        column = dto.block_column
        if column != '':
            try:
                path_prefix = "//div[contains(@class, 'dops-item-row')]//div[contains(@class, 'dops-item-row__title')]"
                path = path_prefix + "//span[contains(text(),'" + column + "')]"
                table_column = block.find_element(By.XPATH, path)
                block = table_column.find_element(By.XPATH, '..//..')
            except NoSuchElementException:
                self.__log.print('Блок "' + column + '" в таблице "' + dto.block_name + '" не найден')
                return rows

        # Поиск списка строк
        table = block.find_elements(By.CLASS_NAME, 'dops-item-row__section')

        # Считываем строки
        for row in table:
            row_text = (self._clean_text(row.text.strip())
                        .replace(' (', '(')
                        .replace('Не забьет', 'Незабьет')
                        .replace('Не будет', 'Небудет')
                        .replace('Нет голов', 'Нетголов'))

            # Если заголовок состоит из двух колонок (например, Тотал)
            # То их объединяем
            cols = row_text.split(' ')
            try:
                float(cols[1])
            except ValueError:
                cols[0] = cols[0] + cols[1]
                del cols[1]

            # 1 колонка
            print_value = self._add_row(0, cols, rows)

            # 2 колонка
            if len(cols) > 3:
                print_value = print_value + ' | ' + self._add_row(2, cols, rows)
            # Должна быть 2 колонка, но её нет
            if len(cols) < 3 and dto.col_count == 2:
                print_value = print_value + ' | ' + self._add_empty_row(rows)

            # 3 колонка
            if len(cols) > 5:
                print_value = print_value + ' | ' + self._add_row(4, cols, rows)
            # Должна быть 2 колонка, но её нет
            if len(cols) < 5 and dto.col_count == 3:
                header3 = ''
                value3 = ''
                rows.append(header3)
                rows.append(value3)
                print_value = print_value + ' | ' + header3 + ': ' + value3

            self.__log.print('     ' + print_value)

        return rows

    @staticmethod
    def _add_row(start_index: int, cols: list[str], rows: list[str]):
        """Заполнение массива строк"""
        header = cols[start_index]
        value = cols[start_index + 1]
        rows.append(header)
        rows.append(value)
        return header + ': ' + value

    @staticmethod
    def _get_mb(rows: t.List[str], value: str):
        """Получить M, B"""
        try:
            index = rows.index(value)
        except ValueError:
            return { 'm': '', 'b': '' }
        m = rows[index + 1]
        b: str = ''
        if index + 3 < len(rows):
            b = rows[index + 3]
        return { 'm': m, 'b': b }

    @staticmethod
    def _add_empty_row(rows: list[str]):
        """Заполнение массива строк, если пусто"""
        header = ''
        value = ''
        rows.append(header)
        rows.append(value)
        return header + ': ' + value

    @staticmethod
    def _get_value(rows: t.List[str], name: str) -> str:
        """Значение в строке по названию"""
        if name in rows:
            cell_index = rows.index(name)
            return rows[cell_index + 1]
        return ''

    @staticmethod
    def _clean_text(value: str) -> str:
        """Очистка текста"""
        return value.strip().replace('\n', ' ').replace('  ', ' ').replace('  ', ' ')

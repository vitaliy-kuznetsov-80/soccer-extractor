import typing as t

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common import NoSuchElementException

from src import Utils, Logger
from src.parce_results_dto import GameRowsDto, MB

class ParserUtils:
    @staticmethod
    def get_rows(dto: GameRowsDto, log: Logger) -> t.List[str]:
        """Парсинг строк таблицы блока"""
        rows: list[str] = []
        log.print('  - ' + dto.block_name)

        # Поиск заголовка
        try:
            header = dto.element.find_element(By.XPATH, "//span[text()='" + dto.block_name + "']")
        except NoSuchElementException:
            log.print('Таблица "' + dto.block_name + '" не найдена')
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
                log.print('Блок "' + column + '" в таблице "' + dto.block_name + '" не найден')
                return rows

        # Поиск списка строк
        table = block.find_elements(By.CLASS_NAME, 'dops-item-row__section')

        # Считываем строки
        for row in table:
            row_text = (Utils.clean_text(row.text.strip())
                        .replace(' (', '(')
                        .replace('Не забьет', 'Незабьет')
                        .replace('Не будет', 'Небудет')
                        .replace('Нет голов', 'Нетголов'))

            # Если заголовок состоит из двух колонок (например, Тотал), то их объединяем
            cols = row_text.split(' ')
            try:
                float(cols[1])
            except ValueError:
                cols[0] = cols[0] + cols[1]
                del cols[1]

            # 1 колонка
            print_value = ParserUtils._add_row(0, cols, rows)

            # 2 колонка
            if len(cols) > 3:
                print_value = print_value + ' | ' + ParserUtils._add_row(2, cols, rows)
            # Должна быть 2 колонка, но её нет
            if len(cols) < 3 and dto.col_count == 2:
                print_value = print_value + ' | ' + ParserUtils._add_empty_row(rows)

            # 3 колонка
            if len(cols) > 5:
                print_value = print_value + ' | ' + ParserUtils._add_row(4, cols, rows)
            # Должна быть 2 колонка, но её нет
            if len(cols) < 5 and dto.col_count == 3:
                header3 = ''
                value3 = ''
                rows.append(header3)
                rows.append(value3)
                print_value = print_value + ' | ' + header3 + ': ' + value3

            log.print('     ' + print_value)

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
    def get_mb(rows: t.List[str], value: str) -> MB:
        """Получить M, B"""
        try:
            index = rows.index(value)
        except ValueError:
            return MB()
        m = rows[index + 1]
        b: str = ''
        if index + 3 < len(rows):
            b = rows[index + 3]
        return MB(m,b)

    @staticmethod
    def _add_empty_row(rows: list[str]):
        """Заполнение массива строк, если пусто"""
        header = ''
        value = ''
        rows.append(header)
        rows.append(value)
        return header + ': ' + value

    @staticmethod
    def get_value(rows: t.List[str], name: str) -> float | None:
        """Значение в строке по названию"""
        if name in rows:
            cell_index = rows.index(name)
            value = rows[cell_index + 1]
            if value is None:
                return None
            return float(value)
        return None
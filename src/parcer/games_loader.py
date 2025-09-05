"""Поментка линий чекбоксами для загрузки игр"""

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

from ..utils import Utils
from ..utils import Logger
from ..page import Page

class GamesLoader:
    """Загрузка игр линий"""
    page: Page
    drv: WebDriver
    container: WebElement
    log: Logger

    def __init__(self, page: Page, log: Logger):
        self.page = page
        self.drv = page.drv
        self.container = page.conteiner
        self.log = log

    def mark_lines(self, limit_count: int, only_id: str) -> None:
        """Пометка строк для получения игр через checkbox"""

        # Таблица парсинга. Берём только левую (СОБЫТИЯ)
        tables = self.container.find_elements(By.CLASS_NAME, 'champs__sport')[0]

        # Список строк линий
        rows = tables.find_elements(By.CLASS_NAME, 'champs__champ')
        self.log.print('Найдено линий: ' + str(len(rows)))

        # Фильтрация строк
        self.log.print('Фильтрованные линии: ')
        count = 0
        ignore_list = self._get_ignore_list()  # Читаем слова-исключения из файла
        for row in rows:
            # Ограничние линий
            if 0 < limit_count < count: break

            # Ссылка на линию с названием
            a_tag = row.find_element(By.CLASS_NAME, 'champs__champ-name')
            line_id = Utils.get_id(a_tag, 'ts=24')
            # Поиск конкртеной линии, если есть
            if only_id and line_id != only_id: continue

            line_text = a_tag.text.strip()  # Название линии

            # Игнор согласно списку
            is_ignore = False
            for item in ignore_list:
                # Найден игнор. Выходим из цикла списка игоноров
                if line_text.find(item) > -1:
                    is_ignore = True
                    break

            # Если игнор, то переходим к следующей игре
            if is_ignore:
                self.log.print('  - ' + line_text)
                continue

            self.log.print('  ' +  line_text)

            # Пометка линии через щелчок по checkbox
            checkbox = row.find_element(By.CLASS_NAME, 'checkbox__mark')
            self.page.click(checkbox)

            if only_id != '': break

            count = count + 1

        self.log.print('Фильтрованых линий: ' + str(count))

    def load_games(self) -> None:
        """Загрузка игр для выбранных линий"""
        # Жмём "Показать" для отображения игр
        button_find = self.container.find_element(By.CLASS_NAME, 'line__controls-button')
        self.page.click(button_find)

        # Ждём загрузки игр
        self.page.wait(By.CLASS_NAME, 'line-event')

    # Private

    @staticmethod
    def _get_ignore_list() -> list[str]:
        """Список фраз - исключений"""
        with open('assets/ignore-soccer.txt', encoding='utf-8') as file:
            result = file.read().splitlines()
            file.close()
            return result

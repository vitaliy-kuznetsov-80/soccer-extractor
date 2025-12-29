"""Пометка линий чек-боксами для загрузки игр"""
from dataclasses import dataclass

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

from ..utils import Utils
from ..utils import Region
from ..utils import Logger
from ..page import Page

@dataclass
class Line:
    id: str
    name_original: str
    name_white: str

class LinesParser:
    """Загрузка игр линий"""
    __page: Page
    __container: WebElement
    __log: Logger
    __game_list: list[Line] = []

    def __init__(self, page: Page, log: Logger):
        self.__page = page
        self.__container = page.container
        self.__log = log

    def lost_lines(self) -> None:
        """Проверка линий, которые недоступны для парсинга"""
        rows = self._get_lines()

        # Получаем списки
        ignore_list = self._get_ignore_list()
        europe_list = self._get_white_list(Region.EUROPE)
        america_list = self._get_white_list(Region.AMERICA)
        asia_list = self._get_white_list(Region.ASIA)

        white_list = set(europe_list + america_list + asia_list)

        self.__log.print('Потерянные линии для всех регионов:')
        is_lost = False
        for row in rows:
            a_tag = row.find_element(By.CLASS_NAME, 'champs__champ-name')
            line_name = a_tag.text.strip()
            line_name_compare = Utils.normalize_text(line_name)

            # Проверка вхождения слов
            in_ignore = False
            for item in ignore_list:
                if Utils.normalize_text(item) in line_name_compare:
                    in_ignore = True
                    break

            in_white = False
            for item in white_list:
                if Utils.normalize_text(item) in line_name_compare:
                    in_white = True
                    break

            # Если не в игнор-листе и не в белом списке — значит потеряшка
            if not in_ignore and not in_white:
                self.__log.print(' - ' + line_name)
                is_lost = True

        if not is_lost:
            self.__log.print('ОТСУТСТВУЮТ')

    def mark_lines(self, limit_count: int, only_id: str, region: Region) -> None:
        """Пометка строк для получения игр через checkbox"""
        rows = self._get_lines()
        self.__log.print('Найдено линий: ' + str(len(rows)))

        # Фильтрация строк
        self.__log.print('Фильтрованные линии: ')
        count = 0
        ignore_list = self._get_ignore_list()  # Читаем слова-исключения из файла

        # Читаем белый список
        white_list: list[str] = self._get_white_list(region)

        for row in rows:
            # Ограничение линий
            if 0 < limit_count < count: break

            # Ссылка на линию с названием
            a_tag = row.find_element(By.CLASS_NAME, 'champs__champ-name')
            line_id = Utils.get_id(a_tag, 'ts=24')
            # Поиск конкретной линии, если есть
            if only_id and line_id != only_id: continue

            line_name_original = a_tag.text.strip()  # Название линии

            # Игнор согласно игнор-списку
            if any(word in line_name_original for word in ignore_list):
                self.__log.print('  - ИГНОР - ' + line_name_original)
                continue

            # Не попал в белый список
            if not any(word in line_name_original for word in white_list):
                self.__log.print('  - ПРОПУСК - ' + line_name_original)
                continue

            line_name_white = ''
            for item in white_list:
                if item in line_name_original:
                    line_name_white = item
                    break

            line_obj = Line(line_id, line_name_original,line_name_white)
            self.__game_list.append(line_obj)
            self.__log.print('  ' + line_name_original)

            # Пометка линии через щелчок по checkbox
            checkbox = row.find_element(By.CLASS_NAME, 'checkbox__mark')
            self.__page.click(checkbox)

            if only_id != '': break

            count = count + 1

        self.__log.print('Фильтрованных линий: ' + str(count))

    def load_games(self) -> None:
        """Загрузка игр для выбранных линий"""
        # Жмём "Показать" для отображения игр
        button_find = self.__container.find_element(By.CLASS_NAME, 'line__controls-button')
        self.__page.click(button_find)

        # Ждём загрузки игр
        self.__page.wait(By.CLASS_NAME, 'line-event')

    # --- Private

    @staticmethod
    def _get_ignore_list() -> list[str]:
        """Список фраз - исключений"""
        return Utils.get_text_list('ignore-soccer.txt')

    @staticmethod
    def _get_white_list(region: Region) -> list[str]:
        """Белый список"""
        return Utils.get_text_list(str(region.value) + '.txt')

    def _get_lines(self) -> list[WebElement]:
        # Таблица парсинга. Берём только левую (СОБЫТИЯ)
        tables = self.__container.find_elements(By.CLASS_NAME, 'champs__sport')[0]

        # Список строк линий
        rows = tables.find_elements(By.CLASS_NAME, 'champs__champ')
        return rows
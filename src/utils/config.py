from pathlib import Path
import json

# Имена полей JSON
PAGE_LOAD_TIMEOUT: str = 'page_load_timeout'
ELEMENT_LOAD_TIMEOUT: str = 'element_load_timeout'
LOG_IN_CONSOLE: str = 'log_in_console'
LINES_LIMIT: str = 'lines_limit'
ONLY_LINE_ID: str = 'only_line_id'
ONLY_GAME_ID: str = 'only_game_id'

class Config:
    """
    Конфиг из папки config/appsettings.json считывается всегда,
    appsettings.local.json только существующие значения и если существует
    """
    __page_load_timeout: int
    __element_load_timeout: int
    __log_in_console: bool
    __lines_limit: int
    __only_line_id: str
    __only_game_id: str

    @property
    def page_load_timeout(self) -> float:
        return self.__page_load_timeout

    @property
    def element_load_timeout(self) -> float:
        return self.__element_load_timeout

    @property
    def log_in_console(self) -> bool:
        return self.__log_in_console

    @property
    def lines_limit(self) -> int:
        return self.__lines_limit

    @property
    def only_line_id(self) -> str:
        return self.__only_line_id

    @property
    def only_game_id(self) -> str:
        return self.__only_game_id

    def __init__(self):
        with open('config/appsettings.json', encoding='utf-8') as file:
            json_string = file.read()
            file.close()
            data = json.loads(json_string)
            g: dict[str, str] = data['general']
            d: dict[str, str] = data['debug']
            self.__page_load_timeout = int(g[PAGE_LOAD_TIMEOUT])
            self.__element_load_timeout = int(g[ELEMENT_LOAD_TIMEOUT])
            self.__log_in_console = bool(d[LOG_IN_CONSOLE])
            self.__lines_limit = int(d[LINES_LIMIT])
            self.__only_line_id = d[ONLY_LINE_ID]
            self.__only_game_id = d[ONLY_GAME_ID]

            # Локальный JSON. Заполняем только существующие поля
            file_local_path = Path('config/appsettings.local.json')
            if not file_local_path.exists(): return # Игнор, если файла нет
            with open(file_local_path, encoding='utf-8') as file_local:
                json_local_string = file_local.read()
                file_local.close()
                data_local = json.loads(json_local_string)
                if 'general' in data_local:
                    gl: dict[str, str] = data_local['general']
                    if PAGE_LOAD_TIMEOUT in gl: self.__page_load_timeout = int(gl[PAGE_LOAD_TIMEOUT])
                    if ELEMENT_LOAD_TIMEOUT in gl: self.__element_load_timeout = int(gl[ELEMENT_LOAD_TIMEOUT])
                if 'debug' in data_local:
                    dl: dict[str, str] = data_local['debug']
                    if LOG_IN_CONSOLE in dl: self.__log_in_console = bool(dl[LOG_IN_CONSOLE])
                    if LINES_LIMIT in dl: self.__lines_limit = int(dl[LINES_LIMIT])
                    if ONLY_LINE_ID in dl: self.__only_line_id = dl[ONLY_LINE_ID]
                    if ONLY_GAME_ID in dl: self.__only_game_id = dl[ONLY_GAME_ID]

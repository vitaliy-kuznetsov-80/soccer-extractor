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
    Конфиг из папки config/. appsettings.json считывается всегда,
    appsettings.local.json только существующие значания и если существует
    """
    page_load_timeout: int
    element_load_timeout: int
    log_in_console: bool
    lines_limit: int
    only_line_id: str
    only_game_id: str

    def __init__(self):
        with open('config/appsettings.json', encoding='utf-8') as file:
            json_string = file.read()
            file.close()
            data = json.loads(json_string)
            g: dict[str] = data['general']
            d: dict[str] = data['debug']
            self.page_load_timeout = g[PAGE_LOAD_TIMEOUT]
            self.element_load_timeout = g[ELEMENT_LOAD_TIMEOUT]
            self.log_in_console = d[LOG_IN_CONSOLE]
            self.lines_limit = d[LINES_LIMIT]
            self.only_line_id = d[ONLY_LINE_ID]
            self.only_game_id = d[ONLY_GAME_ID]

            # Локальный JSON. Заполняем только существующие поля
            file_local_path = Path('config/appsettings.local.json')
            if not file_local_path.exists(): return # Игнор, если файла нет
            with open(file_local_path, encoding='utf-8') as file_local:
                json_local_string = file_local.read()
                file_local.close()
                data_local = json.loads(json_local_string)
                if 'general' in data_local:
                    gl: dict[str] = data_local['general']
                    if PAGE_LOAD_TIMEOUT in gl: self.page_load_timeout = gl[PAGE_LOAD_TIMEOUT]
                    if ELEMENT_LOAD_TIMEOUT in gl: self.element_load_timeout = gl[ELEMENT_LOAD_TIMEOUT]
                if 'debug' in data_local:
                    dl: dict[str] = data_local['debug']
                    if LOG_IN_CONSOLE in dl: self.log_in_console = dl[LOG_IN_CONSOLE]
                    if LINES_LIMIT in dl: self.lines_limit = dl[LINES_LIMIT]
                    if ONLY_LINE_ID in dl: self.only_line_id = dl[ONLY_LINE_ID]
                    if ONLY_GAME_ID in dl: self.only_game_id = dl[ONLY_GAME_ID]

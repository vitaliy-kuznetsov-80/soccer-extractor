"""Анализ линий"""

from ..utils import Utils
from ..utils import Logger

PATH = 'champs?rev=4&ids_sp=1&ver=44&csn=ooca9s'
# 'events?rev=6&ver=44&csn=ooca9s'

class LinesAnalyzer:
    """Анализ игр линий"""
    log: Logger

    def __init__(self, log: Logger):
        self.log = log

    # --- Private

    @staticmethod
    def _get_ignore_list() -> list[str]:
        """Список фраз - исключений"""
        return Utils.get_text_list('ignore-soccer.txt')
import logging
import os
from logging import Logger as DefLogger
from pathlib import Path

from . import Utils

LOGS_FOLDER_NAME = 'logs'

class Logger:
    """Логер"""
    in_console: bool
    log: DefLogger

    def __init__(self, in_console: bool):
        self.in_console = in_console

        # Создание папки логов, если нет
        Path(LOGS_FOLDER_NAME).mkdir(parents=True, exist_ok=True)

        log_filename = self._get_log_filename()

        # Удаляем файл лога, если с таким-же именем
        if os.path.exists(log_filename): os.remove(log_filename)

        if in_console:
            # Логирование в консоль
            logging.basicConfig(
                level=logging.INFO,
                format='%(message)s',
            )
        else:
            # Логирование в файл
            logging.basicConfig(
                level=logging.INFO,
                format='%(message)s',
                encoding='utf-8',
                filename=log_filename
            )

        self.log =logging.getLogger(__name__)

    @staticmethod
    def _get_log_filename():
        filename = Utils.get_filename()
        return  os.path.join(LOGS_FOLDER_NAME, filename + '.log')

    def print(self, value: str):
        self.log.info(value)

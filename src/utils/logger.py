import logging
import os
from logging import Logger as DefLogger, FileHandler
from pathlib import Path

from . import Utils
from . import Config

LOGS_FOLDER_NAME = 'logs'

class Logger:
    """Логгер"""
    __log: DefLogger
    __conf: Config
    __file_handler: FileHandler

    def __init__(self, conf: Config, postfix: str = '') -> None:
        self.__conf = conf
        # Создание папки логов, если нет
        Path(LOGS_FOLDER_NAME).mkdir(parents=True, exist_ok=True)

        log_filename = self._get_log_filename(postfix)

        # Удаляем файл лога, если с таким-же именем
        if os.path.exists(log_filename): os.remove(log_filename)

        self.__log = logging.getLogger(__name__ + postfix)
        self.__log.setLevel(logging.INFO)

        if conf.log_in_console:
            # Логирование в консоль
            logging.basicConfig(
                level=logging.INFO,
                format='%(message)s',
            )
        else:
            self.__file_handler = logging.FileHandler(log_filename, encoding='utf-8')
            formatter = logging.Formatter('%(message)s')
            self.__file_handler.setFormatter(formatter)
            self.__log.addHandler(self.__file_handler)

    def _get_log_filename(self, postfix: str = '') -> str:
        """Генерирует имя файла лога.
        Args:
            postfix: Дополнительный постфикс для имени файла.
        Returns:
            Полный путь к файлу лога.
        """
        filename = Utils.get_filename(self.__conf.day_offset)
        return  os.path.join(LOGS_FOLDER_NAME, filename + '_' + postfix + '.log')

    def print(self, value: str, in_console: bool = False):
        self.__log.info(value)

        if self.__conf.log_in_console:
            return
        if in_console:
            print(value)

    def close_file(self) -> None:
        """Закрывает файл лога"""
        if  self.__conf.log_in_console:
            return

        self.__file_handler.flush()
        self.__log.removeHandler(self.__file_handler)
        self.__file_handler.close()
        logging.shutdown()
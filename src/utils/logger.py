import logging
import os
from logging import Logger as DefLogger

import src.utils.utils as u

class Logger:
    """Логер"""
    in_console: bool
    log: DefLogger

    def __init__(self, in_console: bool):
        self.in_console = in_console
        filename = u.get_filename() # Имя фалйла скрина и Excel
        log_filename = 'results/log' + filename + '.log'

        current_directory = os.getcwd()
        print(current_directory)

        if os.path.exists(log_filename): os.remove(log_filename)

        if in_console:
            logging.basicConfig(
                level=logging.INFO,
                format='%(message)s',
            )
        else:
            logging.basicConfig(
                level=logging.INFO,
                format='%(message)s',
                encoding='utf-8',
                filename=log_filename
            )

        self.log =logging.getLogger(__name__)

    def print(self, value: str):
        self.log.info(value)

"""Утилитные функции"""

import re
from datetime import datetime

from selenium.webdriver.remote.webelement import WebElement

class Utils:

    @staticmethod
    def get_date_stamp() -> str:
        current_date_time = datetime.now()
        return Utils.get_date_stamp_by_date(current_date_time)

    @staticmethod
    def get_date_stamp_by_date(date_time: datetime) -> str:
        return date_time.strftime('%d.%m.%Y')

    @staticmethod
    def get_filename() -> str:
        """Имя сохраняемых файлов"""
        current_date_time = datetime.now()
        time_stamp = Utils.get_date_stamp() + '_' + current_date_time.strftime('%H.%M.%S')
        return time_stamp

    @staticmethod
    def get_id(tag: WebElement, end_str: str = '') -> str:
        """Последний Id в тэге - a"""
        a_tag = tag.get_attribute('href')
        if a_tag:
            return re.search('/soccer/(.*)' + end_str, a_tag).group(1)[:-1].strip()
        return ''

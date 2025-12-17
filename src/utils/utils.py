"""Утилитные функции"""

import re
from datetime import datetime, timedelta
import time
from enum import Enum

from selenium.webdriver.remote.webelement import WebElement

BASE_URL = 'https://betcity.ru/ru/'
BASE_API_URL = 'https://ad.betcity.ru/d/off/'

class Region(Enum):
    EUROPE = "europe"
    AMERICA = "america"
    ASIA = "asia"

class Utils:

    @staticmethod
    def get_date_stamp() -> str:
        """Возвращает текущую дату в формате dd.mm.yyyy"""
        current_date_time = datetime.now()
        return Utils.get_date_stamp_by_date(current_date_time)

    @staticmethod
    def get_date_stamp_by_date(date_time: datetime) -> str:
        """Преобразует объект datetime в строку формата dd.mm.yyyy"""
        return date_time.strftime('%d.%m.%Y')

    @staticmethod
    def get_filename() -> str:
        """Генерирует имя файла на основе текущей даты и времени в формате dd.mm.yyyy_HH.MM.SS"""
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

    @staticmethod
    def get_yesterday() -> datetime:
        """"Вчерашняя дата без времени"""
        return datetime.today() - timedelta(days=1)

    @staticmethod
    def get_url_date(date: datetime) -> str:
        """Преобразует объект datetime в строку формата yyyy-mm-dd"""
        return str(date.year) + '-' + str(date.month).zfill(2) + '-' + str(date.day).zfill(2)

    @staticmethod
    def get_text_list(filename: str) -> list[str]:
        """Читает файл и возвращает список строк (по одной строке на элемент списка)"""
        with open('assets/' + filename, encoding='utf-8') as file:
            result = file.read().splitlines()
            file.close()
            return result

    @staticmethod
    def get_local_timezone_offset() -> float:
        """Возвращает смещение локальной временной зоны относительно UTC в часах"""
        # time.timezone is the offset in seconds west of UTC. For a positive offset (east of UTC), negate the value
        offset_seconds = -time.timezone
        # Convert to hours
        offset_hours = offset_seconds / 3600
        return offset_hours
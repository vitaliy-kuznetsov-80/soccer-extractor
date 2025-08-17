"""Утилитные функции"""

import re
from datetime import datetime

from selenium.webdriver.remote.webelement import WebElement

def get_filename() -> str:
    """Имя сохраняемых файлов"""
    current_date_time = datetime.now()
    time_stamp = current_date_time.strftime('%m.%d.%y %H.%M.%S')
    return '_' + time_stamp

def get_id(tag: WebElement) -> str:
    """Последний Id в тэге - a"""
    a_tag = tag.get_attribute('href')
    return re.search('/ru/line/soccer/(.*)ts=24', a_tag).group(1)[:-1].strip()

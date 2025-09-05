"""Основная программа"""
from dataclasses import dataclass
from datetime import datetime, timedelta
import sys
import os
import time
import traceback

from selenium.common import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

from src.page import Page
from src.utils import Config, Utils
from src.utils import Logger
from src.utils import ExcelManager
from src.utils.excel_manager import RESULTS_FOLDER_NAME


@dataclass
class ResultDto:
    id:  str
    time: str
    team_1: str
    team_2: str
    first_time: str
    total: str

    def __init__(self) -> None:
        self.id = ''
        self.time = ''
        self.team_1 = ''
        self.team_2 = ''
        self.first_time = ''
        self.total = ''

# Url списка линий
URL: str = 'https://betcity.ru/ru/results/soccer'

# Конфиг
conf = Config()

# Настройка логера
log = Logger(conf.log_in_console)

log.print('Старт')
start_time = datetime.now()

def get_yesterday() -> datetime:
    """"Вчерашняя дата без времени"""
    return datetime.today() - timedelta(days=1)

def get_url_date(_date: datetime) -> str:
    return str(_date.year) + '-' + str(_date.month).zfill(2) + '-' + str(_date.day).zfill(2)

try:
    yesterday = get_yesterday()

    # Файл коэффициентов прошлого дня (берем первый со вчерашней датой)
    date_stamp = Utils.get_date_stamp_by_date(yesterday)
    files = os.listdir(RESULTS_FOLDER_NAME)

    filename = ''
    for file in files:
        if file.startswith(date_stamp): filename = file

    if not filename:
        log.print('Вчерашний матч не найден')
        raise SystemExit

    em = ExcelManager()
    em.load_excel(filename)

    # Url вчерашнего дня
    url = URL + '?date=' + get_url_date(yesterday)

    # Получение страницы
    page = Page(url, conf, log)

    # Список Id на проверку
    target_ids: list[str] = em.get_ids()

    index = 2
    for target_id in target_ids:
        target_a: WebElement
        try:
            target_a = page.conteiner.find_element(By.XPATH, "//a[contains(@href, '" + target_id + "')]")
        except NoSuchElementException:
            em.write_empty_cell(index, 37)
            em.write_empty_cell(index, 38)
            em.write(index, 39, 'Не найден')
            log.print(target_id + ' - не найден: ')
            index = index + 1
            continue
        # Контейнер строки (назад на 2 родителя)
        row = target_a.find_element(By.XPATH, '..//..')
        result = ResultDto()
        result.id = Utils.get_id(target_a).strip()
        result.time = row.find_element(By.CLASS_NAME, 'results-event__time').text.strip()
        teams = target_a.text.split(' — ')
        result.team_1 = teams[0].strip()
        result.team_2 = teams[1].strip()
        score = row.find_element(By.CLASS_NAME, 'results-event__score').text.strip()
        # Есть результаты
        if ':' in score:
            sp = score.split(' (')
            # Оба счёта
            if len(sp) > 1:
                result.total = sp[0].strip()
                result.first_time = sp[1].strip()[:-1]
            else:
                # Только финальный
                result.total = score.strip()

        if not result.total and not result.first_time:
            em.write(index, 39, 'Отмена')

        em.write(index, 37, result.first_time)
        em.write(index, 38, result.total)

        log.print(target_id + ' | ' + result.time + ' | ' +
                  result.team_1 + ' | ' + result.team_2 + ' | ' +
                  result.first_time + ' | ' + result.total)

        index = index + 1

    em.save()

    time.sleep(1)
    page.close()

    end_time = datetime.now()
    log.print('Время работы: ' + str(end_time - start_time))
    log.print('Финиш')
except Exception as e: # pylint: disable=broad-except
    log.print('\nERROR')

    _, ex_value, ex_traceback = sys.exc_info()
    trace_back = traceback.extract_tb(ex_traceback)

    log.print('Message: ' + str(ex_value))

    for trace in trace_back:
        log.print('File: {}, Line: {:d}, Func.Name: {}, Message: {}'.format(trace[0], trace[1], trace[0], trace[3]))

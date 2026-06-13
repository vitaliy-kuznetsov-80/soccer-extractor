from schedule import run_pending, every
from datetime import datetime
import time
import sched

from main import Main
from main_results import Results
from src.dto.region_enum import RegionEnum
from src.utils import Config

scheduler = sched.scheduler(time.time, time.sleep)

print(f"Старт планировщика в: {datetime.now()}")

def run_region(region: RegionEnum, retry_count=0):
    main = Main(region)
    try:
        main.run()
    except Exception:
        # Повторный запуск на основе retry политики

        retry_count += 1

        if retry_count > conf.retry_count:
            print('Ошибка парсинга в ' + str(region).capitalize() + '. Конец')
            return

        print('Ошибка парсинга в ' + str(region).capitalize() + '. Повтор № ' + str(retry_count))

        scheduler.enter(conf.scheduler_retry_period, 1, run_region, argument=(region, retry_count)) # conf.scheduler_retry_period
        scheduler.run()

def run_europe():
    run_region(RegionEnum.EUROPE)

def run_america():
    run_region(RegionEnum.AMERICA)

def run_asia():
    run_region(RegionEnum.ASIA)

def run_results():
    results = Results()
    results.run()

conf = Config()

print('Расписание стартов:')
print(f'  {conf.europe_start_time} Европа')
print(f'  {conf.america_start_time} Северная Америка')
print(f'  {conf.asia_start_time} Азия')
print(f'  {conf.results_start_time} Результаты')

every().day.at(conf.europe_start_time).do(run_europe)
every().day.at(conf.america_start_time).do(run_america)
every().day.at(conf.asia_start_time).do(run_asia)
every().day.at(conf.results_start_time).do(run_results)

while True:
    run_pending()
    time.sleep(1)
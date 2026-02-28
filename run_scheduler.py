from schedule import run_pending, every
from datetime import datetime
import time

from main import Main
from main_results import Results
from src.dto.region_enum import RegionEnum
from src.utils import Config

print(f"Старт планировщика в: {datetime.now()}")

def run_europe():
    main = Main(RegionEnum.EUROPE)
    main.run()

def run_america():
    main = Main(RegionEnum.AMERICA)
    main.run()

def run_asia():
    main = Main(RegionEnum.ASIA)
    main.run()

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
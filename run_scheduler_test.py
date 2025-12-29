from schedule import run_pending, every
from datetime import datetime, timedelta
import time

from main import Main
from main_results import Results
from src.utils import Region

print(f"Старт теста планировщика в: {datetime.now()}")

def datetime_to_time(dt: datetime):
    return str(dt.hour).zfill(2) + ':' + str(dt.minute).zfill(2) + ':' + str(dt.second).zfill(2)

now = datetime.now()
europe_start_datetime = now + timedelta(minutes=2)
america_start_datetime = now + timedelta(minutes=6)
asia_start_datetime = now + timedelta(minutes=8)
results_start_datetime = now + timedelta(seconds=4)
europe_start_time = datetime_to_time(europe_start_datetime)
america_start_time = datetime_to_time(america_start_datetime)
asia_start_time = datetime_to_time(asia_start_datetime)
results_start_time = datetime_to_time(results_start_datetime)

def run_europe():
    main = Main(Region.EUROPE)
    main.run()

def run_america():
    main = Main(Region.AMERICA)
    main.run()

def run_asia():
    main = Main(Region.ASIA)
    main.run()

def run_results():
    results = Results()
    results.run()

every().day.at(europe_start_time).do(run_europe)
every().day.at(america_start_time).do(run_america)
every().day.at(asia_start_time).do(run_asia)
every().day.at(results_start_time).do(run_results)

while True:
    run_pending()
    time.sleep(1)
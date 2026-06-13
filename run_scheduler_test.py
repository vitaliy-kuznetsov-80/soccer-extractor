from datetime import datetime
import time

from main import Main
from main_results import Results
from src.dto.region_enum import RegionEnum

print(f"Прогон: {datetime.now()}")

results = Results()
results.run()
time.sleep(5)

main_europe = Main(RegionEnum.EUROPE)
main_europe.run()
time.sleep(5)

main_america = Main(RegionEnum.AMERICA)
main_america.run()
time.sleep(5)

main_asia = Main(RegionEnum.ASIA)
main_asia.run()
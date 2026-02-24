from datetime import datetime
import time

from main import Main
from main_results import Results
from src import Region

print(f"Прогон: {datetime.now()}")

results = Results()
results.run()
time.sleep(5)

main_europe = Main(Region.EUROPE)
main_europe.run()
time.sleep(5)

main_america = Main(Region.AMERICA)
main_america.run()
time.sleep(5)

main_asia = Main(Region.ASIA)
main_asia.run()
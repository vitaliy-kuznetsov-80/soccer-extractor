from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver import Chrome

import utils as u
import params as p

# Пометка строк для получения игр
def mark_lines(driver: Chrome):
    # Таблица парсинга. Берём только левую (СОБЫТИЯ)
    tables = driver.find_elements(By.CLASS_NAME, 'champs__sport')[0]

    # Список строк линий
    rows = tables.find_elements(By.CLASS_NAME, 'champs__champ')
    print('Найдено линий: ' + str(len(rows)))

    # Фильтрация строк
    print('Фильтрованные линии: ')
    # Читаем слова-исключения из файла
    # todo Из файла
    filter_array = ['Статистика', 'до 21 года', 'Серия D', 'Серия C', 'Примавера', 'Израиль', 'Ирак']
    for row in rows:
        # Ссылка на линию с названием
        a = row.find_element(By.CLASS_NAME, 'champs__champ-name')
        line_text = a.text

        # Игнор
        is_ignore = False
        for item in filter_array:
            if line_text.find(item) > -1:
                is_ignore = True
                break
        if is_ignore:
            print('- ' + line_text)
            continue

        print(line_text)

        # Пометка линии через щелчок по checkbox
        checkbox = row.find_element(By.CLASS_NAME, 'checkbox__mark')
        u.click(driver, checkbox)

# Загрузка игр для выбранных линий
def load_games(driver: Chrome):
    # Жмём "Показать" для отображения игр
    find_button = driver.find_element(By.CLASS_NAME, 'line__controls-button')
    u.click(driver, find_button)

    # Ждём загрузки игр
    WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CLASS_NAME, "line-event")))

# Парсинг игр
def parce_games(driver: Chrome, filename: str):
    # Строки игр
    rows = driver.find_elements(By.CLASS_NAME, 'line-event')
    prev_play_button = None  # Запоминаем предыдущую кнопку для закрытия, перед открытием нового
    for row in rows:
        # Закрывем предыдущй
        if prev_play_button is not None:
            u.click(driver, prev_play_button)
            driver.implicitly_wait(1)

        # Кнопка раскрытия игры
        play_button = row.find_element(By.CLASS_NAME, 'line-event__dops-toggle')
        if play_button.tag_name != 'button': continue  # Игнор не кнопок

        # Клик по раскрывашке (правая колонка)
        u.click(driver, play_button)
        # Ожидаем прогрузки по названию таблицы нижней части коэффициентов (должна быть всегда)
        waiting_path = "//span[starts-with(., 'Цифра в итоговом счете')]"
        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.XPATH, waiting_path)))

        # Парсинг игры
        header_line = p.get_header_params(row)

        # Получение и запись коэффициентов
        p.save_to_excel(driver, header_line, filename)

        prev_play_button = play_button  # Запоминаем кнопку раскрытия
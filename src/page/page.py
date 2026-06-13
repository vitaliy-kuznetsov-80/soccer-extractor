import time

from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from src.utils import Logger
from src.utils import Config
from src.utils.utils import BASE_URL

def click_in_list_by_text(elements: list[WebElement], text: str) -> None:
    result = False
    for element in elements:
        if text.lower() in element.text.lower():
            result = True
            element.click()
            break
    if not result:
        raise TimeoutException('Не найден элемент списка с текстом: ' + text)

class Page:
    """Страница"""
    url: str
    log: Logger
    drv: WebDriver
    container: WebElement
    conf: Config

    def __init__(self, url: str, conf: Config, log: Logger):
        self.url = BASE_URL + url
        self.log = log
        self.conf = conf

        self.log.print('Парсинг: ' + url)

        result: bool = self._get_page() # Получить DOM дерево
        if not result: raise TimeoutException('Не удалось получить страницу')

    def init(self, ready_content_class: str) -> None:
        self._close_dialogs()  # Закрытие диалогов
        self._set_region_by_name('москва') # Выбор часового пояса МСК
        self._get_container()  # Получение контейнера для игр

        # Ожидание прогрузки контента
        time.sleep(1)
        self.wait(By.CLASS_NAME, ready_content_class)
        self.log.print('Контент загружен')

    def click(self, element: WebElement) -> None:
        """Клик по элементу"""
        self.drv.execute_script("arguments[0].click();", element)

    def wait(self, find_by: str, find_element: str, timeout:  int | None = None) -> None:
        if timeout is None: timeout = self.conf.element_load_timeout

        """Поиск элемента"""
        located = ec.presence_of_element_located((find_by, find_element))
        try:
            WebDriverWait(self.drv, timeout).until(located)
        except TimeoutException:
            self.log.print('Не удалось найти: ' + find_element)
            raise TimeoutException('Не удалось найти: ' + find_element)

    def wait_disappear(self, find_by: str, find_element: str, timeout:  int | None = None) -> None:
        if timeout is None: timeout = self.conf.element_load_timeout

        """Поиск элемента"""
        located = ec.invisibility_of_element_located((find_by, find_element))
        try:
            WebDriverWait(self.drv, timeout).until(located)
        except TimeoutException:
            self.log.print('Элемент не скрылся: ' + find_element)
            raise TimeoutException('Элемент не скрылся: ' + find_element)

    def get_screenshot(self, filename: str) -> None:
        """Снятие скриншота"""
        self.drv.get_screenshot_as_file(filename)

    def close(self):
        """Закрытие страницы"""
        for handle in self.drv.window_handles:
            self.drv.switch_to.window(handle)
            self.drv.close()
        self.drv.quit()

    def find_element_by_class(self, class_name: str, parent: WebElement = None) -> WebElement:
        """Поиск элемента по имени класса с ожиданием"""
        self.wait(By.CLASS_NAME, class_name)
        if parent is None: parent = self.drv

        return parent.find_element(By.CLASS_NAME, class_name)

    def find_elements_by_class(self, class_name: str, parent: WebElement = None) -> list[WebElement]:
        """Поиск элементов по имени класса с ожиданием"""
        self.wait(By.CLASS_NAME, class_name)
        if parent is None: parent = self.drv

        return parent.find_elements(By.CLASS_NAME, class_name)

    def find_element_and_click_by_class(self, class_name: str, text: str, parent: WebElement = None) -> None:
        """Поиск элементов по имени класса `class_name` с ожиданием и клик по одному из найденных, по контенту `text`"""
        elements = self.find_elements_by_class(class_name, parent)
        click_in_list_by_text(elements, text)
        time.sleep(1)

    # --- Private

    def _set_region_by_name(self, region_name: str) -> None:
        """Выбор часового пояса"""

        # 1. Щелчок по кнопке настроек
        self.find_element_by_class('sub-header__icon-settings').click()

        # 2. Ждём загрузки окна настроек
        settings_dialog_body = self.find_element_by_class('pa-settings__section')

        # 3. Щелчок по кнопке выбора региона
        self.find_element_and_click_by_class('pa-list-item__content', 'часовой пояс', settings_dialog_body)

        # 4. Открываем диалог регионов
        region_list = self.find_element_by_class('pa-selection-list')

        # 5. Выбираем регион
        self.find_element_and_click_by_class('pa-list-item', region_name, region_list)

        # 5. Жмём кнопку Сохранить
        self.find_element_and_click_by_class('pa-settings__button', 'сохранить')

        # 6. Ждём загрузки контента
        self._wait_base_content()

        self.log.print('Выбран часовой пояс: ' + region_name)

    def _get_container(self) -> None:
        """Контейнер, где находятся все игры (div class="container") (для сокращения времени поиска)"""
        container = self.find_element_by_class('container')
        self.container = container
        self.log.print('Контейнер получен')

    def _close_dialogs(self) -> None:
        """Прячем окно уведомления и кукисов"""
        # Кнопка куки
        try:
            cookie_buttons = self.drv.find_elements(By.CLASS_NAME, 'cookie-modal__button')
            if len(cookie_buttons) > 0:
                cookie_buttons[0].click()
        except NoSuchElementException:
            self.log.print('Кнопка куки не найдена')

        # Кнопка уведомления
        try:
            confirm_buttons = self.drv.find_elements(By.CLASS_NAME, 'push-confirm__button')
            if len(confirm_buttons) > 0:
                confirm_buttons[0].click()
        except NoSuchElementException:
            self.log.print('Кнопка уведомления не найдена')

        time.sleep(0.5)
        self.log.print('Диалоги закрыты')

    def _wait_base_content(self) -> None:
        """Загрузка основного контента"""
        time.sleep(1)
        self.wait(By.CLASS_NAME, 'container')

    def _get_page(self) -> bool:
        """Получить DOM дерево страницы"""
        options = self.__config_browser()

        # Получение драйвера Chrome 3 раза с периодом 1 сек
        for attempt in range(3):
            try:
                self.drv = webdriver.Chrome(options)
            except Exception as e:
                self.log.print('Ошибка получения драйвера. Таймаут')
                if attempt < 2:
                    time.sleep(1)
                else:
                    self.log.print("Принудительная остановка: " + str(e))
                    return False

        self.drv.maximize_window() # Полноэкранный режим

        self.drv.set_page_load_timeout(self.conf.page_load_timeout) # Таймаут принудительной остановки загрузки

        # Получение страницы с политикой retry
        for attempt in range(self.conf.retry_count):
            try:
                self.log.print('Попытка получения страницы: ' + str(attempt + 1))
                self.drv.get(self.url) # Запрос получения страниц
                self.log.print('Страница получена')
                self._wait_base_content()
                self.log.print('Страница загружена')
                return True
            except TimeoutException:
                self.log.print('Таймаут')
                if attempt < self.conf.retry_count - 1:
                    time.sleep(self.conf.retry_count * 1)
                else:
                    self.log.print("Принудительная остановка")
                    self.drv.execute_script("window.stop();")
                    self.drv.quit()
                    return False
        return False

    @staticmethod
    def __config_browser() -> Options:
        """Конфигурация браузера"""
        options = webdriver.ChromeOptions()
        # Опции оптимизации загрузки
        options.add_argument('-no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument("disable-infobars")
        options.add_argument('-disable-dev-shm-usage')
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")
        options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_experimental_option('excludeSwitches', ['disable-popup-blocking'])
        options.add_experimental_option("prefs", {
            "profile.managed_default_content_settings.images": 2,
            'media_stream': 2,
            "profile.default_content_setting_values.notifications": 2  # 2 = Block
        })
        return options
import time

from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from .utils import Logger
from .utils import Config
from .utils.utils import BASE_URL

class Page:
    """Страница"""
    url: str
    log: Logger
    drv: WebDriver
    container: WebElement
    conf: Config

    def __init__(self, url: str, conf: Config, log: Logger, redy_content_class: str):
        self.url = BASE_URL + url
        self.log = log
        self.conf = conf

        self.log.print('Парсинг: ' + url)

        result: bool = self._get_page() # Получить DOM дерево
        if not result: raise TimeoutException('Не удалось получить страницу')

        self._close_dialogs()  # Закрытие диалогов
        self._set_msk()  # Выбор часового пояса МСК
        self._get_container()  # Получение контенера для игр

        # Ожидание прогрузки контента
        time.sleep(1)
        self.wait(By.CLASS_NAME, redy_content_class)
        self.log.print('Контент загружен')

    def click(self, element: WebElement) -> None:
        """Клик по элементу"""
        self.drv.execute_script("arguments[0].click();", element)

    def wait(self, find_by: str, find_element: str, timeout:  int | None = None) -> None:
        if timeout is None: timeout = self.conf.element_load_timeout

        """Поиск элемента"""
        located = ec.presence_of_element_located((find_by, find_element))
        WebDriverWait(self.drv, timeout).until(located)

    def close(self):
        """Закрытие страницы"""
        self.drv.close()

    # --- Private

    def _get_container(self) -> None:
        """Контенер, где находятся все игры (div class="container") (для сокращения времени поиска)"""
        conteiner = self.drv.find_element(By.CLASS_NAME, 'container')
        self.container = conteiner
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

        # Кнопка уведомленния
        try:
            confirm_buttons = self.drv.find_elements(By.CLASS_NAME, 'push-confirm__button')
            if len(confirm_buttons) > 0:
                confirm_buttons[0].click()
        except NoSuchElementException:
            self.log.print('Кнопка уведомленния не найдена')

        time.sleep(0.5)
        self.log.print('Диалоги закрыты')

    def _set_msk(self) -> None:
        """Выбор часового пояса МСК"""
        # Кнопка настроек
        button_settings = self.drv.find_element(By.CLASS_NAME, 'sub-header__icon-settings')
        self.click(button_settings)

        # Ждём загрузки окна
        self.wait(By.CLASS_NAME, 'settings__body')

        # Выбираем Москву
        body = self.drv.find_element(By.CLASS_NAME, 'settings__body')
        path = "//span[@class='select-dropdown__item' and contains(text(),'Москва')]"
        drop_down_item = body.find_element(By.XPATH, path)
        self.click(drop_down_item)
        time.sleep(1)

        # Сохраняем
        button_save = self.drv.find_element(By.CLASS_NAME, 'settings-footer-button_save')
        self.click(button_save)

        self.wait_base_content()

        self.log.print('Выбран часовой пояс МСК')

    def wait_base_content(self) -> None:
        """Загрузка основного контента"""
        time.sleep(1)
        self.wait(By.CLASS_NAME, 'container')

    def _get_page(self) -> bool:
        """Получить DOM дерево страницы"""
        options = self.__config_browser()
        self.drv = webdriver.Chrome(options)
        self.drv.maximize_window() # Полноэкранный режим

        self.drv.set_page_load_timeout(self.conf.page_load_timeout) # Тамаут принудительной оставновки загрузки

        for attempt in range(self.conf.retry_count):
            try:
                self.log.print('Попытка получения страницы: ' + str(attempt + 1))
                self.drv.get(self.url) # Запрос получения страниц
                self.log.print('Страница получена')
                self.wait_base_content()
                self.log.print('Страница загружена')
                return True
            except TimeoutException:
                self.log.print('Таймаут')
                if attempt < self.conf.retry_count - 1:
                    time.sleep(self.conf.retry_count * 1)
                else:
                    print("Принудительная остановка")
                    self.drv.execute_script("window.stop();")
                    self.drv.quit()
                    return False
        return False

    @staticmethod
    def __config_browser() -> Options:
        options = webdriver.ChromeOptions()
        # Опции оптимизации загрузки
        options.add_argument('-no-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument("disable-infobars")
        options.add_argument('-disable-dev-shm-usage')
        options.add_argument("--disable-extensions")
        options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_experimental_option('excludeSwitches', ['disable-popup-blocking'])
        options.add_experimental_option("prefs", {
            "profile.managed_default_content_settings.images": 2,
            'media_stream': 2,
        })
        return options
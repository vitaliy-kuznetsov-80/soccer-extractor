# soccer-extractor
## Установка

Установить зависимости

``
pip3 install -r requirements.txt
``

## Запуск
``
py main.py
``

## Настройки файла `appsettings.json`
### Общие константы
```
"general": {
  "page_load_timeout": Таймаут принудительной остановки загрузки базовой страницы
  "element_load_timeout": Таймаут 
}
```

### Отладочные константы
```
"debug": {
  "LOG_IN_CONSOLE": true - Вывод логов в консоле, false - в файл
  "LINES_LIMIT": Лимит линий. 0 - без лимит
  "GAMES_LIMIT": Лимит обработки игр. 0 - без лимит
  "ONLY_ID": Загрузка одной игры по Id (строка). Пустая строка - отключено
}
``` 

Если есть файл `appsettings.local.json`, он перезатирает константы из `appsettings.json`. Если какой-то константы в `appsettings.local.json` нет, она берётся из `appsettings.json`.

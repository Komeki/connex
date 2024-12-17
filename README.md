# connex

Для запуска aiogram бота на своем ПК сначала нужна сама библиотека aiogram

`pip install aiogram`

Запуск файла connex.py
Можно перезапускать бота вручную:
- Запуск -> connex.py 
- Выключить -> Ctrl + C

Я поставил библиотеку watchdog, что позволяет не перезапускать бота.
Можно сохранять код Ctrl + S, бот будет сразу же обновлён.

Библиотека:

`pip install watchdog`

Запуск программы:

`watchmedo auto-restart --patterns="*.py" --recursive -- python connex.py`

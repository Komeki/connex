# connex

Запуск файла connex.py

Для запуска aiogram бота на своем ПК сначала нужна сама библиотека aiogram

`pip install aiogram`

Можно перезапускать бота вручную, но я поставил библиотеку watchdog, что позволяет (не выключать/включать) заново бота.
Можно сразу сохранять код Ctrl + S, бот будет сразу же обновлён.

Библиотека:

`pip install watchdog`

Запуск программы:

`watchmedo auto-restart --patterns="*.py" --recursive -- python connex.py`

# Home accountant

Простая система учета расходов для экономии денежных средств. 

## Струкрута проекта
```
.
├── README.md            - Этот файл
├── db.db                - База данных
├── install.sh           - Установочный скрипт для linux
├── main.py              - Основной файл
└── requirements.txt     - Файл со списком зависимостей
```

## Запуск и установка

Убедитесь, что у вас установлен [Python3](https://python.org)

Установка зависимостей:
```
pip3 install -r requirements.txt # Не требуется при установки с помощью install.sh
```
Запуск:

Windows, macOS:
```
python3 main.py
```

Linux:

```
sh install.sh # Установка программы в систему
```

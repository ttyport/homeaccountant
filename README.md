#Home accountant
Простая система учета расходов для экономии денежных средств. 

##Струкрута проекта
```
.
├── db.db                - База данных
├── install.sh           - Установочный скрипт для linux
├── main.py              - Основной файл
├── requirements.txt     - Файл со списком зависимостей
├── README.md            - Этот файл
└── uninstall.sh         - Скрипт удаления с linux
```

##Запуск и установка

Убедитесь, что у вас установлен [Python3](https://python.org)

Установка зависимостей:
```
pip3 install -r requirements.txt
```
Запуск:

Windows, macOS:
```
python3 main.py
```

Linux:

```
sudo ./install.sh #Установка программы в систему
```

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.Qt import Qt
from PyQt5.QtChart import *
from hashlib import sha256
import sqlite3
from screeninfo import get_monitors
from datetime import date


near = [
    'qwe', 'wer', 'ert', 'rty', 'tyu', 'yui', 'uio', 'iop',
    'asd', 'sdf', 'dfg', 'fgh', 'ghj', 'hjk', 'jkl',
    'zxc', 'xcv', 'cvb', 'vbn', 'bnm',
    'йцу', 'цук', 'уке', 'кен', 'енг', 'нгш', 'гшщ', 'шщз', 'щзх', 'зхъ',
    'фыв', 'ыва', 'вап', 'апр', 'про', 'рол', 'олд', 'лдж', 'джэ',
    'ячс', 'чсм', 'сми', 'мит', 'ить', 'тьб', 'ьбю', 'жэё'
]  # Список рядом стоящих сочетаний букв


class LoginFirstTime(QDialog):  # Диалог создания учетной записи
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):  # Инициализация GUI
        self.frame = QFrame()
        self.frame.setStyleSheet(framestyle)
        self.setStyleSheet(appstyle)
        self.setGeometry(300, 300, 155, 125)
        self.setWindowTitle('Login')
        self.login = QLineEdit(self)
        self.login.setPlaceholderText("Login")
        self.login.move(15, 15)

        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Password")
        self.password.move(15, 50)

        self.ok = QPushButton("Ok", self)
        self.ok.move(35, 85)
        self.layout = QGridLayout()
        self.layout.addWidget(self.login)
        self.layout.addWidget(self.password)
        self.layout.addWidget(self.ok)
        self.setLayout(self.layout)
        self.ok.clicked.connect(self.write)
        self.show()

    def write(self):  # Запись логина и пароля в базу данных
        password = self.password.text()
        if len(password) > 7:
            if password.lower() != password and password.upper() != password:
                if any(map(str.isdigit, password)) and any(map(str.isalpha, password)):
                    if not any(char in password.lower() for char in near):
                        message = None
                    else:
                        message = "Too close symbols"
                else:
                    message = "Use at least 1 letter and 1 letter"
            else:
                message = "Use lowercase und uppercase letters"
        else:
            message = "Use at least 8 characters"
        if message:
            msg = QMessageBox()
            msg.setStyleSheet(appstyle)
            msg.setIcon(QMessageBox.Critical)
            msg.setText(message)
            msg.setWindowTitle("Weak password")
            msg.setStandardButtons(QMessageBox.Close)
            msg.exec_()
        else:
            cursor = db.cursor()
            string_to_hash = self.password.text()
            hash = sha256(str(string_to_hash).encode('utf-8'))
            query = """
            INSERT INTO login (login, password) VALUES (?, ?)
            """

            cursor.execute(query, (self.login.text(), str(hash.hexdigest())), )
            db.commit()

            self.new_window = Main()
            self.new_window.show()
            self.hide()


class Login(QDialog):  # Диалог входа в программу
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):  # Инициализация GUI
        self.frame = QFrame()
        self.frame.setStyleSheet(framestyle)
        self.setStyleSheet(appstyle)
        self.setGeometry(300, 300, 155, 125)
        self.setWindowTitle('Login')
        self.login = QLineEdit(self)
        self.login.setPlaceholderText("Login")
        self.login.move(15, 15)

        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Password")
        self.password.move(15, 50)

        self.ok = QPushButton("Ok", self)
        self.ok.move(35, 85)
        self.layout = QGridLayout()
        self.layout.addWidget(self.login)
        self.layout.addWidget(self.password)
        self.layout.addWidget(self.ok)
        self.setLayout(self.layout)
        self.ok.clicked.connect(self.launch)
        self.show()

    def launch(self):  # Запуск основного окна
        cursor = db.cursor()
        result = cursor.execute("""select * from login""").fetchall()
        string_to_hash = self.password.text()
        hash = sha256(str(string_to_hash).encode('utf-8'))
        if str(hash.hexdigest()) == result[0][-1] and self.login.text() == result[0][0]:

            self.new_window = Main()
            self.new_window.show()
            self.hide()
        else:
            msg = QMessageBox()
            msg.setStyleSheet(appstyle)
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Incorrect login or password")
            msg.setWindowTitle("Password error")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()


class Main(QMainWindow):  # Основное окно

    def __init__(self):  # Инициализация всех виджетов
        super().__init__()
        self.initUI()
        self.init_table()
        self.init_buttons()
        self.init_type()
        self.init_incomes()
        self.init_income_buttons()
        self.init_income_types()
        self.init_money()
        self.refresh_graph()
        self.init_spent()

    def initUI(self):  # Инициализация GUI
        self.frame = QFrame()
        self.frame.setStyleSheet(framestyle)
        self.setStyleSheet(appstyle)
        # Настройка меню
        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.quit)

        saveAction = QAction('&Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save results')
        saveAction.triggered.connect(self.save)

        addType = QAction('&Add type', self)
        addType.setShortcut('Ctrl+T')
        addType.setStatusTip('New income type')
        addType.triggered.connect(self.addsubtypedialog)

        delSubtype = QAction('&Del subtype', self)
        delSubtype.setShortcut('Ctrl+D')
        delSubtype.setStatusTip('Delete subtype')
        delSubtype.triggered.connect(self.deletesubtypedialog)

        delType = QAction('&Del type', self)
        delType.setShortcut('Ctrl+F')
        delType.setStatusTip('Delete type')
        delType.triggered.connect(self.deletetypedialog)

        delIncome = QAction('&Del income type', self)
        delIncome.setShortcut('Ctrl+G')
        delIncome.setStatusTip('Delete type')
        delIncome.triggered.connect(self.delete_income_type_dialog)

        addIncome = QAction('&Add income type', self)
        addIncome.setShortcut('Ctrl+H')
        addIncome.setStatusTip('New income type')
        addIncome.triggered.connect(self.add_type_income_dialog)

        export = QAction('&Export data', self)
        export.setShortcut('Ctrl+E')
        export.setStatusTip('Export data to csv file')
        export.triggered.connect(self.export)

        import_file = QAction('&Import data', self)
        import_file.setShortcut('Ctrl+I')
        import_file.setStatusTip('Import data from csv file')
        import_file.triggered.connect(self.import_file)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(addType)
        fileMenu.addAction(delSubtype)
        fileMenu.addAction(delType)
        fileMenu.addAction(delIncome)
        fileMenu.addAction(addIncome)
        fileMenu.addAction(export)
        fileMenu.addAction(import_file)

        self.x = get_monitors()[0].height
        self.y = get_monitors()[0].width
        self.setGeometry(0, 0, self.y, self.x)
        self.setWindowTitle('Home Accountant')

        self.saved = True
        self.mainwidget = QWidget(self)
        self.setCentralWidget(self.mainwidget)

        self.tabWidget = QTabWidget(self.mainwidget)  # Виджет вкладок
        self.tabWidget.setGeometry(0, 0, self.y, self.x)

        self.tab = QWidget()
        self.tabWidget.addTab(self.tab, "Расходы")

        self.tablayout = QGridLayout()
        self.tablayout.addWidget(self.tabWidget)
        self.mainwidget.setLayout(self.tablayout)

        self.tab2 = QWidget()
        self.tabWidget.addTab(self.tab2, "Доходы")

        self.money_table = QTableWidget(self.tab2)
        self.income_buttons = QTableWidget(self.tab2)

        self.widget1 = QWidget(self.tab2)
        self.del_row1 = QPushButton("Удалить", self.widget1)
        self.del_row1.clicked.connect(self.del_row_1)
        layout1 = QGridLayout()
        layout1.addWidget(self.del_row1)
        self.widget1.setLayout(layout1)

        layout2 = QGridLayout()
        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.addWidget(self.money_table)
        splitter1.addWidget(self.widget1)
        layout2.addWidget(splitter1)

        income_splitter = QSplitter(Qt.Vertical)
        income_splitter.addWidget(splitter1)
        income_splitter.addWidget(self.income_buttons)
        self.income_layout = QGridLayout()
        self.income_layout.addWidget(income_splitter)
        self.tab2.setLayout(self.income_layout)

        self.tab3 = QWidget()
        self.tabWidget.addTab(self.tab3, "Отчетность")

        # Создание графика
        self.series = QHorizontalBarSeries()
        self.chart = QChart()
        self.chart.setTitle("Сводка расходов")
        self.chart.addSeries(self.series)
        self.chartView = QChartView(self.chart)

        self.axisX = QValueAxis()
        self.chart.addAxis(self.axisX, Qt.AlignBottom)
        self.series.attachAxis(self.axisX)

        self.reportlayout = QGridLayout()
        self.reportlayout.addWidget(self.chartView)
        self.tab3.setLayout(self.reportlayout)

        self.money = 0

        self.tableWidget = QTableWidget(self.tab)
        self.buttons = QTableWidget(self.tab)

        self.widget = QWidget(self.tab)

        self.del_row = QPushButton("Удалить", self.widget)
        self.del_row.clicked.connect(self.deleterow)

        self.spent = 0
        self.spent_btn = QPushButton(str(self.spent), self.widget)
        self.spent_btn.setDisabled(True)

        self.spent_label = QLabel("Всего потрачено:", self.widget)

        self.left_label = QLabel("Осталось:", self.widget)
        self.left_btn = QPushButton(str(self.money), self.widget)
        self.left_btn.setDisabled(True)


        self.money_layout = QGridLayout()
        self.money_layout.addWidget(self.spent_label)
        self.money_layout.addWidget(self.spent_btn)
        self.money_layout.addWidget(self.left_label)
        self.money_layout.addWidget(self.left_btn)
        verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.money_layout.addItem(verticalSpacer)
        self.money_layout.addWidget(self.del_row)
        self.widget.setLayout(self.money_layout)

        self.money_splitter = QSplitter(Qt.Horizontal)
        self.money_splitter.addWidget(self.tableWidget)
        self.money_splitter.addWidget(self.widget)

        splitter = QSplitter(Qt.Vertical)
        splitter.addWidget(self.money_splitter)
        splitter.addWidget(self.buttons)

        self.layout = QGridLayout()
        self.layout.addWidget(splitter)
        self.tab.setLayout(self.layout)

        self.graph_data = {}
        self.showMaximized()

    def del_row_1(self):  # Удаление записей из доходов
        try:
            self.money -= float(self.money_table.item(self.money_table.currentRow(), 1).text())
            self.left_btn.setText(str(self.money))
        except AttributeError:
            pass
        self.money_table.removeRow(self.money_table.currentRow())

    def init_spent(self):  # Обновление потраченных денег
        spent = 0
        try:
            for i in range(self.tableWidget.rowCount()):
                spent += float(self.tableWidget.item(i, 3).text())
            self.spent = spent
            self.spent_btn.setText(str(spent))
        except AttributeError:
            pass

    def add_type_income_dialog(self):  # Диалог добавления типа доходов
        self.dialog_add_income = QDialog()
        self.dialog_add_income.setStyleSheet(appstyle)
        self.dialog_add_income.setWindowTitle("Add type")
        self.type_add = QLineEdit()
        self.type_add.setPlaceholderText("Type")
        ok = QPushButton("Add", self.dialog_add_income)
        savebtn = QPushButton("Cancel", self.dialog_add_income)
        layout = QGridLayout()
        layout.addWidget(self.type_add)
        layout.addWidget(ok)
        layout.addWidget(savebtn)
        self.dialog_add_income.setLayout(layout)
        ok.clicked.connect(self.addtypeincome)
        savebtn.clicked.connect(self.dialog_add_income.close)
        self.dialog_add_income.exec_()

    def addtypeincome(self):  # Добавление типа доходов (вызывается соответствующим диалогом)
        text = self.type_add.text()
        cursor = db.cursor()
        query = f"insert into income_types(type) values('{text}')"
        cursor.execute(query)
        db.commit()
        self.init_income_types()
        self.init_income_buttons()
        self.dialog_add_income.close()

    def delete_income_type_dialog(self):  # Диалог удаления типа доходов
        self.dialog_delete_income = QDialog()
        self.dialog_delete_income.setStyleSheet(appstyle)
        self.dialog_delete_income.setWindowTitle("Delete income type")
        self.type_del_income = QComboBox()
        self.type_del_income.addItems(self.income_type.keys())
        ok = QPushButton("Delete", self.dialog_delete_income)
        savebtn = QPushButton("Cancel", self.dialog_delete_income)
        layout = QGridLayout()
        layout.addWidget(self.type_del_income)
        layout.addWidget(ok)
        layout.addWidget(savebtn)
        self.dialog_delete_income.setLayout(layout)
        ok.clicked.connect(self.deleteincometype)
        savebtn.clicked.connect(self.dialog_delete_income.close)
        self.dialog_delete_income.exec_()

    def deleteincometype(self):  # Удаление типа доходов (вызывается соответствующим диалогом)
        cursor = db.cursor()
        query = f"""delete from income_types where type = '{self.type_del_income.currentText()}'"""
        cursor.execute(query)
        db.commit()
        self.init_income_types()
        self.init_income_buttons()
        self.dialog_delete_income.close()

    def init_graph_data(self):  # Обновление данных для графика отчетности
        try:
            for i in range(self.tableWidget.rowCount()):
                try:
                    self.graph_data[self.tableWidget.item(i, 0).text()] += float(self.tableWidget.item(i, 3).text())
                except:
                    self.graph_data[self.tableWidget.item(i, 0).text()] = float(self.tableWidget.item(i, 3).text())
        except AttributeError:
            pass

    def init_money(self):  # Обновления оставщихся денег
        money = 0
        try:
            for i in range(self.money_table.rowCount()):
                money += float(self.money_table.item(i, 1).text())

            for i in range(self.tableWidget.rowCount()):
                money -= float(self.tableWidget.item(i, 3).text())
        except AttributeError:
            pass

        self.money = money
        self.left_btn.setText(str(self.money))

    def init_income_buttons(self):  # Инициализация кнопок типов доходов
        cursor = db.cursor()
        result = cursor.execute("SELECT type FROM income_types").fetchall()

        self.income_buttons.setRowCount(1)
        self.income_buttons.setColumnCount(len(result))

        self.income_buttons.setVerticalHeaderItem(0, QTableWidgetItem("Тип дохода"))

        header = self.income_buttons.horizontalHeader()
        for i in range(self.income_buttons.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

        result = [str(x[0]) for x in result]

        for i, elem in enumerate(result):
            button = QPushButton(str(elem))
            button.clicked.connect(self.add_income)
            self.income_buttons.setCellWidget(0, i, button)
        self.income_buttons.show()

    def add_income(self):  # Добавление записи дохода
        try:
            self.money_table.item(0, 0).text()
            self.money_table.setRowCount(self.money_table.rowCount() + 1)
            self.money_table.setCurrentCell(self.money_table.rowCount() - 1, 0)
            text = self.sender().text()
            row = self.money_table.currentRow()
            self.money_table.setItem(row, 0, QTableWidgetItem(text))
            self.money_table.setCurrentCell(row, 1)
            self.money_table.setItem(row, 2, QTableWidgetItem(date.today().strftime('%Y-%m-%d')))
        except AttributeError:
            if self.money_table.rowCount() == 0:
                self.money_table.setRowCount(1)
            text = self.sender().text()
            self.money_table.setItem(0, 0, QTableWidgetItem(text))
            self.money_table.setCurrentCell(0, 1)
            self.money_table.setItem(0, 2, QTableWidgetItem(date.today().strftime('%Y-%m-%d')))

    def init_income_types(self):  # Обновление словаря с типами доходов
        cursor = db.cursor()
        result = cursor.execute("SELECT id, type FROM income_types").fetchall()
        for i in range(len(result)):
            result[i] = [x for x in result[i]]

        self.income_type = {}

        for el in result:
            self.income_type[el[1]] = el[0]

    def init_incomes(self):  # Выведение уже записанных доходов в таблицу
        cursor = db.cursor()
        query = "select type, price, date from incomes"
        result = cursor.execute(query).fetchall()
        self.money_table.setRowCount(len(result))
        self.money_table.setColumnCount(4)
        titles = ["Доход", "Прибыль", "Дата"]
        for i in range(3):
            self.money_table.setHorizontalHeaderItem(i, QTableWidgetItem(titles[i]))

        header = self.money_table.horizontalHeader()
        for i in range(self.money_table.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        for i in range(len(result)):
            result[i] = [x for x in result[i]]

        for i, row in enumerate(result):
            for j, col in enumerate(row):
                self.money_table.setItem(i, j, QTableWidgetItem(str(col)))
                self.money_table.setItem(i, 3, QTableWidgetItem(str(result[i][1])))

        self.money_table.setColumnHidden(3, True)
        self.money_table.itemChanged.connect(self.money_item_changed)
        self.money_table.show()

    def money_item_changed(self, item):  # Функция, которая реагирует на изменение данных в таблице доходов
        if item.column() == 1:
            try:
                float(item.text())
            except ValueError:
                msg = "Доход должен быть числом"
                title = "Income error"
                reply = QMessageBox.critical(self, title, msg, QMessageBox.Ok)

                if reply == QMessageBox.Ok:
                    return

            if float(item.text()) < 0:
                msg = "Доход не может быть меньше нуля"
                title = "Income error"
                reply = QMessageBox.critical(self, title, msg, QMessageBox.Ok)

                if reply == QMessageBox.Ok:
                    return

            try:
                last = float(self.money_table.item(item.row(), 3).text())
            except AttributeError:
                last = 0

            self.money -= last
            self.money += float(item.text())
            self.left_btn.setText(str(self.money))
            self.money_table.setItem(item.row(), 3, QTableWidgetItem(item.text()))

    def init_type(self):  # Обновление словаря с типами покупок
        cursor = db.cursor()
        query_types = "select * from types"
        result = cursor.execute(query_types).fetchall()
        self.types = {}
        for i in result:
            self.types[str(i[1])] = str(i[0])
        query_subtypes = "select * from subtypes"
        result = cursor.execute(query_subtypes).fetchall()
        self.subtypes = {}
        for i in result:
            self.subtypes[i[2]] = i[0]

    def deletetypedialog(self):  # Диалог удаления типа покупок
        self.dialog_delete_type = QDialog()
        self.dialog_delete_type.setStyleSheet(appstyle)
        self.dialog_delete_type.setWindowTitle("Delete Type")
        self.type_del_type = QComboBox()
        self.type_del_type.addItems(self.types.keys())
        ok = QPushButton("Delete", self.dialog_delete_type)
        savebtn = QPushButton("Cancel", self.dialog_delete_type)
        layout = QGridLayout()
        layout.addWidget(self.type_del_type)
        layout.addWidget(ok)
        layout.addWidget(savebtn)
        self.dialog_delete_type.setLayout(layout)
        ok.clicked.connect(self.deletetype)
        savebtn.clicked.connect(self.dialog_delete_type.close)
        self.dialog_delete_type.exec_()

    def deletetype(self):  # Удаление типа покупок (вызывается соответствующей функцией)
        cursor = db.cursor()
        query = f"delete from subtypes where type = {self.types[self.type_del_type.currentText()]}"
        cursor.execute(query)
        query = f"""delete from types where type = '{self.type_del_type.currentText()}'"""
        cursor.execute(query)
        db.commit()
        self.init_type()
        self.init_buttons()
        self.dialog_delete_type.close()

    def deletesubtypedialog(self):  # Диалог удаления подтипа покупок
        self.dialog_delete_type = QDialog()
        self.dialog_delete_type.setStyleSheet(appstyle)
        self.dialog_delete_type.setWindowTitle("Delete subtype")
        self.type_del_type = QComboBox()
        self.type_del_type.addItems(self.types.keys())
        self.subtype_del_type = QComboBox()
        keys = []
        cursor = db.cursor()
        result = cursor.execute(f"""select subtype from subtypes where type = {
        self.types[self.type_del_type.currentText()]}""").fetchall()
        for el in result:
            keys.append(str(el[0]))
        self.subtype_del_type.addItems(keys)
        self.type_del_type.currentTextChanged.connect(self.changed)
        ok = QPushButton("Delete", self.dialog_delete_type)
        savebtn = QPushButton("Cancel", self.dialog_delete_type)
        layout = QGridLayout()
        layout.addWidget(self.type_del_type)
        layout.addWidget(self.subtype_del_type)
        layout.addWidget(ok)
        layout.addWidget(savebtn)
        self.dialog_delete_type.setLayout(layout)
        ok.clicked.connect(self.deletesubtype)
        savebtn.clicked.connect(self.dialog_delete_type.close)
        self.dialog_delete_type.exec_()

    def changed(self):  # Какой то костыль, я честно не знаю, что он делает, но без него ничего не работает
        self.subtype_del_type.clear()
        keys = []
        cursor = db.cursor()
        result = cursor.execute(f"""select subtype from subtypes where type = {
        self.types[self.type_del_type.currentText()]}""").fetchall()
        for el in result:
            keys.append(str(el[0]))
        self.subtype_del_type.addItems(keys)

    def deletesubtype(self):  # Удаление подтипа покупок (вызывается соответствующей функцией)
        query = f"""delete from subtypes where subtype = '{
        self.subtype_del_type.currentText()}' and type = {self.types[self.type_del_type.currentText()]}"""
        cursor = db.cursor()
        cursor.execute(query)
        db.commit()
        self.init_type()
        self.init_buttons()
        self.dialog_delete_type.close()

    def addsubtypedialog(self):  # Диалог добавления подтипа покупок
        self.dialog_delete_type = QDialog()
        self.dialog_delete_type.setStyleSheet(appstyle)
        self.dialog_delete_type.setWindowTitle("Add type")
        self.type_add = QLineEdit()
        self.type_add.setPlaceholderText("Type")
        self.subtype_add = QLineEdit()
        self.subtype_add.setPlaceholderText("Subtype")
        ok = QPushButton("Add", self.dialog_delete_type)
        savebtn = QPushButton("Cancel", self.dialog_delete_type)
        layout = QGridLayout()
        layout.addWidget(self.type_add)
        layout.addWidget(self.subtype_add)
        layout.addWidget(ok)
        layout.addWidget(savebtn)
        self.dialog_delete_type.setLayout(layout)
        ok.clicked.connect(self.addsubtype)
        savebtn.clicked.connect(self.dialog_delete_type.close)
        self.dialog_delete_type.exec_()

    def addsubtype(self):  # Добавление подтипа покупок (вызывается соответствующей функцией)
        if type(self.subtype_add) != str and type(self.type_add) != str:
            self.subtype_add = str(self.subtype_add.text())
            self.type_add = str(self.type_add.text())
        cursor = db.cursor()
        if self.type_add not in self.types:
            self.addtype()
        query = f"insert into subtypes(type, subtype) values('" \
                f"{self.types[self.type_add]}', '{self.subtype_add}')"
        cursor.execute(query)
        db.commit()
        self.init_buttons()
        try:
            self.dialog_delete_type.close()
        except AttributeError:
            pass

    def addtype(self):  # Добавление типа (вызывается соответствующей функцией)
        if type(self.type_add) != str:
            self.type_add = str(self.type_add.text())
        query = f"insert into types(type) values('{self.type_add}')"
        cursor = db.cursor()
        cursor.execute(query)
        db.commit()
        self.init_type()

    def init_table(self):  # Выведение уже записанных расходов в таблицу
        cursor = db.cursor()
        result = cursor.execute("SELECT type, subtype, name, price, date FROM purchases").fetchall()
        try:
            self.tableWidget.setRowCount(len(result))
            self.tableWidget.setColumnCount(len(result[0]) + 1)
        except IndexError:
            self.tableWidget.setRowCount(1)
            self.tableWidget.setColumnCount(6)
            self.tableWidget.show()
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        self.titles = [description[0] for description in cursor.description]
        titles = ["Категория", "Подкатегория", "Примечание", "Цена", "Дата"]
        for i, val in enumerate(titles):
            self.tableWidget.setHorizontalHeaderItem(i, QTableWidgetItem(val))
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                if j != 2:
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
                else:
                    if str(val) != "None":
                        self.tableWidget.setItem(i, j, QTableWidgetItem(str(val)))
            self.tableWidget.setItem(i, 5, QTableWidgetItem(str(result[i][3])))

        self.tableWidget.setColumnHidden(5, True)
        self.tableWidget.show()
        self.tableWidget.itemChanged.connect(self.item_changed)
        self.init_graph_data()
        self.refresh_graph()
        self.saved = True

    def deleterow(self):  # Удаление записи из таблицы расходов
        try:
            try:
                self.graph_data[self.tableWidget.item(self.tableWidget.currentRow(), 0).text()] -= \
                    float(self.tableWidget.item(self.tableWidget.currentRow(), 3).text())
            except KeyError:
                pass
            self.refresh_graph()
            self.spent -= float(self.tableWidget.item(self.tableWidget.currentRow(), 3).text())
            self.spent_btn.setText(str(self.spent))
            self.money += float(self.tableWidget.item(self.tableWidget.currentRow(), 3).text())
            self.left_btn.setText(str(self.money))
        except AttributeError:
            pass
        self.tableWidget.removeRow(self.tableWidget.currentRow())

    def item_changed(self, item):  # Функция, которая реагирует на изменение элемента в таблице расходов
        text = self.tableWidget.item(item.row(), 0).text()
        if item.column() == 3:
            try:
                float(item.text())
            except ValueError:
                msg = "Цена должна быть числом"
                title = "Price error"
                reply = QMessageBox.critical(self, title, msg, QMessageBox.Ok)

                if reply == QMessageBox.Ok:
                    return
            if float(item.text()) < 0:
                msg = "Цена не может быть меньше нуля"
                title = "Price error"
                reply = QMessageBox.critical(self, title, msg, QMessageBox.Ok)

                if reply == QMessageBox.Ok:
                    return
            try:
                last = float(self.tableWidget.item(item.row(), 5).text())
            except AttributeError:
                last = 0

            try:
                self.graph_data[text] -= last
                self.graph_data[text] += float(item.text())
            except Exception as e:
                self.graph_data[text] = float(item.text())

            self.spent -= last
            self.spent += float(item.text())
            self.spent_btn.setText(str(self.spent))
            self.money += last
            self.money -= float(item.text())
            self.left_btn.setText(str(self.money))
            self.chart.removeAxis(self.axisX)
            self.refresh_graph()

            self.tableWidget.setItem(item.row(), 5, QTableWidgetItem(item.text()))
        self.saved = False

    def refresh_graph(self):  # Обновление и перерисовка графика
        self.chart.removeAllSeries()
        self.chart.removeAxis(self.axisX)
        self.series = QHorizontalBarSeries()
        for key, val in self.graph_data.items():
            if val > 0:
                obj = QBarSet(str(key))
                obj.append([val])
                self.series.append(obj)
        self.chart.addSeries(self.series)
        self.axisX = QValueAxis()
        self.chart.addAxis(self.axisX, Qt.AlignBottom)
        self.series.attachAxis(self.axisX)
        self.chartView.repaint()

    def init_buttons(self):  # Инициализация кнопок добавления расхода
        self.buttons.setRowCount(0)
        cursor = db.cursor()
        result = cursor.execute("SELECT type FROM types").fetchall()
        self.buttons.setColumnCount(len(result))
        for i, elem in enumerate(result):
            self.buttons.setHorizontalHeaderItem(i, QTableWidgetItem(str(elem[0])))

        query = """select subtype from subtypes
        where type in (select id from types where type=?)"""
        result1 = []
        for i in result:
            result1.append(cursor.execute(query, (str(i[0]),)).fetchall())
        max_len = 0
        for i in result1:
            if len(i) > max_len:
                max_len = len(i)
        self.buttons.setRowCount(max_len)

        header = self.buttons.horizontalHeader()
        for i in range(self.buttons.columnCount()):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

        for i in range(len(result1)):
            result1[i] = [str(x[0]) for x in result1[i]]

        for i in range(len(result1)):
            for j in range(max_len - len(result1[i])):
                result1[i].append(None)
        for i, elem in enumerate(result1):
            for j, val in enumerate(elem):
                if val is not None:
                    button = QPushButton(str(val))
                    button.clicked.connect(self.add_record)
                    self.buttons.setCellWidget(j, i, button)
        self.buttons.show()

    def add_record(self):  # Добавление записи в таблицу расходов
        try:
            self.tableWidget.item(0, 0).text()
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            self.tableWidget.setCurrentCell(self.tableWidget.rowCount() - 1, 0)
            header = self.buttons.horizontalHeaderItem(self.buttons.currentColumn()).text()
            text = self.sender().text()
            row = self.tableWidget.currentRow()
            self.tableWidget.setItem(row, 0, QTableWidgetItem(header))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(text))
            self.tableWidget.setCurrentCell(row, 3)
            self.tableWidget.setItem(row, 4, QTableWidgetItem(date.today().strftime('%Y-%m-%d')))
        except AttributeError:
            if self.tableWidget.rowCount() == 0:
                self.tableWidget.setRowCount(1)
            header = self.buttons.horizontalHeaderItem(self.buttons.currentColumn()).text()
            text = self.sender().text()
            self.tableWidget.setItem(0, 0, QTableWidgetItem(header))
            self.tableWidget.setItem(0, 1, QTableWidgetItem(text))
            self.tableWidget.setCurrentCell(0, 3)
            self.tableWidget.setItem(0, 4, QTableWidgetItem(date.today().strftime('%Y-%m-%d')))

    def save(self):  # Сохранение всех данных в бд
        if self.tableWidget.rowCount() > 0:
            try:
                data = []
                for i in range(self.tableWidget.rowCount()):
                    data1 = {}
                    for j in range(5):
                        if j == 2:
                            try:
                                text = self.tableWidget.item(i, j).text()
                            except AttributeError:
                                text = None
                        else:
                            text = self.tableWidget.item(i, j).text()
                        if j == 3:
                            try:
                                text = float(text)
                            except ValueError:
                                msg = "Цена должна быть числом"
                                title = "Price error"
                                reply = QMessageBox.critical(self, title, msg, QMessageBox.Ok)

                                if reply == QMessageBox.Ok:
                                    return
                        data1[self.titles[j]] = text
                    data.append(data1)
                cursor = db.cursor()
                query = "delete from purchases"
                cursor.execute(query)
                db.commit()
                for el in data:
                    keys = tuple(el.keys())
                    values = tuple(el.values())
                    query = f"""insert into purchases('{keys[0]}', '{keys[1]}', '{keys[2]}', '{keys[3]}', {keys[4]})
                    values('{values[0]}', '{values[1]}', '{values[2]}', '{values[3]}', '{values[4]}')"""
                    cursor.execute(query)
                    db.commit()
                    self.saved = True
            except AttributeError:
                self.notenoughdata()
            try:
                self.dialog.close()
            except:
                pass
        else:
            cursor = db.cursor()
            query = "delete from purchases"
            cursor.execute(query)
            db.commit()
            self.saved = True


        if self.money_table.rowCount() > 0:
            try:
                data = []
                for i in range(self.money_table.rowCount()):
                    data1 = []
                    for j in range(3):
                        text = self.money_table.item(i, j).text()
                        if j == 1:
                            try:
                                text = float(text)
                            except ValueError:
                                msg = "Доход должен быть числом"
                                title = "Price error"
                                reply = QMessageBox.critical(self, title, msg, QMessageBox.Ok)

                                if reply == QMessageBox.Ok:
                                    return
                        data1.append(text)
                    data.append(data1)
                cursor = db.cursor()
                query = "delete from incomes"
                cursor.execute(query)
                db.commit()
                for el in data:
                    query = f"""insert into incomes('type', 'price', 'date')
                    values('{el[0]}', '{el[1]}', '{el[2]}')"""
                    cursor.execute(query)
                    db.commit()
                    self.saved = True
            except AttributeError:
                self.notenoughdata()
            try:
                self.dialog.close()
            except:
                pass
        else:
            cursor = db.cursor()
            query = "delete from incomes"
            cursor.execute(query)
            db.commit()
            self.saved = True

    def notenoughdata(self):  # Диалог незаполненной таблицы
        msg = QMessageBox()
        msg.setStyleSheet(appstyle)
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Заполните все ячейки")
        msg.setWindowTitle("Not all data")
        msg.setStandardButtons(QMessageBox.Close)
        msg.exec_()

    def quit(self):  # Вызывается при выходе из приложения если данные не сохранены
        if not self.saved:
            self.dialog = QDialog()
            self.dialog.setStyleSheet(appstyle)
            self.dialog.setWindowTitle("Quit without saving?")
            self.dialog.resize(150, 90)
            self.ok = QPushButton("Yes", self.dialog)
            self.savebtn = QPushButton("Save", self.dialog)
            self.ok.move(32, 15)
            self.savebtn.move(32, 50)
            self.layout = QGridLayout()
            self.layout.addWidget(self.ok)
            self.layout.addWidget(self.savebtn)
            self.dialog.setLayout(self.layout)
            self.ok.clicked.connect(qApp.quit)
            self.savebtn.clicked.connect(self.save)
            self.dialog.exec_()
        else:
            qApp.quit()

    def export(self):  # Экспорт в .csv файл
        try:
            try:
                data = []
                for i in range(self.tableWidget.rowCount()):
                    data1 = {}
                    for j in range(5):
                        if j == 2:
                            try:
                                text = self.tableWidget.item(i, j).text().strip("\n")
                            except AttributeError:
                                text = "None"
                        else:
                            text = self.tableWidget.item(i, j).text().strip("\n")
                        data1[self.titles[j]] = text
                    data.append(data1)

                path = QFileDialog.getExistingDirectory(self)
                file = open(f"{path}/info.csv", "w", encoding="UTF-8")
                for el in data:
                    keys = tuple(el.keys())
                    to_write = ";".join(el[i] for i in keys)
                    print(to_write, file=file)
                file.close()
            except AttributeError:
                self.notenoughdata()
        except PermissionError:
            pass

    def import_file(self):  # Импорт из .csv файла
        try:
            path = QFileDialog.getOpenFileName(self, 'Choose file', '','(*.csv)')[0]
            file = open(path)
            self.tableWidget.setRowCount(0)
            self.tableWidget.setRowCount(0)
            for i, line in enumerate(file):
                data = line.split(";")
                if data[0] in self.types and data[1] in self.subtypes:
                    self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
                    for j in range(5):
                        if j != 2 or str(data[j]) != "None":

                            self.tableWidget.setItem(i, j, QTableWidgetItem(str(data[j]).strip("\n")))
                else:
                    if data[0] not in self.types:
                        msg = f"No such type {data[0]}, would you like to add it?"
                    else:
                        msg = f"No such subtype {data[1]} in type {data[0]}, would you like to add it?"
                    reply = QMessageBox.question(self, "Import error", msg, QMessageBox.Yes, QMessageBox.No)

                    if reply == QMessageBox.Yes:
                        self.type_add = data[0]
                        self.subtype_add = data[1]
                        self.addsubtype()
                        self.init_buttons()
                        self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
                        for j in range(5):
                            if j != 2 or str(data[j]) != "None":
                                self.tableWidget.setItem(i, j, QTableWidgetItem(str(data[j])))
        except FileNotFoundError:
            pass


def encrypt(password):  # Шифровка пароля
    return sha256(password).hexdigest()


def logined():  # Определяет, зарегестрирован ли пользователь
    cursor = db.cursor()
    result = cursor.execute("""select * from login""").fetchall()
    if len(result) > 0:
        return True
    return False


if __name__ == '__main__':
    if sys.platform != "win32":
        framestyle = """
                border-radius: 1px;
                """
        appstyle = """
                color: #ffffff;
                background-color: #333333;
                """
    else:
        framestyle = ""
        appstyle = ""

    path = f"{str(os.path.expanduser('~'))}/.homeaccountant/db.db"
    try:
        open(path).close()
    except FileNotFoundError:
        path = "db.db"
    db = sqlite3.connect(path)
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Breeze"))
    if not logined():
        ex = LoginFirstTime()
    else:
        ex = Login()
    sys.exit(app.exec_())

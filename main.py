#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

import os
from PyQt5.QtSql import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from hashlib import sha256
import sqlite3
import csv
# from PyQt5.QtGui import QStyle
# from PyQt5 import QStyleFactory
from screeninfo import get_monitors

near = [
    'qwe', 'wer', 'ert', 'rty', 'tyu', 'yui', 'uio', 'iop',
    'asd', 'sdf', 'dfg', 'fgh', 'ghj', 'hjk', 'jkl',
    'zxc', 'xcv', 'cvb', 'vbn', 'bnm',
    'йцу', 'цук', 'уке', 'кен', 'енг', 'нгш', 'гшщ', 'шщз', 'щзх', 'зхъ',
    'фыв', 'ыва', 'вап', 'апр', 'про', 'рол', 'олд', 'лдж', 'джэ',
    'ячс', 'чсм', 'сми', 'мит', 'ить', 'тьб', 'ьбю', 'жэё'
]


class LoginFirstTime(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
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

    def write(self):
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
            self.new_window = Example()
            self.new_window.show()
            self.hide()


class Login(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
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

    def launch(self):
        cursor = db.cursor()
        result = cursor.execute("""select * from login""").fetchall()
        string_to_hash = self.password.text()
        hash = sha256(str(string_to_hash).encode('utf-8'))
        if str(hash.hexdigest()) == result[0][-1] and self.login.text() == result[0][0]:

            self.new_window = Example()
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


class Example(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()
        self.init_table()
        self.init_buttons()
        self.init_type()

    def initUI(self):
        self.frame = QFrame()
        self.frame.setStyleSheet(framestyle)
        self.setStyleSheet(appstyle)

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
        addType.setStatusTip('New type')
        addType.triggered.connect(self.addsubtypedialog)

        delSubtype = QAction('&Del subtype', self)
        delSubtype.setShortcut('Ctrl+D')
        delSubtype.setStatusTip('Delete subtype')
        delSubtype.triggered.connect(self.deletesubtypedialog)

        delType = QAction('&Del type', self)
        delType.setShortcut('Ctrl+F')
        delType.setStatusTip('Delete type')
        delType.triggered.connect(self.deletetypedialog)

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
        fileMenu.addAction(export)
        fileMenu.addAction(import_file)
        self.x = get_monitors()[0].height
        self.y = get_monitors()[0].width
        self.setGeometry(0, 0, self.y, self.x)
        self.setWindowTitle('Home Accountant')
        self.saved = True
        self.tableWidget = QTableWidget()
        # self.tableWidget.cellChanged.connect(self.item_changed)
        self.buttons = QTableWidget(self)
        self.mainwidget = QWidget(self)
        self.setCentralWidget(self.mainwidget)
        self.del_row = QPushButton("Удалить", self)
        self.del_row.clicked.connect(self.deleterow)
        self.layout = QGridLayout()
        self.layout.addWidget(self.tableWidget)
        self.layout.addWidget(self.del_row)
        self.layout.addWidget(self.buttons)
        self.mainwidget.setLayout(self.layout)
        self.show()
    #
    # def item_changed(self, item):
    #     print("Help me")
    #     if self.titles[item.column()] == "Цена":
    #         print(item.text())


    def init_type(self):
        cursor = db.cursor()
        query_types = "select * from types"
        result = cursor.execute(query_types).fetchall()
        self.types = {}
        for i in result:
            self.types[i[1]] = i[0]
        query_subtypes = "select * from subtypes"
        result = cursor.execute(query_subtypes).fetchall()
        self.subtypes = {}
        for i in result:
            self.subtypes[i[2]] = i[0]

    def deletetypedialog(self):
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

    def deletetype(self):
        cursor = db.cursor()
        query = f"delete from subtypes where type = {self.types[self.type_del_type.currentText()]}"
        cursor.execute(query)
        query = f"""delete from types where type = '{self.type_del_type.currentText()}'"""
        cursor.execute(query)
        db.commit()
        self.init_type()
        self.init_buttons()
        self.dialog_delete_type.close()

    def deletesubtypedialog(self):
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

    def deletesubtype(self):
        query = f"""delete from subtypes where subtype = '{
        self.subtype_del_type.currentText()}' and type = {self.types[self.type_del_type.currentText()]}"""
        print(query)
        cursor = db.cursor()
        cursor.execute(query)
        db.commit()
        self.init_type()
        self.init_buttons()
        self.dialog_delete_type.close()

    def addsubtypedialog(self):
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

    def addsubtype(self):
        if type(self.subtype_add) != str and type(self.type_add) != str:
            self.subtype_add = self.subtype_add.text()
            self.type_add = self.type_add.text()
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

    def addtype(self):
        if type(self.type_add) != str:
            self.type_add = self.type_add.text()
        query = f"insert into types(type) values('{self.type_add}')"
        cursor = db.cursor()
        cursor.execute(query)
        db.commit()
        self.init_type()

    def init_table(self):
        cursor = db.cursor()
        # Получили результат запроса, который ввели в текстовое поле
        result = cursor.execute("SELECT type, subtype, name, price FROM purchases").fetchall()
        # Заполнили размеры таблицы
        self.start_db = result
        try:
            self.tableWidget.setRowCount(len(result))
            # Если запись не нашлась, то не будем ничего делать
            self.tableWidget.setColumnCount(len(result[0]))
        except IndexError:
            self.tableWidget.setRowCount(1)
            self.tableWidget.setColumnCount(4)
            self.tableWidget.show()
        self.titles = [description[0] for description in cursor.description]
        titles = ["Категория", "Подкатегория", "Товар", "Цена"]
        for i, val in enumerate(titles):
            self.tableWidget.setHorizontalHeaderItem(i, QTableWidgetItem(str(val)))
        # Заполнили таблицу полученными элементами
        for i, elem in enumerate(result):
            for j, val in enumerate(elem):
                self.tableWidget.setItem(i, j, QTableWidgetItem(val))
        self.tableWidget.show()
        self.saved = True

    def deleterow(self):
        self.tableWidget.removeRow(self.tableWidget.currentRow())

    def item_changed(self, item):
        self.saved = False

    def init_buttons(self):
        cursor = db.cursor()
        result = cursor.execute("SELECT type FROM types").fetchall()
        self.buttons.setRowCount(len(result))
        self.buttons.setColumnCount(len(result[0]))
        for i, elem in enumerate(result):
            self.buttons.setVerticalHeaderItem(i, QTableWidgetItem(str(elem[0])))

        query = """select subtype from subtypes
        where type in (select id from types where type=?)"""
        result1 = []
        for i in result:
            result1.append(cursor.execute(query, (str(i[0]),)).fetchall())
        max_len = 0
        for i in result1:
            if len(i) > max_len:
                max_len = len(i)
        self.buttons.setColumnCount(max_len)
        for i, elem in enumerate(result1):
            for j, val in enumerate(elem):
                for l, lav in enumerate(val):
                    button = QPushButton(str(lav))
                    button.clicked.connect(self.add_record)
                    self.buttons.setCellWidget(i, j, button)
        self.buttons.show()

    def addrow(self):
        self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
        self.tableWidget.setCurrentCell(self.tableWidget.rowCount() - 1, 0)

    def add_record(self):
        try:
            self.tableWidget.item(0, 0).text()
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            self.tableWidget.setCurrentCell(self.tableWidget.rowCount() - 1, 0)
            header = self.buttons.verticalHeaderItem(self.buttons.currentRow()).text()
            text = self.sender().text()
            row = self.tableWidget.currentRow()
            self.tableWidget.setItem(row, 0, QTableWidgetItem(header))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(text))
            self.tableWidget.setCurrentCell(row, 2)
        except AttributeError:
            if self.tableWidget.rowCount() == 0:
                self.tableWidget.setRowCount(1)
            header = self.buttons.verticalHeaderItem(self.buttons.currentRow()).text()
            text = self.sender().text()
            self.tableWidget.setItem(0, 0, QTableWidgetItem(header))
            self.tableWidget.setItem(0, 1, QTableWidgetItem(text))
            self.tableWidget.setCurrentCell(0, 2)

    def save(self):
        try:
            data = []
            for i in range(self.tableWidget.rowCount()):
                data1 = {}
                for j in range(4):
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
                query = f"""insert into purchases('{keys[0]}', '{keys[1]}', '{keys[2]}', '{keys[3]}')
                values('{values[0]}', '{values[1]}', '{values[2]}', '{values[3]}')"""
                cursor.execute(query)
                db.commit()
                self.saved = True
        except AttributeError:
            self.notenoughdata()
        try:
            self.dialog.close()
        except:
            pass

    def notenoughdata(self):
        msg = QMessageBox()
        msg.setStyleSheet(appstyle)
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Заполните все ячейки")
        msg.setWindowTitle("Not all data")
        msg.setStandardButtons(QMessageBox.Close)
        msg.exec_()

    def quit(self):
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

    def export(self):
        try:
            data = []
            for i in range(self.tableWidget.rowCount()):
                data1 = {}
                for j in range(4):
                    text = self.tableWidget.item(i, j).text().strip("\n")
                    data1[self.titles[j]] = text
                data.append(data1)

            path = QFileDialog.getExistingDirectory(self)
            file = open(f"{path}/info.csv", "w", encoding="UTF-8")
            print(data)
            for el in data:
                keys = tuple(el.keys())
                to_write = ";".join(el[i] for i in keys)
                print(to_write, file=file)
                # to_write = [el[_] for _ in keys]
                # file.write(to_write)
                # writer.writerow(to_write)
            file.close()
        except AttributeError:
            self.notenoughdata()

    def import_file(self):
        path = QFileDialog.getOpenFileName(self, 'Choose file', '','(*.csv)')[0]
        file = open(path)
        delta = self.tableWidget.rowCount()
        for i, line in enumerate(file):
            data = line.split(";")
            if data[0] in self.types and data[1] in self.subtypes:
                self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
                for j in range(4):
                    self.tableWidget.setItem(i + delta, j, QTableWidgetItem(str(data[j]).strip("\n")))
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
                    for j in range(4):
                        self.tableWidget.setItem(i + delta, j, QTableWidgetItem(str(data[j])))


def encrypt(password):
    return sha256(password).hexdigest()


def logined():
    cursor = db.cursor()
    result = cursor.execute("""select * from login""").fetchall()
    if len(result) > 0:
        return True
    return False


if __name__ == '__main__':
    if os.uname().sysname != "Windows":
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
    path = f"{str(os.path.expanduser('~'))}/.local/share/homeaccountant/db.db"
    try:
        open(path)
    except FileNotFoundError:
        path = "db.db"
    db = sqlite3.connect(path)
    # cursor = db.cursor()
    # query = "delete from purchases"
    # cursor.execute(query)
    # db.commit()
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Breeze"))
    # app.setStyleSheet("""
    #             color: #ffffff;
    #             background-color: #333333;
    #             """)
    if not logined():
        ex = LoginFirstTime()
    else:
        ex = Login()
    sys.exit(app.exec_())

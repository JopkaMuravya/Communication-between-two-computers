from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QListWidgetItem, QWidget, QLabel
from PyQt5.QtCore import QThread, pyqtSignal
import sys
import datetime
import time
from MainTryUI import Ui_MainTry
from your_answerUI import Ui_Your_Answer
from answerUI import Ui_Answer
from threading import Thread
import socket
import os

clientaa = None
stop_thread = False
NumberImage = 0


class UAnswer(QWidget, Ui_Your_Answer):
    def __init__(self, parent=None):
        super(UAnswer, self).__init__(parent)
        QWidget.__init__(self)
        self.setupUi(self)
        self.setMinimumWidth(680)


class Answer(QWidget, Ui_Answer):
    def __init__(self, parent=None):
        super(Answer, self).__init__(parent)
        QWidget.__init__(self)
        self.setupUi(self)
        self.setMinimumWidth(680)


class Chat(QtWidgets.QDialog, Ui_MainTry):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Добавляем поле для ввода IP-адреса
        self.ip_lineEdit = QtWidgets.QLineEdit(self)
        self.ip_lineEdit.setPlaceholderText("Введите IP-адрес")
        self.ip_lineEdit.setGeometry(10, 10, 200, 30)  # Установите нужные координаты и размер

        # Добавляем кнопку для подключения
        self.connect_pushButton = QtWidgets.QPushButton("Подключиться", self)
        self.connect_pushButton.setGeometry(220, 10, 100, 30)  # Установите нужные координаты и размер
        self.connect_pushButton.clicked.connect(self.connect_to_server)

        self.send_pushButton.clicked.connect(self.sendm)
        self.end_pushButton.clicked.connect(self.closed)
        self.reclineEdit.setHidden(True)
        self.reclineEdit.textChanged.connect(self.recMassage)
        self.image_pushButton.clicked.connect(self.sendi)
        self.reclineEditImg.setHidden(True)
        self.reclineEditImg.textChanged.connect(self.recImage)

        self.client_thread = None

    def closeEvent(self, event):
        # Вызываем метод закрытия
        self.closed()
        event.accept()  # Принять событие закрытия

    def connect_to_server(self):
        ip_address = self.ip_lineEdit.text()  # Получаем IP-адрес из текстового поля
        if ip_address:
            self.client_thread = clientThread(self, ip_address)  # Передаем IP-адрес в поток
            self.client_thread.start()  # Запускаем поток
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Введите IP-адрес")

    def closed(self):
        global stop_thread
        stop_thread = True
        if clientaa:
            clientaa.close()
        self.close()

    def sendm(self):
        global clientaa
        u_answer = UAnswer()
        u_answer.your_text_label.setText(str(self.sendtext_lineEdit.text()))
        if clientaa is not None:
            clientaa.send("massage".encode('utf-8'))
            massage = self.sendtext_lineEdit.text().encode('utf-8')
            clientaa.send(massage)
        item = QListWidgetItem()
        item.setSizeHint(u_answer.sizeHint())
        self.chatlistWidget.addItem(item)
        self.chatlistWidget.setItemWidget(item, u_answer)
        self.chatlistWidget.setMinimumWidth(u_answer.width())
        self.sendtext_lineEdit.setText("")
        self.chatlistWidget.setCurrentRow(self.chatlistWidget.count() - 1)

    def sendi(self):
        u_answer = UAnswer()
        path = QtWidgets.QFileDialog.getOpenFileName()[0]
        pixmap = QPixmap(path)

        small_pixmap = pixmap.scaled(200, 200, QtCore.Qt.KeepAspectRatio)
        u_answer.your_text_label.setPixmap(small_pixmap)

        size_img = os.path.getsize(path)

        if clientaa is not None:
            clientaa.send("image".encode('utf-8'))
            time.sleep(0.5)
            clientaa.send(f"{size_img}".encode('utf-8'))
            time.sleep(0.5)
            with open(path, 'rb') as file:
                image_data = file.read(size_img)
                clientaa.send(image_data)
        item = QListWidgetItem()
        item.setSizeHint(u_answer.sizeHint())
        self.chatlistWidget.addItem(item)
        self.chatlistWidget.setItemWidget(item, u_answer)
        self.chatlistWidget.setMinimumWidth(u_answer.width())
        u_answer.groupBox_3.setMaximumWidth(220)
        self.sendtext_lineEdit.setText("")
        self.chatlistWidget.setCurrentRow(self.chatlistWidget.count() - 1)

    def recMassage(self, text):
        answer = Answer()
        answer.yourfriend_text_label.setText(str(text))
        item = QListWidgetItem()
        item.setSizeHint(answer.sizeHint())
        self.chatlistWidget.addItem(item)
        self.chatlistWidget.setItemWidget(item, answer)
        self.chatlistWidget.setMinimumWidth(answer.width())
        self.chatlistWidget.setCurrentRow(self.chatlistWidget.count() - 1)

    def recImage(self):
        if os.path.isfile(f'Image{NumberImage}.jpg'):
            answer = Answer()
            pixmap = QPixmap(f'Image{NumberImage}.jpg')

            small_pixmap = pixmap.scaled(200, 200, QtCore.Qt.KeepAspectRatio)
            answer.yourfriend_text_label.setPixmap(small_pixmap)

            item = QListWidgetItem()
            item.setSizeHint(answer.sizeHint())
            self.chatlistWidget.addItem(item)
            self.chatlistWidget.setItemWidget(item, answer)
            self.chatlistWidget.setMinimumWidth(answer.width())
            answer.groupBox_2.setMaximumWidth(220)
            self.chatlistWidget.setCurrentRow(self.chatlistWidget.count() - 1)

class clientThread(Thread):
    def __init__(self, window, ip_address):
        Thread.__init__(self)
        self.window = window
        self.ip_address = ip_address

    def run(self):
        global NumberImage
        global clientaa, stop_thread
        while not stop_thread:
            clientaa = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            print('Waiting for connection response')

            try:
                clientaa.connect((self.ip_address, 1234))
                while True:
                    massage = clientaa.recv(1024)
                    clearM = massage.decode("utf-8")
                    if clearM == "massage":
                        massage = clientaa.recv(1024)
                        clearM = massage.decode("utf-8")
                        self.window.reclineEdit.setText(str(clearM))
                    elif clearM == "image":
                        NumberImage += 1
                        massage = clientaa.recv(1024)
                        clearM = massage.decode("utf-8")
                        size_img = int(clearM)
                        with open(f'Image{NumberImage}.jpg', "wb") as file:
                            image_chunk = clientaa.recv(size_img)
                            file.write(image_chunk)
                        self.window.reclineEditImg.setText(str(NumberImage))
            except socket.error as e:
                print(str(e))
            finally:
                if clientaa:
                    clientaa.close()  # Закрываем сокет при завершении работы

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = Chat()
    main_window.show()  # Сначала показываем главное окно
    sys.exit(app.exec_())
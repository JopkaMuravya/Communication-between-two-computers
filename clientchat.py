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
from _thread import *
clientaa = None
stop_thread = False
NumberImage = 0


class UAnswer(QWidget, Ui_Your_Answer):
    def __init__(self, parent=None):
        super(UAnswer, self).__init__(parent)
        QWidget.__init__(self)
        self.setupUi(self)

class Answer(QWidget, Ui_Answer):
    def __init__(self, parent=None):
        super(Answer, self).__init__(parent)
        QWidget.__init__(self)
        self.setupUi(self)

class Chat(QtWidgets.QDialog, Ui_MainTry):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.send_pushButton.clicked.connect(self.sendm)
        self.end_pushButton.clicked.connect(self.closed)
        self.reclineEdit.setHidden(True)
        self.reclineEdit.textChanged.connect(self.recMassage)
        self.image_pushButton.clicked.connect(self.sendi)
        self.reclineEditImg.setHidden(True)
        self.reclineEditImg.textChanged.connect(self.recImage)


    def closed(self):
        global stop_thread
        stop_thread = True
        self.close()

    def sendm(self):
        global clientaa
        u_answer = UAnswer()
        u_answer.your_text_label.setText(str(self.sendtext_lineEdit.text()))
        if clientaa != None:
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
        u_answer.your_text_label.setPixmap(pixmap)
        size_img = os.path.getsize(path)
        if clientaa != None:
            clientaa.send("image".encode('utf-8'))
            time.sleep(0.5)
            clientaa.send(f"{size_img}".encode('utf-8'))
            time.sleep(0.5)
            file = open(path, 'rb')
            image_data = file.read(size_img)
            clientaa.send(image_data)
            file.close()
        item = QListWidgetItem()
        item.setSizeHint(u_answer.sizeHint())
        self.chatlistWidget.addItem(item)
        self.chatlistWidget.setItemWidget(item, u_answer)
        self.chatlistWidget.setMinimumWidth(u_answer.width())
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
        self.chatlistWidget.setCurrentRow(self.chatlistWidget.count()-1)

    def recImage(self):
        answer = Answer()
        pixmap = QPixmap(f'Image{NumberImage}.jpg')
        answer.yourfriend_text_label.setPixmap(pixmap)
        self.test = QLabel()
        self.test.setPixmap(pixmap)
        self.test.resize(pixmap.width(), pixmap.height())
        self.test.move(625, 625)
        self.test.show()
        if os.path.isfile(f'Image{NumberImage}.jpg'):
            print(12334)
        item = QListWidgetItem()
        item.setSizeHint(answer.sizeHint())
        self.chatlistWidget.addItem(item)
        self.chatlistWidget.setItemWidget(item, answer)
        self.chatlistWidget.setMinimumWidth(answer.width())
        self.chatlistWidget.setCurrentRow(self.chatlistWidget.count() - 1)
        print(NumberImage)

class clientThread(Thread):
    def __init__(self, widow):
        Thread.__init__(self)
        self.window = widow

    def run(self):
        global NumberImage
        global clientaa, stop_thread
        while not stop_thread:
            if stop_thread == True: break
            clientaa = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            print('Waiting for connection response')

            try:
                clientaa.connect(("192.168.0.109", 12345))
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
                        file = open(f'Image{NumberImage}.jpg', "wb")
                        image_chunk = clientaa.recv(size_img)
                        file.write(image_chunk)
                        file.close()
                        self.window.reclineEditImg.setText(str(NumberImage))
            except socket.error as e:
                print(str(e))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = Chat()
    client = clientThread(main_window)
    stop_thread = False
    client.start()
    main_window.show()
    sys.exit(app.exec_())
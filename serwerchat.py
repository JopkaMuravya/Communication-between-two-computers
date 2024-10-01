from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QListWidgetItem, QWidget
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
server = None
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
        u_answer = UAnswer()
        u_answer.your_text_label.setText(str(self.sendtext_lineEdit.text()))
        if server != None:
            server.send("massage".encode('utf-8'))
            massage = self.sendtext_lineEdit.text().encode('utf-8')
            server.send(massage)
        item = QListWidgetItem()
        item.setSizeHint(u_answer.sizeHint())
        self.chatlistWidget.addItem(item)
        self.chatlistWidget.setItemWidget(item, u_answer)
        self.chatlistWidget.setMinimumWidth(u_answer.width())
        self.sendtext_lineEdit.setText("")
        self.chatlistWidget.setCurrentRow(self.chatlistWidget.count()-1)

    def sendi(self):
        u_answer = UAnswer()
        path = QtWidgets.QFileDialog.getOpenFileName()[0]
        pixmap = QPixmap(path)
        u_answer.your_text_label.setPixmap(pixmap)
        size_img = os.path.getsize(path)
        if server != None:
            server.send("image".encode('utf-8'))
            server.send(f"{size_img}".encode('utf-8'))
            file = open(path, 'rb')
            image_data = file.read(size_img)
            server.send(image_data)
            file.close()
        item = QListWidgetItem()
        item.setSizeHint(u_answer.sizeHint())
        self.chatlistWidget.addItem(item)
        self.chatlistWidget.setItemWidget(item, u_answer)
        self.chatlistWidget.setMinimumWidth(u_answer.width())
        self.sendtext_lineEdit.setText("")
        self.chatlistWidget.setCurrentRow(self.chatlistWidget.count() - 1)
        self.chatlistWidget.resize(pixmap.width(), pixmap.height())

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
        item = QListWidgetItem()
        item.setSizeHint(answer.sizeHint())
        self.chatlistWidget.addItem(item)
        self.chatlistWidget.setItemWidget(item, answer)
        self.chatlistWidget.setMinimumWidth(answer.width())
        self.chatlistWidget.setCurrentRow(self.chatlistWidget.count() - 1)


class serverThread(Thread):
    def __init__(self, widow):
        Thread.__init__(self)
        self.window = widow

    def run(self):
        global NumberImage
        global stop_thread
        while not stop_thread:
            if stop_thread == True: break
            clientaa = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            host = "10.193.160.160"
            port = 12345
            clientaa.bind(("10.193.160.160", 12345))
            print(' Socket is listening...')
            clientaa.listen(1)
            global server
            (server, (ip, pot)) = clientaa.accept()
            print('Connected to: ' + str(ip) + ':' + str(pot))
            while True:
                massage = server.recv(1024)
                clearM = massage.decode("utf-8")
                if clearM == "massage":
                    massage = server.recv(1024)
                    clearM = massage.decode("utf-8")
                    self.window.reclineEdit.setText(str(clearM))
                elif clearM == "image":
                    NumberImage += 1
                    massage = server.recv(1024)
                    clearM = massage.decode("utf-8")
                    size_img = int(clearM)
                    file = open(f'Image{NumberImage}.jpg', "wb")
                    image_chunk = server.recv(size_img)
                    file.write(image_chunk)
                    file.close()
                    self.window.reclineEditImg.setText(str(NumberImage))



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = Chat()
    server = serverThread(main_window)
    stop_thread = False
    server.start()
    main_window.show()
    sys.exit(app.exec_())

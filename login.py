import sys
from welcome import Switch
from PyQt5.QtNetwork import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class App(QWidget):
 
    def __init__(self):
        super().__init__()
        self.sock = QTcpSocket()
        self.udpSocket = QUdpSocket()
        self.account = {"admin": "admin", "user": "user", "luna": "luna"}
        self.title = 'Login Interface'
        self.width = 240
        self.height = 180
        self.isok = False
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle(self.title)
        self.resize(self.width, self.height)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.close)
        buttonBox.button(QDialogButtonBox.Ok).setDefault(True)
        buttonBox.button(QDialogButtonBox.Ok).setShortcut('Return')
        buttonBox.button(QDialogButtonBox.Cancel).setShortcut('Escape')

        self.createFormGroupBox()
        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.formGroupBox)
        windowLayout.addWidget(buttonBox)
        self.setLayout(windowLayout)

        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)
        self.show()

    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox('Login')
        layout = QFormLayout()
        self.handle = QLineEdit(self)
        self.password = QLineEdit(self)
        self.password.setEchoMode(QLineEdit.Password)
        layout.addRow(QLabel('Handle:'), self.handle)
        layout.addRow(QLabel('Password:'), self.password)
        self.formGroupBox.setLayout(layout)

    def connect(self):
        self.sock.connectToHost("192.168.1.100", 8888)
        self.udpSocket.bind(8080)
        print('UDP is listening port 8080')
        linkmessage = b'link start'
        if self.sock.isWritable():
            self.sock.write(linkmessage)
            # self.sock.write((nickName).encode())
            self.sock.readyRead.connect(self.slotreadyread)
        else:
            QMessageBox.warning(linkmessage, "Tips:", "Service Down", QMessageBox.Cancel)

    def slotreadyread(self):
        """
        收到服务器发来的数据处理
        """
        if self.sock.bytesAvailable() > 0:
            data = bytes(self.sock.readLine()).decode().rstrip()
            print("dialog recv  " + data)
            if data == 'link finish':

                if self.sock.isWritable():
                    self.sock.write(self.tmpName.encode())
                self.swi = Switch(self.tmpName, self.sock, self.udpSocket)
                self.swi.show()
                self.sock.readyRead.disconnect(self.slotreadyread)
                del self.sock
                print("Login Successfully!")
                self.close()


    def check(self):
        if self.handle.text() in self.account and self.password.text() == self.account[self.handle.text()]:
            self.isok = True
            self.tmpName = self.handle.text()
            # self.connect(self.handle.text())

    @pyqtSlot()
    def accept(self):
        self.check()
        if self.isok == True:
            # self.hide()
            self.connect()
            # self.swi = Switch(self.tmpName, self.sock)
            # self.swi.show()
            # del self.sock
            # print("Login Successfully!")
            # self.close()
        else:
            QMessageBox.question(self, 'Error', 'Incorrect Password!', QMessageBox.Ok)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())

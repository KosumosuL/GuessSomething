from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from clientWindow2 import Game
import sys

class Switch(QWidget):

    def __init__(self, nickName, socket, udpSocket):
        super().__init__()
        self.title = 'GUI Sample'
        self.width = 240
        self.height = 180
        self.nickName = nickName
        self.sock = socket
        self.udpSocket = udpSocket
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        # self.resize(self.width, self.height)

        windowLayout = QVBoxLayout()
        windowLayout.addStretch()
        pe = QPalette()
        pe.setBrush(self.backgroundRole(), QBrush(QPixmap('wallpaper.jpg')))
        self.setPalette(pe)
        self.setFixedSize(800, 480)

        hbox = QHBoxLayout()
        # game button
        gameButton = QPushButton('Start', self)
        gameButton.setFixedSize(100,50)
        gameButton.setToolTip('Switch to Game interface')
        gameButton.clicked.connect(self.g_click)
        hbox.addWidget(gameButton)
        windowLayout.addLayout(hbox)
        # help qmessage

        self.setLayout(windowLayout)

        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)
        self.show()


    @pyqtSlot()
    def g_click(self):
        self.hide()
        print(self.nickName)
        print(self.sock)
        print(self.udpSocket)
        self.game = Game(self.nickName)
        self.game.getSocket(self.sock, self.udpSocket)
        print(1)
        self.game.show()
        # self.game._signal.connect(self.re_show)
        print("ok")

    @pyqtSlot()
    def re_show(self):
        print("ok")
        if self.isVisible() == False:
            self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Switch()
    sys.exit(app.exec_())
from testPaint2 import *
# from testPaint import
from testWidgets import MsgList, BubbleText
from testGues import *
# from backup.testThread import *
from PyQt5.QtNetwork import QHostAddress

GAME_TIME = 20

class Game(QWidget):

    def __init__(self, nickName):
        super().__init__()
        self.title = 'Game Sample'
        self.nickName = nickName
        self.gameTime = GAME_TIME
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.onTimerOut)
        self.role = False        # True为绘画者
        self.gameTitle = " "
        self.width = 700
        self.height = 600
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        # self.resize(self.width, self.height)

        windowLayout = QHBoxLayout()
        tipLayoout = QHBoxLayout()
        leftLayout = QVBoxLayout()
        rightLayout = QVBoxLayout()
        sendLayout = QHBoxLayout()
        gameLayout = QVBoxLayout()

        # drawing board
        self.drawBoard = Canvas()
        drawBoardPalette = QPalette()
        drawBoardPalette.setColor(QPalette.WindowText, Qt.red)  # 设置字体颜色
        self.drawBoard.setAutoFillBackground(True)  # 设置背景充满，为设置背景颜色的必要条件
        drawBoardPalette.setColor(QPalette.Window, Qt.white)  # 设置背景颜色
        self.drawBoard.setPalette(drawBoardPalette)
        self.drawBoard.setFixedSize(500, 500)
        # tip board
        self.tipLabel = QLabel()
        tipLabelPalette = QPalette()
        tipLabelPalette.setColor(QPalette.WindowText, Qt.black)  # 设置字体颜色
        self.tipLabel.setAutoFillBackground(True)  # 设置背景充满，为设置背景颜色的必要条件
        tipLabelPalette.setColor(QPalette.Window, Qt.white)  # 设置背景颜色
        self.tipLabel.setPalette(tipLabelPalette)
        self.tipLabel.setFixedSize(370, 100)
        self.tipLabel.setAlignment(Qt.AlignCenter)
        self.tipLabel.setFont(QFont("Microsoft YaHei", 25, QFont.Normal))
        self.tipLabel.setText(u"题目")
        # chat board
        self.chatBoard = MsgList()
        self.chatBoard.setFixedSize(400, 550)
        # send text
        self.sendContent = QTextEdit()
        self.sendContent.setPlaceholderText("（＾∀＾●）ﾉｼ")
        self.sendContent.setFixedSize(330, 50)
        sendBtn = QPushButton("send")
        sendBtn.setToolTip('push to send message')
        sendBtn.clicked.connect(self.send_click)
        sendBtn.setFixedSize(50, 50)
        # LCDTimer
        self.lcd = QLCDNumber()
        self.lcd.setDigitCount(3)
        self.lcd.setMode(QLCDNumber.Dec)
        self.lcd.display(str(self.gameTime).zfill(3))
        self.lcd.setFixedSize(40, 100)
        self.lcd.setSegmentStyle(QLCDNumber.Flat)
        # nameLabel
        nameLabel = QLabel()
        tipLabelPalette = QPalette()
        tipLabelPalette.setColor(QPalette.WindowText, Qt.black)  # 设置字体颜色
        nameLabel.setAutoFillBackground(True)  # 设置背景充满，为设置背景颜色的必要条件
        tipLabelPalette.setColor(QPalette.Window, Qt.white)  # 设置背景颜色
        nameLabel.setPalette(tipLabelPalette)
        nameLabel.setFixedSize(50, 45)
        nameLabel.setAlignment(Qt.AlignCenter)
        nameLabel.setFont(QFont("Microsoft YaHei", 10, QFont.Normal))
        nameLabel.setText(self.nickName)
        # switch button
        self.swiBtn = QPushButton()
        self.swiBtn = QPushButton("ready")
        self.swiBtn.setToolTip('ready or next game')
        self.swiBtn.clicked.connect(self.swi_click)
        self.swiBtn.setFixedSize(50, 45)


        gameLayout.addWidget(nameLabel)
        gameLayout.addWidget(self.swiBtn)
        gameWidget = QWidget()
        gameWidget.setLayout(gameLayout)

        tipLayoout.addWidget(gameWidget)
        tipLayoout.addWidget(self.tipLabel)
        tipLayoout.addWidget(self.lcd)
        tipWidget = QWidget()
        tipWidget.setLayout(tipLayoout)

        leftLayout.addWidget(tipWidget)
        leftLayout.addWidget(self.drawBoard)
        leftWidget = QWidget()
        leftWidget.setLayout(leftLayout)

        sendLayout.addWidget(self.sendContent)
        sendLayout.addWidget(sendBtn)
        sendWidget = QWidget()
        sendWidget.setLayout(sendLayout)

        rightLayout.addWidget(self.chatBoard)
        rightLayout.addWidget(sendWidget)
        rightWidget = QWidget()
        rightWidget.setLayout(rightLayout)
        windowLayout.addWidget(leftWidget)
        windowLayout.addWidget(rightWidget)
        self.setLayout(windowLayout)

        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)
        self.show()

    # server返回开始后，变为gaming状态，设置tip和角色，开始计时
    def startGame(self, titleIdx=0, role=False):
        if self.swiBtn.text() == 'readying':
            self.swiBtn.setText('gaming')
            self.title = Title()
            self.role = role
            self.gameTitle = self.title.getTitle(titleIdx)
            if role == True:    # if you are painter
                self.tipLabel.setText(self.title.getTitle(titleIdx))
                self.drawBoard.setDisabled(False)
                self.drawBoard.setRole(role)
            else:
                self.tipLabel.setText(self.title.getTip(titleIdx))
                self.drawBoard.setDisabled(True)
                self.drawBoard.setRole(role)
            self.timer.start()


    def stopGame(self, message="nothing"):
        if self.swiBtn.text() == 'gaming':
            self.swiBtn.setText('next')
        QMessageBox.information(self, 'result', message, QMessageBox.Ok)

    def getSocket(self, socket, udpSocket):
        """从登录框中获取socket"""
        self.sock = socket
        self.udpSocket = udpSocket
        if self.sock.isWritable():
            self.sock.write('send'.encode())
        self.sock.readyRead.connect(self.slotreadyread)
        self.udpSocket.readyRead.connect(self.handleRecv)

    def handleRecv(self):
        if self.role == False:
            buf, ip, port = self.udpSocket.readDatagram(1024)
            message = buf.decode()
            print('Recv UDP: {}'.format(message))
            p = list(map(int, message.split('.')))
            print(p)
            if p[0] == -1 and p[1] == -1 and p[2] == -1:
                points = []
            else:
                points = self.drawBoard.getPoints()
            i = 0
            while(i < len(p) - 3):
                points.append(point(p[i], p[i + 1], p[i + 2]))
                i += 3
            self.drawBoard.setPoints(points)
            self.drawBoard.update()

    def handleSend(self):
        if self.role:
            points = self.drawBoard.getPoints()
            text = str(point(-1, -1, -1))
            for i in range(len(points)):
                if len(text) > 0:
                    text += "."
                text += str(points[i])
                if i == len(points) - 1 or len(text) > 950:
                    message = bytes(text, encoding="utf-8")
                    print(message)
                    self.udpSocket.writeDatagram(message, QHostAddress("224.0.0.1"), 8080)
                    text = ""

    def slotreadyread(self):
        """接受socket数据处理函数"""
        while self.sock.bytesAvailable() > 0:
            data = bytes(self.sock.readLine()).decode().rstrip()
            print("chat room recv: " + data)        #data: role:message

            try:
                # chat message
                head, junk, data = data.partition(":")
                if head == "message":   # message:name:message
                    print("say: " + data)               #data: name:message
                    name, junk, message = data.partition(":")
                    self.chatBoard.addTextMsg(name, message, True)      #from ${nickname}
                # system broadcast
                elif head == "broadcast":
                    print("sys:  " + data)
                    self.chatBoard.addTextMsg("system", data, True)      # from "system"
                # game start
                elif head == "start":
                    print("start message: " + data)     # data: titleIdx.role
                    titleIdx = int(data.split('.')[0])
                    role = (data.split('.')[1] == self.nickName)
                    self.startGame(titleIdx, role)
                # game stop
                elif head == "stop":
                    print("stop message: " + data)
                    self.stopGame(data)
            except Exception:
                print("unexpected data: " + data)

    def send(self, message):
        # print(message + "   is sent")
        if self.sock.isWritable():
            self.sock.write(message.encode())
        # print("send finish")


    @pyqtSlot()
    def send_click(self):
        sendMessage = self.sendContent.toPlainText()
        # print(sendMessage)

        if sendMessage != "":
            # check answer
            if self.role == False and sendMessage == self.gameTitle:
                self.send(self.nickName + ':right')
            else:
                self.send(sendMessage)
            buble = BubbleText(sendMessage, False)
            self.sendContent.clear()
            self.chatBoard.addTextMsg(self.nickName, sendMessage, False)

    @pyqtSlot()
    def onTimerOut(self):
        self.gameTime = self.gameTime - 1
        self.lcd.display(str(self.gameTime).zfill(3))
        self.handleSend()

        if self.gameTime == 0:
            self.timer.stop()
            self.send(self.nickName + ':timeout')

    @pyqtSlot()
    def swi_click(self):
        if self.swiBtn.text() == 'ready' or self.swiBtn.text() == 'next':
            # 点击ready时界面清空，计时器回归，状态变为readying，向server发送信息
            self.gameTime = GAME_TIME
            self.lcd.display(str(self.gameTime).zfill(3))
            self.tipLabel.clear()
            self.drawBoard.clear()
            self.chatBoard.clear()
            self.swiBtn.setText('readying')
            self.send(self.nickName + ':readying')

    @pyqtSlot()
    def re_show(self):
        if self.isVisible() == False:
            self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Game("ano")
    sys.exit(app.exec_())

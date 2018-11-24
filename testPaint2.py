import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from copy import deepcopy
import qtawesome

class point():
    def __str__(self):
        return "%s.%s.%s" % (self.x, self.y, self.color)

    def __init__(self, x, y, color=2):
        super(point, self).__init__()
        self.x = x
        self.y = y
        self.color = color

class Canvas(QWidget):

    def __init__(self, height=500, width=500):
        super(Canvas, self).__init__()

        # resize设置宽高，move设置位置
        self.height = height
        self.width = width
        self.resize(self.height, self.width)
        # self.move(100, 100)
        # self.setWindowTitle("不简单的画板1.0")

        # 初始化颜色、线宽和线型
        self.color = 2
        self.lineWidth = 2
        self.line = Qt.SolidLine

        # 是否可以操作
        self.role = True

        # setMouseTracking设置为False，否则不按下鼠标时也会跟踪鼠标事件
        self.setMouseTracking(False)

        # 撤销按钮
        self.revokeButton = QPushButton(qtawesome.icon('fa.undo', color='grey'), '', self)
        self.revokeButton.move(450, 0)
        self.revokeButton.clicked.connect(self.revoke)

        # 清空按钮
        self.refreshButton = QPushButton(qtawesome.icon('fa.refresh', color='grey'), '', self)
        self.refreshButton.move(450, 20)
        self.refreshButton.clicked.connect(self.refresh)

        # 颜色
        self.colorButton = QPushButton('', self)
        self.colorButton.move(450, 40)
        self.colorButton.clicked.connect(self.setPenColor)
        self.colorButton.setIcon(qtawesome.icon('fa.circle', color=QColor(self.color)))

        # points是记录所有点坐标的list
        self.points = [point(-1, -1, self.color)]

    def paintEvent(self, event):
        qp = QPainter(self)
        '''
        首先判断points列表中是不是至少有两个点了
        然后将points中第一个点赋值给point_start
        利用中间变量point_now遍历整个points列表
        point_end = point_now

        判断point_end是否是断点，如果是
        point_start赋值为断点
        continue
        判断point_start是否是断点，如果是
        point_start赋值为point_end
        continue

        画point_start到point_end之间的线
        point_start = point_end
        这样，不断地将相邻两个点之间画线，就能留下鼠标移动轨迹了
        '''
        if len(self.points):
            point_start = self.points[0]
            for point_end in self.points:
                if point_start.x != -1 and point_end.x != -1:
                    qp.drawLine(point_start.x, point_start.y, point_end.x, point_end.y)
                elif point_start.x == -1:
                    qp.setPen(QPen(QColor(point_start.color), self.lineWidth, self.line))
                point_start = point_end

    def mouseMoveEvent(self, event):
        '''
        重写(按住)鼠标移动事件
        将当前点point_now添加到points列表中
        调用update()函数在这里相当于调用paintEvent()函数
        '''
        if self.role:
            # 中间变量point_now提取当前点
            point_now = point(event.pos().x(), event.pos().y(), self.color)
            if point_now.x >= 0 and point_now.x <= self.width and point_now.y >=0 and point_now.y <= self.height or len(self.points) > 1 and self.points[-1].x >= 0 and point_now.x != -1:
                # point_now添加到self.points中
                self.points.append(point_now)
                self.update()

    def mouseReleaseEvent(self, event):
        '''
        重写松开鼠标的事件
        在每次松开后向points列表中添加一个断点(-1, -1)
        '''
        if self.role:
            if len(self.points) > 1 and self.points[-1].x != -1:
                self.points.append(point(-1, -1, self.color))

    def clear(self):
        self.points.clear()
        self.points.append(point(-1, -1, self.color))
        self.update()

    @pyqtSlot()
    def revoke(self):
        if self.role:
            if len(self.points) > 1:
                del self.points[-1]
                while len(self.points) and self.points[-1].x != -1:
                    del self.points[-1]
                self.points[-1] = point(-1, -1, self.color)
                self.update()

    @pyqtSlot()
    def refresh(self):
        if self.role:
            self.points.clear()
            self.points.append(point(-1, -1, self.color))
            self.update()

    def setRole(self, r):
        self.role = r

    @pyqtSlot()
    def setPenColor(self):
        if self.role:
            c = QColorDialog.getColor()
            if c.isValid():
                self.color = int(c.name()[1:], base=16)
                self.colorButton.setIcon(qtawesome.icon('fa.circle', color=QColor(self.color)))
                self.points[-1] = point(-1, -1, self.color)
                self.update()

    def setPoints(self, p):
        self.points = p
        self.update()

    def getPoints(self):
        return deepcopy(self.points)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Canvas()
    ex.show()
    sys.exit(app.exec_())
import sys
from login import App
from welcome import Switch
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
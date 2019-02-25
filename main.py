import sys
from PyQt5 import QtCore, QtGui, QtWidgets

import qtCreatorProject.MP3Player.mp3PlayerGUI

class Mp3Player(QtWidgets.QMainWindow, qtCreatorProject.MP3Player.mp3PlayerGUI.Ui_mainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

    def add(self):
        for i in range(10):
            item = QtWidgets.QListWidgetItem("Item %i" % i)
            self.listWidget.addItem(item)

def main():
    app = QtWidgets.QApplication(sys.argv)
    form = Mp3Player()
    form.show()
    form.add()
    app.exec_()

if __name__ == '__main__':
    main()
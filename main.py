from PyQt5 import QtCore, QtGui, QtWidgets #
import sys

import qtCreatorProject.MP3Player.mp3PlayerGUI

class Mp3Player(QtWidgets.QMainWindow, qtCreatorProject.MP3Player.mp3PlayerGUI.Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)

def main():
    app = QtWidgets.QApplication(sys.argv)
    form = Mp3Player()
    form.show()
    app.exec_()


if __name__ == '__main__':
    main()
import sys
from os import walk
from PyQt5 import QtCore, QtGui, QtWidgets

import qtCreatorProject.MP3Player.mp3PlayerGUI

class Mp3Player(QtWidgets.QMainWindow, qtCreatorProject.MP3Player.mp3PlayerGUI.Ui_mainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.setupActions()

    def setupActions(self):
        self.actionFile.triggered.connect(self.handleActionFile)
        self.actionSearch.triggered.connect(self.handleActionSearch)

    def handleActionFile(self):
        path = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.directoryLabel.setText(path)
        f = []
        for (dirpath, dirnames, filenames) in walk(path):
            files = [fi for fi in filenames if fi.endswith(".mp3")]
            f.extend(files)
            break

        for file in f:
            item = QtWidgets.QListWidgetItem(file)
            self.listWidget.addItem(item)

    def handleActionSearch(self):
        print("handle search")

def main():
    app = QtWidgets.QApplication(sys.argv)
    form = Mp3Player()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
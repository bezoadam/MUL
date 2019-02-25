import sys
import os
import vlc
from os import walk, path
from PyQt5 import QtCore, QtGui, QtWidgets

import qtCreatorProject.MP3Player.mp3PlayerGUI

class Mp3Player(QtWidgets.QMainWindow, qtCreatorProject.MP3Player.mp3PlayerGUI.Ui_mainWindow):
    valueChanged = QtCore.pyqtSignal(int)
    instance = vlc.Instance()
    player = instance.media_player_new()

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.setupActions()
        self.setupValueChanged()

    def setupActions(self):
        self.actionFile.triggered.connect(self.handleActionFile)
        self.actionSearch.triggered.connect(self.handleActionSearch)
        self.playButton.clicked.connect(self.handlePlayButton)
        self.stopButton.clicked.connect(self.handleStopButton)
        self.previousButton.clicked.connect(self.handlePreviousButton)
        self.nextButton.clicked.connect(self.handleNextButton)

    def setupValueChanged(self):
        self.volumeProgressBar.valueChanged.connect(self.handleProgressBarValue)
        self.volumeDial.valueChanged.connect(self.volumeProgressBar.setValue)
        self.volumeDial.valueChanged.connect(self.valueChanged)

    def handleActionFile(self):
        path = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        if os.path.isdir(path):
            self.listWidget.clear()
            self.directoryLabel.setText(path)
            f = []
            for (dirpath, dirnames, filenames) in walk(path):
                files = [fi for fi in filenames if fi.endswith(".mp3")]
                f.extend(files)
                break

            for file in sorted(f):
                item = QtWidgets.QListWidgetItem(file)
                self.listWidget.addItem(item)

    def handleActionSearch(self):
        print("handle search")

    def handleProgressBarValue(self, value):
        self.volumeLabel.setText(str(value))

    def handlePlayButton(self):
        currentItem = self.listWidget.currentItem()
        if currentItem is not None:
            songName = currentItem.text()
            songNamePath = self.directoryLabel.text().title() + "/" + songName
            print(songNamePath)
            media = self.instance.media_new(songNamePath)
            self.player.set_media(media)
            self.player.play()

    def handleStopButton(self):
        self.player.stop()

    def handlePreviousButton(self):
        pass

    def handleNextButton(self):
        pass

def main():
    app = QtWidgets.QApplication(sys.argv)
    form = Mp3Player()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
import sys
import os
import vlc
import time
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
        self.muteButton.clicked.connect(self.handleMuteButton)

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
        self.player.audio_set_volume(value)
        self.volumeLabel.setText(str(value))

    def handlePlayButton(self):
        currentItem = self.listWidget.currentItem()
        if currentItem is not None:
            songName = currentItem.text()
            print(songName)
            self.songNameLabel.setText(songName)
            self.songNameLabel.repaint()
            songNamePath = self.directoryLabel.text().title() + "/" + songName
            media = self.instance.media_new(songNamePath)
            self.player.set_media(media)
            self.player.play()
            initialVolume = self.volumeLabel.text()
            self.player.audio_set_volume(int(initialVolume))

            duration = self.player.get_length() / 1000
            mm, ss = divmod(duration, 60)

            print ("Current song is : ", songName, "Length:", "%02d:%02d" % (mm, ss))

    def handleStopButton(self):
        print(self.player.get_length())
        self.songNameLabel.setText("")
        self.songNameLabel.repaint()
        self.player.stop()

    def handleMuteButton(self):
        self.player.audio_toggle_mute()
        iconPath = "icon/unmute.png" if self.player.audio_get_mute() else "icon/mute.png"
        self.muteButton.setIcon(QtGui.QIcon(iconPath))
        self.muteButton.repaint()

    def handlePreviousButton(self):
        currentIndex = self.listWidget.currentIndex()
        if not currentIndex.row() == 0:
            self.listWidget.setCurrentRow(currentIndex.row() - 1)
            self.listWidget.repaint()
            self.handlePlayButton()
    def handleNextButton(self):
        currentIndex = self.listWidget.currentIndex()
        if not currentIndex.row() + 1 > self.listWidget.count() - 1:
            self.listWidget.setCurrentRow(currentIndex.row() + 1)
            self.listWidget.repaint()
            self.handlePlayButton()

def main():
    app = QtWidgets.QApplication(sys.argv)
    form = Mp3Player()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
import sys
import os
import vlc
import time
import threading
from random import randint
from os import walk, path
from PyQt5 import QtCore, QtGui, QtWidgets

import qtCreatorProject.MP3Player.mp3PlayerGUI

class JumpSlider(QtWidgets.QSlider):

    def __init__(self, widget, player):
        self.player = player
        QtWidgets.QSlider.__init__(self, widget)

    def mousePressEvent(self, ev):
        """ Jump to click position """
        newValue = QtWidgets.QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), ev.x(), self.width())
        self.player.set_time(newValue * 1000)

    def mouseMoveEvent(self, ev):
        """ Jump to pointer position while moving """
        newValue = QtWidgets.QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), ev.x(), self.width())
        self.player.set_time(newValue * 1000)

class Mp3Player(QtWidgets.QMainWindow, qtCreatorProject.MP3Player.mp3PlayerGUI.Ui_mainWindow):
    valueChanged = QtCore.pyqtSignal(int)
    sliderUpdated = QtCore.pyqtSignal(int)
    instance = vlc.Instance()
    player = instance.media_player_new()
    songsLoaded = False
    f_stop = threading.Event()
    songDuration = None

    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self)
        self.setupCustomSlider()
        self.setupActions()
        self.setupValueChanged()
        self.mockMp3()

    #TODO Delete this
    def mockMp3(self):
        path = "mp3/"
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

            self.songsLoaded = True

    def setupActions(self):
        self.actionFile.triggered.connect(self.handleActionFile)
        self.actionSearch.triggered.connect(self.handleActionSearch)
        self.actionPlay.triggered.connect(self.handlePlayButton)
        self.actionStop.triggered.connect(self.handleStopButton)
        self.actionPrevious.triggered.connect(self.handlePreviousButton)
        self.actionNext.triggered.connect(self.handleNextButton)
        self.actionShuffle.triggered.connect(self.handleShuffleButton)
        self.actionMute.triggered.connect(self.handleMuteButton)
        self.playButton.clicked.connect(self.handlePlayButton)
        self.stopButton.clicked.connect(self.handleStopButton)
        self.previousButton.clicked.connect(self.handlePreviousButton)
        self.nextButton.clicked.connect(self.handleNextButton)
        self.muteButton.clicked.connect(self.handleMuteButton)
        self.shuffleButton.clicked.connect(self.handleShuffleButton)

    def setupValueChanged(self):
        self.volumeProgressBar.valueChanged.connect(self.handleProgressBarValue)
        self.volumeDial.valueChanged.connect(self.volumeProgressBar.setValue)
        self.volumeDial.valueChanged.connect(self.valueChanged)

    def setupCustomSlider(self):
        self.slider = JumpSlider(self.centralWidget, self.player)
        self.slider.setGeometry(QtCore.QRect(20, 300, 281, 22))
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setObjectName("slider")
        self.sliderUpdated.connect(self.updateSliderValue)

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

            self.songsLoaded = True

    def handleActionSearch(self):
        print("handle search")

    def handleProgressBarValue(self, value):
        self.player.audio_set_volume(value)
        self.volumeLabel.setText(str(value))

    def handlePlayButton(self):
        if not self.songsLoaded:
            return
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
            self.songDuration = None
            initialVolume = self.volumeLabel.text()
            self.player.audio_set_volume(int(initialVolume))
            self.sliderUpdated.emit(0)
            self.f_stop.clear()
            self.f(self.f_stop)

    def handleStopButton(self):
        if not self.songsLoaded:
            return
        self.songNameLabel.setText("")
        self.songNameLabel.repaint()
        self.sliderUpdated.emit(0)
        self.player.stop()
        self.f_stop.set()

    def handleMuteButton(self):
        self.player.audio_toggle_mute()
        iconPath = "icon/unmute.png" if self.player.audio_get_mute() else "icon/mute.png"
        self.muteButton.setIcon(QtGui.QIcon(iconPath))
        self.muteButton.repaint()

    def handlePreviousButton(self):
        if not self.songsLoaded:
            return
        currentIndex = self.listWidget.currentIndex()
        if not currentIndex.row() == 0:
            self.listWidget.setCurrentRow(currentIndex.row() - 1)
            self.listWidget.repaint()
            self.handlePlayButton()
    def handleNextButton(self):
        if not self.songsLoaded:
            return
        currentIndex = self.listWidget.currentIndex()
        if not currentIndex.row() + 1 > self.listWidget.count() - 1:
            self.listWidget.setCurrentRow(currentIndex.row() + 1)
            self.listWidget.repaint()
            self.handlePlayButton()

    def handleShuffleButton(self):
        randomNumber = randint(0, self.listWidget.count() - 1)
        self.listWidget.setCurrentRow(randomNumber)
        self.listWidget.repaint()
        self.handlePlayButton()

    def updateSliderValue(self, value):
        self.slider.setValue(value)

    def f(self, f_stop):
        if self.player.is_playing():
            if self.songDuration is None:
                length = self.player.get_length()
                self.songDuration = length * 0.001
                self.slider.setMaximum(int(self.songDuration))
            elapsedTime = self.player.get_time() * 0.001
            self.sliderUpdated.emit(elapsedTime)
            if abs(self.songDuration - elapsedTime) < 2.0:
                self.handleNextButton()
        if not f_stop.is_set():
            threading.Timer(1, self.f, [f_stop]).start()

def main():
    app = QtWidgets.QApplication(sys.argv)
    form = Mp3Player()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()
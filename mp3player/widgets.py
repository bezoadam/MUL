import os
from io import BytesIO
from collections import OrderedDict
import math
from typing import Dict, Set, List
import threading
import random

import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TPE1, TIT2, TRCK, TALB, APIC, TORY, TCON, COMM
from PyQt5 import QtWidgets, uic, Qt, QtGui
import vlc


class JumpSlider(QtWidgets.QSlider):
	def __init__(self, *args):
		QtWidgets.QSlider.__init__(self, *args)

	def mousePressEvent(self, e):
		self.handleEvent(e)

	def mouseMoveEvent(self, e):
		self.handleEvent(e)

	def mouseReleaseEvent(self, e):
		self.handleEvent(e)

	def handleEvent(self, e):
		self.setSliderPosition(int(self.minimum() + ((self.maximum() - self.minimum()) * e.x()) / float(self.width())))

	def handleValueChanged(self, x):
		self.mainWindow.updateVolumeFromSlider()

	def setup(self, mainWindow):
		self.mainWindow = mainWindow
		self.valueChanged.connect(self.handleValueChanged)


class VolumeSlider(JumpSlider):
	def __init__(self, *args):
		super(JumpSlider, self).__init__(*args)

	def handleValueChanged(self, x):
		self.mainWindow.updateVolumeFromSlider()


class TimeSlider(JumpSlider):
	def __init__(self, *args):
		super(JumpSlider, self).__init__(*args)

	def handleValueChanged(self, x):
		self.mainWindow.updateTimeFromSlider()


class MP3Tag(QtWidgets.QTableWidgetItem):
	def __init__(self, mp3file, tagIdentifier, text):
		super(QtWidgets.QTableWidgetItem, self).__init__(text)
		self.mp3file = mp3file

	def getMP3File(self):
		return self.mp3file


class MP3File(object):
	property_2_name: OrderedDict = OrderedDict({
		"fileName": "Soubor",  # Not tag, just for general usage
		"songName": "Jméno písně",
		"artist": "Umělec",
		"album": "Album",
		"track": "Stopa",
		"year": "Rok",
		"genre": "Žánr",
		"comment": "Komentář",
		"cover": "Obal",
	})
	coverExtensions = ["jpg", "jpeg", "gif", "png"]

	def __init__(self, path):
		super(object, self).__init__()

		self.path = path
		self.baseDir = os.path.dirname(self.path)
		self.baseName = os.path.basename(self.path)
		self.property_2_tag: OrderedDict = OrderedDict({
			"fileName": "PATH",  # Not tag, just for general usage
			"songName": "TIT2",
			"artist": "TPE1",
			"album": "TALB",
			"track": "TRCK",
			"year": "TORY",
			"genre": "TCON",
			"comment": "COMM",
			"cover": "APIC",
		})

		self.tag_2_property: OrderedDict = OrderedDict({
			"PATH": "fileName",  # Not tag, just for general usage
			"TIT2": "songName",
			"TPE1": "artist",
			"TALB": "album",
			"TRCK": "track",
			"TORY": "year",
			"TCON": "genre",
			"COMM": "comment",
			"APIC": "cover",
		})

		self.initColumns()

		self.reloadTagsFromFile()

	def reloadCoverImage(self):
		self.image = None

		audio = MP3(self.path, ID3=ID3)
		for key in audio.keys():
			for tag in self.tag_2_property:
				if tag in key:
					if tag == "APIC":
						self.loadCoverImageFromBytes(audio.tags.get(key).data)

	def loadCoverImageFromBytes(self, bytes):
		self.imageBytes = bytes
		self.image = QtGui.QPixmap.fromImage(QtGui.QImage.fromData(self.imageBytes))

	def removeCoverImage(self):
		audio = MP3(self.path, ID3=ID3)
		keys = list(audio.keys())
		for key in reversed(keys):
			if "APIC" in key:
				audio.pop(key, None)
		audio.save()
		del audio
		self.imageBytes = None
		self.image = None

	def reloadTagsFromFile(self):
		self.fileName.setText(self.baseName)

		audio = MP3(self.path, ID3=ID3)

		for key in audio.keys():
			for tag in self.tag_2_property:
				if tag in key:
					if tag == "APIC":
						self.loadCoverImageFromBytes(audio.tags.get(key).data)
					else:
						self.getAttr(self.tag_2_property[tag]).setText(str(audio[tag].text[0]))

		self.songLength = int(audio.info.length)
		self.songBitrate = audio.info.bitrate

		del audio

	def saveTag(self, propertyName, propertyValue):
		if propertyName == "fileName":
			self.rename(propertyValue)
		elif propertyName == "cover":
			self.saveCover(propertyValue)
		else:
			audio = MP3(self.path, ID3=ID3)
			tag = self.property_2_tag[propertyName]
			audio[tag] = getattr(mutagen.id3, tag)(encoding=3, text=propertyValue)
			audio.save()
			del audio

		self.getAttr(propertyName).setText(str(propertyValue))

	def initColumns(self):
		self.imageBytes = None
		self.image = None
		for key in self.property_2_tag:
			self.setAttr(key, MP3Tag(self, key, ""))

	def getAttr(self, attrName):
		return self.__getattribute__(attrName)

	def setAttr(self, attrName, value):
		self.__setattr__(attrName, value)

	def canRename(self, newPath):
		return not os.path.exists(os.path.join(self.baseDir, newPath)) or newPath == self.baseName

	def rename(self, newPath):
		if newPath != self.baseName:
			os.renames(os.path.join(self.baseDir, self.baseName), os.path.join(self.baseDir, newPath))
			self.baseName = newPath
			self.path = os.path.join(self.baseDir, self.baseName)

	def hasCover(self):
		for key in self.tag_2_property:
			if "APIC" in key:
				return True
		return False

	def saveCover(self, coverPath):
		# Init audio
		audio = MP3(self.path, ID3=ID3)

		# Remove cover images (do not remove cover if there's cover and coverPath is not set properly)
		if coverPath != "" or not self.hasCover():
			keys = list(audio.keys())
			for key in reversed(keys):
				if "APIC" in key:
					audio.pop(key, None)

		if coverPath != "":
			extension = coverPath.split(".")[-1].lower()
			if extension == "jpg":
				extension = "jpg"
			mime = "image/" + extension

		if coverPath != "":
			with open(coverPath, "rb") as coverFile:
				img = coverFile.read()
				audio['APIC'] = APIC(
					encoding=3,
					mime=mime,
					type=3,
					data=img
				)
				self.loadCoverImageFromBytes(img)
		audio.save()
		del audio


class MP3Table(QtWidgets.QTableWidget):
	HEADER_CHECK_EMPTY = "[_]"
	HEADER_CHECK_CHECKED = "[X]"

	def __init__(self, *args):
		super(QtWidgets.QTableWidget, self).__init__(*args)

	def setup(self, mainWindow):
		self.mainWindow = mainWindow
		self.createHeaders()
		self.horizontalHeader().sectionClicked.connect(self.handleHeaderClicked)
		self.horizontalHeader().sortIndicatorChanged.connect(self.handleSort)
		self.cellClicked.connect(self.handleCellClick)
		self.lastSelectedRow = None
		self.lastOrderedColumn = None
		self.lastOrder = None
		self.checkedRows: List = list()

	def isEmpty(self):
		return self.rowCount() == 0

	def checkedRowsCount(self):
		return len(self.checkedRows)

	def getMP3File(self, row):
		return self.item(row, 1).mp3file

	def handleCellClick(self, row, col):
		if col > 0:
			rows = [i.topRow() for i in self.selectedRanges() if i.rightColumn() - i.leftColumn() > 0]
			if len(rows) == 1:
				self.lastSelectedRow = rows[0]
				self.mainWindow.handleRowClicked(self.lastSelectedRow)
		if col == 0:
			self.toggleRow(row)

			self.selectRow()

	def handleSort(self, logicalIndex, eSort):
		if logicalIndex != 0:
			self.horizontalHeader().setSortIndicator(logicalIndex, eSort)

			rows = [i.topRow() for i in self.selectedRanges() if i.rightColumn() - i.leftColumn() > 0]
			if len(rows) == 1 and self.lastSelectedRow is not None:
				self.selectRow(rows[0])

		# QtWidgets.QHeaderView.set
		# self.horizontalHeader().setSortIndicator(0, self.model().sortOrder())

	def selectRow(self, row=None):
		self.lastSelectedRow = self.lastSelectedRow if row is None else row
		self.setRangeSelected(QtWidgets.QTableWidgetSelectionRange(0, 0, self.rowCount() - 1, self.columnCount() - 1), False)
		if self.lastSelectedRow is not None:
			self.setRangeSelected(QtWidgets.QTableWidgetSelectionRange(self.lastSelectedRow, 0, self.lastSelectedRow, self.columnCount() - 1), True)

	def selectNextRow(self, deterministic_next=True):
		if not self.isEmpty():
			if self.lastSelectedRow is None:
				self.lastSelectedRow = 0 if deterministic_next else random.randint(0, self.rowCount() - 1)
			else:
				self.lastSelectedRow = (self.lastSelectedRow + 1) % self.rowCount() if deterministic_next else (self.lastSelectedRow + random.randint(0, self.rowCount() - 1)) % self.rowCount()

			self.selectRow()
			self.mainWindow.handleRowClicked(self.lastSelectedRow)

	def selectPreviousRow(self, deterministic_next=True):
		if not self.isEmpty():
			if self.lastSelectedRow is None:
				self.lastSelectedRow = 0 if deterministic_next else random.randint(0, self.rowCount() - 1)
			else:
				self.lastSelectedRow = (self.lastSelectedRow - 1) % self.rowCount() if deterministic_next else (self.lastSelectedRow + random.randint(0, self.rowCount() - 1)) % self.rowCount()

			self.selectRow()
			self.mainWindow.handleRowClicked(self.lastSelectedRow)

	def unCheckRow(self, row):
		item = self.item(row, 0)
		if item in self.checkedRows:
			self.checkedRows.remove(item)
		item.setCheckState(Qt.Qt.Unchecked)

		self.updateCheckHeader()
		self.mainWindow.updateFilesPickedLabel()

	def checkRow(self, row):
		item = self.item(row, 0)
		if item not in self.checkedRows:
			self.checkedRows.append(item)
		item.setCheckState(Qt.Qt.Checked)

		self.updateCheckHeader()
		self.mainWindow.updateFilesPickedLabel()

	def toggleRow(self, row):
		item = self.item(row, 0)
		if item not in self.checkedRows:
			self.checkRow(row)
		else:
			self.unCheckRow(row)

		self.updateCheckHeader()

	def checkAllRows(self):
		for i in range(self.rowCount()):
			self.checkRow(i)

	def unCheckAllRows(self):
		for i in range(self.rowCount()):
			self.unCheckRow(i)

	def removeCheckedMP3Files(self):
		for item in sorted(self.checkedRows, key=lambda x: x.row(), reverse=True):
			self.removeMP3(item.row())

	def removeMP3(self, row):
		# TODO make it better
		if row < self.rowCount():
			if self.lastSelectedRow is not None and self.lastSelectedRow == row:
				if self.rowCount() == 1:
					self.lastSelectedRow = None
				elif self.rowCount() - 1 <= row:
					self.lastSelectedRow -= 1
				self.unCheckRow(row)
				self.removeRow(row)
				self.selectRow()
				self.mainWindow.handleRowClicked(self.lastSelectedRow)
			else:
				self.unCheckRow(row)
				self.removeRow(row)

	def updateCheckHeader(self):
		if self.checkedRowsCount() == self.rowCount():
			self.horizontalHeaderItem(0).setText(self.HEADER_CHECK_CHECKED)
		else:
			self.horizontalHeaderItem(0).setText(self.HEADER_CHECK_EMPTY)

	def createHeaders(self):
		header_labels = [self.HEADER_CHECK_EMPTY] + [j for (i, j) in MP3File.property_2_name.items() if i != "cover"]
		self.setColumnCount(len(header_labels))
		self.setHorizontalHeaderLabels(header_labels)
		self.setFocusPolicy(Qt.Qt.NoFocus)
		self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
		self.setColumnWidth(0, 20)

	def addMP3(self, mp3file):
		rowCount = self.rowCount()
		self.insertRow(rowCount)
		checkBoxHeader = QtWidgets.QTableWidgetItem()
		checkBoxHeader.setFlags(Qt.Qt.ItemIsUserCheckable | Qt.Qt.ItemIsEnabled)
		checkBoxHeader.setCheckState(Qt.Qt.Unchecked)
		checkBoxHeader.setTextAlignment(Qt.Qt.AlignCenter)
		self.setItem(rowCount, 0, checkBoxHeader)
		for idx, key in enumerate(mp3file.property_2_tag):
			if key != "cover":
				self.setItem(rowCount, idx + 1, mp3file.getAttr(key))

	def reorderItems(self):
		if self.lastOrderedColumn is None or self.lastOrder is None:
			self.horizontalHeader().setSortIndicatorShown(False)
		else:
			self.horizontalHeader().setSortIndicatorShown(True)
			self.horizontalHeader().setSortIndicator(self.lastOrderedColumn, self.lastOrder)
			self.sortItems(self.lastOrderedColumn, order=self.lastOrder)

	def sortItems(self, column, order=Qt.Qt.AscendingOrder):
		self.lastOrderedColumn = column
		self.lastOrder = order
		super().sortItems(column, order=order)

	def handleHeaderClicked(self, column):
		# If checkbox is clicked
		if column == 0:
			if self.checkedRowsCount() == self.rowCount():
				self.unCheckAllRows()
			else:
				self.checkAllRows()
			self.reorderItems()
		else:
			self.horizontalHeader().setSortIndicatorShown(True)
			if self.horizontalHeader().sortIndicatorOrder() == Qt.Qt.AscendingOrder:
				self.horizontalHeader().setSortIndicator(column, Qt.Qt.AscendingOrder)
				self.sortItems(column, order=Qt.Qt.AscendingOrder)
			else:
				self.horizontalHeader().setSortIndicator(column, Qt.Qt.DescendingOrder)
				self.sortItems(column, order=Qt.Qt.DescendingOrder)


class MP3Player(QtWidgets.QMainWindow):
	# Play state
	PLAYING = 0
	STOPPED = 1
	PAUSED = 2

	# Shuffle state
	SHUFFLE = 0
	UNSHUFFLE = 1

	# Mute state
	MUTE = 0
	UNMUTE = 1

	def __init__(self):
		self.app = QtWidgets.QApplication([])
		super(QtWidgets.QMainWindow, self).__init__()

		uiFile = "ui/new_window.ui"
		with open(uiFile) as f:
			uic.loadUi(f, self)

		self.propertyInit()

		self.setupHandlers()

		self.setupCustomWidgets()

	def propertyInit(self):
		# Window state
		self.closed = False

		# Player states
		self.playState = self.STOPPED
		self.shuffleState = self.UNSHUFFLE
		self.muteState = self.UNMUTE

		# MP3file
		self.mp3file = None

		# VLC player
		self.media = None
		self.vlcInstance = vlc.Instance()
		self.vlcPlayer = self.vlcInstance.media_player_new()
		self.vlcPlayer.audio_set_volume(100)
		self.updatingPlayerState()

		# Init sliders
		self.volume = 100
		self.previousVolume = 100
		self.currentSeconds = 0
		self.songLength = 0
		self.updateVolume(self.volume)
		self.updateTimes(self.currentSeconds, self.songLength)

	def setupCustomWidgets(self):
		self.tableWidget.setup(self)
		self.timeSlider.setup(self)
		self.volumeSlider.setup(self)

	def setupHandlers(self):
		self.openFileButton.clicked.connect(self.handleOpenFileButton)
		self.chooseImageButton.clicked.connect(self.handleChooseImageButton)
		self.removeFileButton.clicked.connect(self.handleRemoveFileButton)
		self.deleteCoverButton.clicked.connect(self.handleDeleteCoverButton)
		self.renameFileButton.clicked.connect(self.handleRenameFileButton)
		self.saveChangesButton.clicked.connect(self.handleSaveChangesButton)
		self.groupEditButton.clicked.connect(self.handleGroupEditButton)
		self.playButton.clicked.connect(self.handlePlayButton)
		self.stopButton.clicked.connect(self.handleStopButton)
		self.nextButton.clicked.connect(self.handleNextButton)
		self.previousButton.clicked.connect(self.handlePreviousButton)
		self.shuffleButton.clicked.connect(self.handleShuffleButton)
		self.muteButton.clicked.connect(self.handleMuteButton)
		QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+A"), self).activated.connect(self.handleSelectAll)
		QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+D"), self).activated.connect(self.handleUnSelectAll)
		QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+O"), self).activated.connect(self.handleOpenFileButton)
		QtWidgets.QShortcut(Qt.Qt.Key_Delete, self, self.handleRemoveFileButton)
		QtWidgets.QShortcut(Qt.Qt.Key_Right, self, self.nextSong)
		QtWidgets.QShortcut(Qt.Qt.Key_Left, self, self.previousSong)
		QtWidgets.QShortcut(Qt.Qt.Key_Down, self, self.nextSong)
		QtWidgets.QShortcut(Qt.Qt.Key_Up, self, self.previousSong)
		QtWidgets.QShortcut(Qt.Qt.Key_Space, self, self.togglePlayPause)
		QtWidgets.QShortcut(Qt.Qt.Key_Escape, self, self.focusOut)

	def focusOut(self):
		self.setFocus(Qt.Qt.OtherFocusReason)

	def closeEvent(self, event):
		self.closed = True
		event.accept()

	def handleSelectAll(self):
		self.tableWidget.checkAllRows()

	def handleUnSelectAll(self):
		self.tableWidget.unCheckAllRows()

	def clearTags(self):
		self.labelImage.hide()
		for key in MP3File.property_2_name:
			self.__getattribute__(key + "Line").setText("")

	def fillTags(self, mp3file):
		for key in mp3file.property_2_tag:
			self.__getattribute__(key + "Line").setText(mp3file.getAttr(key).text())

	def redrawCoverImage(self):
		if self.mp3file is not None and self.mp3file.image is not None:
			img = self.mp3file.image
			if (img.width() / img.height()) > (self.labelImage.width() / self.labelImage.height()):
				img = img.scaledToWidth(self.labelImage.width())
			else:
				img = img.scaledToHeight(self.labelImage.height())
			self.labelImage.setPixmap(img)
			self.labelImage.show()
		else:
			self.labelImage.hide()

	def handleRowClicked(self, row):
		if row is None:
			self.mp3file = None
		else:
			self.mp3file = self.tableWidget.getMP3File(row)

		self.reloadMP3File(self.mp3file)

	def reloadMP3File(self, mp3file):
		if mp3file is not None:
			# Load media file to vlc media and if it should be playing and it is not playing, hit play
			self.media = self.vlcInstance.media_new(mp3file.path)
			self.vlcPlayer.set_media(self.media)
			if self.playState == self.PLAYING and not self.vlcPlayer.is_playing():
				self.vlcPlayer.play()

			# Update correct informations
			self.songBitRateLabel.setText(str(self.mp3file.songBitrate))
			self.updateTimes(currentSeconds=0, songLength=self.mp3file.songLength)

			# Fill the tags into the lineEdits and reload CoverImage
			self.fillTags(self.mp3file)
			self.mp3file.reloadCoverImage()
			self.redrawCoverImage()
		else:
			# If there's no file, we should definitely stop and clear media file
			self.stop()
			self.media = None

			# Remove informations and set times to zeros
			self.songBitRateLabel.setText("N/A")
			self.updateTimes(currentSeconds=0, songLength=0)

			# Clear tags and reload cover image (it will be empty)
			self.clearTags()
			self.redrawCoverImage()

	def updatingPlayerState(self):
		if self.playState == self.PLAYING or self.playState == self.PAUSED:
			songTime = int(self.vlcPlayer.get_time() * 0.001)
			self.updateTimes(currentSeconds=songTime)

		if self.playState == self.PLAYING and self.vlcPlayer.get_time() >= self.songLength * 1000:
			print("Song ended, trying to play next song")
			self.nextSong()

		if not self.closed:
			threading.Timer(0.2, self.updatingPlayerState).start()

	def handleChooseImageButton(self):
		path = QtWidgets.QFileDialog.getOpenFileName(self, "Select image cover", filter="images ({})".format(" ".join(["*." + i for i in MP3File.coverExtensions])))[0]
		if path != "":
			self.coverLine.setText(path)
			with open(self.coverLine.text(), "rb") as coverFile:
				self.mp3file.loadCoverImageFromBytes(coverFile.read())
			self.redrawCoverImage()

	def handleOpenFileButton(self):
		paths = QtWidgets.QFileDialog.getOpenFileNames(self, "Select MP3 files", filter="mp3(*.mp3)")[0]
		for path in paths:
			mp3file = MP3File(path)
			self.tableWidget.addMP3(mp3file)

	def convertSecsToString(self, secs, hours_digits=0, long_format=False):
		hours = secs // 3600
		mins = (secs % 3600) // 60
		secs = secs % 60

		if not long_format:
			if hours_digits == 0 and hours == 0:
				return "{}:{}".format(str(mins).zfill(2), str(secs).zfill(2))
			elif hours_digits == 0 and hours > 0:
				return "{}:{}:{}".format(str(hours), str(mins).zfill(2), str(secs).zfill(2))
			hours_digits = int(math.ceil(math.log10(hours)))
			return "{}:{}:{}".format(str(hours).zfill(hours_digits), str(mins).zfill(2), str(secs).zfill(2))
		else:
			if hours_digits == 0 and hours == 0:
				return "{} mins {} secs".format(str(mins), str(secs))
			elif hours_digits == 0 and hours > 0:
				return "{} hours {} mins {} secs".format(str(hours), str(mins), str(secs))
			hours_digits = int(math.ceil(math.log10(hours)))
			return "{} hours {} mins {} secs".format(str(hours), str(mins), str(secs))

	def updateFilesPickedLabel(self):
		self.filesPickedLabel.setText(str(self.tableWidget.checkedRowsCount()))

	def updateTimeFromSlider(self):
		self.songTimeLabel.setText(self.convertSecsToString(self.timeSlider.maximum()))
		self.songCurrentTimeLabel.setText(self.convertSecsToString(self.timeSlider.sliderPosition()))
		self.songLengthStrLabel.setText(self.convertSecsToString(self.timeSlider.maximum(), long_format=True))
		self.updateTimes(int(self.timeSlider.sliderPosition()), int(self.timeSlider.maximum()), recurse=False)

	def updateTimes(self, currentSeconds=None, songLength=None, recurse=True):
		if currentSeconds is not None and not isinstance(currentSeconds, int):
			raise TypeError("currentSeconds must be integer")

		if songLength is not None and not isinstance(songLength, int):
			raise TypeError("songLength must be integer")

		if currentSeconds is not None and self.currentSeconds != currentSeconds:
			self.currentSeconds = currentSeconds

		if songLength is not None and self.songLength != songLength:
			self.songLength = songLength

		if recurse:
			self.songCurrentTimeLabel.setText(self.convertSecsToString(self.currentSeconds))
			self.songTimeLabel.setText(self.convertSecsToString(self.songLength))
			self.songLengthStrLabel.setText(self.convertSecsToString(self.songLength, long_format=True))
			self.timeSlider.setSliderPosition(self.currentSeconds)
			self.timeSlider.setMaximum(self.songLength)

		if int(self.vlcPlayer.get_time() * 0.001) != self.currentSeconds:
			self.vlcPlayer.set_time(self.currentSeconds * 1000)

	def updateVolumeFromSlider(self):
		self.updateVolume(int(self.volumeSlider.sliderPosition()), recurse=False)

	def updateVolume(self, volume, recurse=True):
		self.volume = volume
		if self.volume > 0:
			self.muteState = self.UNMUTE
			self.muteButton.setIcon(QtGui.QIcon("ui/icon/unmute.png"))
			self.muteButton.setToolTip("Mute")
		else:
			self.muteState = self.MUTE
			self.muteButton.setIcon(QtGui.QIcon("ui/icon/mute.png"))
			self.muteButton.setToolTip("UnMute")

		if recurse:
			self.volumeSlider.setSliderPosition(self.volume)

		self.vlcPlayer.audio_set_volume(self.volume)

	def mute(self):
		self.previousVolume = self.volume
		self.volume = 0
		self.updateVolume(0)

	def unmute(self):
		self.volume, self.previousVolume = self.previousVolume, self.volume
		self.updateVolume(self.volume)

	def togglePlayPause(self):
		if self.playState == self.PLAYING:
			self.pause()
		else:
			self.play()

	def play(self):
		self.playState = self.PLAYING
		self.playButton.setIcon(QtGui.QIcon("ui/icon/pause.png"))
		self.playButton.setToolTip("Pause")

		self.vlcPlayer.play()

	def stop(self):
		self.playState = self.STOPPED
		self.playButton.setIcon(QtGui.QIcon("ui/icon/play.png"))
		self.stopButton.setToolTip("Stop")

		self.updateTimes(currentSeconds=0)
		self.vlcPlayer.stop()

	def pause(self):
		self.playState = self.PAUSED
		self.playButton.setIcon(QtGui.QIcon("ui/icon/play.png"))
		self.playButton.setToolTip("Play")

		self.vlcPlayer.pause()

	def nextSong(self):
		self.tableWidget.selectNextRow(self.shuffleState == self.UNSHUFFLE)

	def previousSong(self):
		self.tableWidget.selectPreviousRow(self.shuffleState == self.UNSHUFFLE)

	def shuffle(self):
		self.shuffleState = self.SHUFFLE
		self.shuffleButton.setIcon(QtGui.QIcon("ui/icon/unshuffle.png"))
		self.shuffleButton.setToolTip("Switch shuffle off")

	def unshuffle(self):
		self.shuffleState = self.UNSHUFFLE
		self.shuffleButton.setIcon(QtGui.QIcon("ui/icon/shuffle.png"))
		self.shuffleButton.setToolTip("Switch shuffle on")

	def handleRemoveFileButton(self):
		filesCount = self.tableWidget.checkedRowsCount()
		if filesCount > 0:
			if filesCount == 1:
				filesInflected = "vybraný {} soubor".format(filesCount)
			elif filesCount < 5:
				filesInflected = "vybrané {} soubory".format(filesCount)
			else:
				filesInflected = "vybraných {} souborů".format(filesCount)
			msg = "Opravdu chcete odstranit {}?".format(filesInflected)
			reply = QtWidgets.QMessageBox.question(self, 'Message', msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)

			if reply == QtWidgets.QMessageBox.Yes:
				self.tableWidget.removeCheckedMP3Files()
		else:
			QtWidgets.QMessageBox.warning(self, "Nevybrané žádné soubory", "Nebyly vybrány žádné soubory pro odstranění.")

		if self.tableWidget.rowCount() == 0 or self.playState == self.PLAYING:
			self.stop()

	def handleDeleteCoverButton(self):
		if self.mp3file is not None and self.mp3file.image is not None:
			msg = "Opravdu chcete odstranit fotku alba?"
			reply = QtWidgets.QMessageBox.question(self, 'Message', msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)

			if reply == QtWidgets.QMessageBox.Yes:
				self.mp3file.removeCoverImage()
				self.coverLine.setText("")
				self.redrawCoverImage()
		else:
			QtWidgets.QMessageBox.warning(self, "Fotka alba neexistuje", "Fotku alba nelze odstranit, protože neexistuje.")

	def handleRenameFileButton(self):
		if self.tableWidget.checkedRowsCount() > 0:
			print("handleRenameFileButton")
		else:
			QtWidgets.QMessageBox.warning(self, "Nevybrané žádné soubory", "Nebyly vybrány žádné soubory pro přejmenování.")

	def saveTags(self):
		# Check tricky parts
		if not self.mp3file.canRename(self.fileNameLine.text()):
			raise FileExistsError("Cannot rename file because file already exists!")
		if self.fileNameLine.text() == "":
			raise FileNotFoundError("The file name cannot be empty!")
		if self.coverLine.text() != "" and not os.path.exists(self.coverLine.text()):
			raise FileNotFoundError("The album image doesnt exists!")
		if self.coverLine.text() != "" and self.coverLine.text().split(".")[-1] not in MP3File.coverExtensions:
			raise NameError("Image is in wrong format")

		# Rename file if needed
		self.mp3file.saveTag("fileName", self.fileNameLine.text())

		# Set album name
		self.mp3file.saveTag("cover", self.coverLine.text())

		# Save all other tags
		if self.mp3file is not None:
			for key, value in self.mp3file.property_2_tag.items():
				if value not in ["APIC", "PATH"]:
					self.mp3file.saveTag(key, self.__getattribute__(key + "Line").text())

	def handleSaveChangesButton(self):
		if self.mp3file is not None:
			try:
				self.saveTags()
				self.redrawCoverImage()
			# TODO handle errors with dialogs
			except Exception as e:
				print("EXCEPTION occured: {}".format(e))
		else:
			QtWidgets.QMessageBox.warning(self, "Není načtený soubor", "Nebyl načten žádný hudební soubor, nelze uložit změny.")

	def handleGroupEditButton(self):
		if self.tableWidget.checkedRowsCount() > 0:
			print("handleGroupEditButton")
		else:
			QtWidgets.QMessageBox.warning(self, "Nevybrané žádné soubory", "Nebyly vybrány žádné soubory pro hromadné přejmenování.")

	def handlePlayButton(self):
		if self.playState == self.PLAYING:
			self.pause()

		elif self.playState == self.PAUSED or self.playState == self.STOPPED:
			self.play()

	def handleStopButton(self):
		self.stop()

	def handleNextButton(self):
		self.nextSong()

	def handlePreviousButton(self):
		self.previousSong()

	def handleShuffleButton(self):
		if self.shuffleState == self.SHUFFLE:
			self.unshuffle()

		elif self.shuffleState == self.UNSHUFFLE:
			self.shuffle()

	def handleMuteButton(self):
		if self.muteState == self.MUTE:
			self.unmute()

		elif self.muteState == self.UNMUTE:
			self.mute()

	def run(self):
		self.show()
		return self.app.exec()
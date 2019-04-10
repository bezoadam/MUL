import os
from io import BytesIO
from collections import OrderedDict, defaultdict
import math
from typing import Dict, Set, List
import threading
import random

import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TPE1, TIT2, TRCK, TALB, APIC, TDRC, TCON, COMM
from PyQt5 import QtWidgets, uic, Qt, QtGui
import vlc

from mp3player.sliders import JumpSlider, VolumeSlider, TimeSlider
from mp3player.MP3Table import MP3Table, MP3File, MP3Tag
from mp3player.EditWindow import EditWindow

class TagDialog(QtWidgets.QDialog):
	def __init__(self, *args):
		'''Initializer
		'''
		super(QtWidgets.QDialog, self).__init__(*args)

		# Load UI
		uiFile = "ui/tag_dialog.ui"
		with open(uiFile) as f:
			uic.loadUi(f, self)

	def clear(self):
		self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
		self.comboBox.setCurrentIndex(-1)

	def handleCurrentIndexChanged(self, index):
		if index < 0:
			self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
		else:
			self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)

	def exec(self, *args, **kwargs):
		self.clear()
		return super().exec(*args, **kwargs)

	def setup(self, mainWindow):
		self.mainWindow = mainWindow
		self.comboBox.currentIndexChanged.connect(self.handleCurrentIndexChanged)

		self.properties = [i for (i, j) in MP3File.property_2_name.items() if i != "fileName"]
		self.tags = [MP3File.property_2_tag[i] for i in self.properties]
		self.items = [MP3File.property_2_name[i] for i in self.properties]

		indices = sorted(range(len(self.items)), key=lambda x: self.items[x])

		self.properties = [self.properties[i] for i in indices]
		self.tags = [self.tags[i] for i in indices]
		self.items = [self.items[i] for i in indices]

		self.comboBox.addItems(self.items)

	def getChoosedProperty(self):
		if self.comboBox.currentIndex() >= 0:
			return self.properties[self.comboBox.currentIndex()]

	def getChoosedTag(self):
		if self.comboBox.currentIndex() >= 0:
			return self.tags[self.comboBox.currentIndex()]

	def getChoosedItem(self):
		if self.comboBox.currentIndex() >= 0:
			return self.items[self.comboBox.currentIndex()]


class SortTable(QtWidgets.QTableWidget):
	'''Custom SortTable for managing group editation

	Arguments:

		QtWidgets {QTableWidget} -- Base class

	Returns:

		SortTable -- instance of SortTable
	'''

	def __init__(self, *args):
		'''Initializer of SortTable
		'''
		super(QtWidgets.QTableWidget, self).__init__(*args)

		# Setup handlers
		self.setupHandlers()

	def setup(self, editWindow):
		self.editWindow = editWindow

	def setupHandlers(self):
		self.itemSelectionChanged.connect(self.handleRowSelection)

	def handleRowSelection(self):
		row = self.getSelectedRowFromRanges()
		if row is not None:
			if row == 0:
				self.editWindow.upButton.setEnabled(False)
				self.editWindow.downButton.setEnabled(True)
			elif row == self.rowCount() - 1:
				self.editWindow.upButton.setEnabled(True)
				self.editWindow.downButton.setEnabled(False)
			else:
				self.editWindow.upButton.setEnabled(True)
				self.editWindow.downButton.setEnabled(True)
			self.editWindow.removeButton.setEnabled(True)
		else:
			self.editWindow.upButton.setEnabled(False)
			self.editWindow.downButton.setEnabled(False)
			self.editWindow.removeButton.setEnabled(False)

	def isEmpty(self):
		return self.rowCount() > 0

	def getMP3File(self, row):
		'''Get mp3 file wrapper from this table

		Arguments:

			row {int} -- Row to get a mp3 file

		Returns:

			MP3File -- MP3File
		'''
		return self.data[row]

	def getSelectedRowFromRanges(self):
		'''Get selected row of TableWdiget using selected ranges

		Returns:

			int -- Row index
		'''
		rows = [i.topRow() for i in self.selectedRanges() if i.rightColumn() - i.leftColumn() > 0]
		if len(rows) == 1:
			return rows[0]
		else:
			return None

	def setRangeSelectionByRow(self, row):
		'''Set RangeSelected according to the single row given (if not given set it by actual selected row)

		Keyword Arguments:

			row {int} -- Row index which range should be selected (default: {None})
		'''
		self.setRangeSelected(QtWidgets.QTableWidgetSelectionRange(0, 0, self.rowCount() - 1, self.columnCount() - 1), False)
		if row is not None:
			self.setRangeSelected(QtWidgets.QTableWidgetSelectionRange(row, 0, row, self.columnCount() - 1), True)
			self.handleRowSelection()

	def switchRows(self, row1, row2):
		for i in range(self.columnCount()):
			item1 = self.takeItem(row1, i)
			item2 = self.takeItem(row2, i)
			self.setItem(row2, i, item1)
			self.setItem(row1, i, item2)

	def moveRowUp(self):
		row = self.getSelectedRowFromRanges()
		if row is not None:
			self.switchRows(row, row - 1)
			self.editWindow.switchRows(row, row - 1)
			self.setRangeSelectionByRow(row - 1)

	def moveRowDown(self):
		row = self.getSelectedRowFromRanges()
		if row is not None:
			self.switchRows(row, row + 1)
			self.editWindow.switchRows(row, row + 1)
			self.setRangeSelectionByRow(row + 1)

	def handleRemoveRow(self):
		row = self.getSelectedRowFromRanges()
		if row is not None:
			self.removeRow(row)
			self.editWindow.removeRow(row)

	def createHeaders(self, header_labels):
		self.setColumnCount(len(header_labels))
		self.setHorizontalHeaderLabels(header_labels)
		self.setFocusPolicy(Qt.Qt.NoFocus)

	def fillRows(self, data):
		pass

	def addRow(self, mp3file):
		'''Add MP3 file to table

		Arguments:

			mp3file {MP3File} -- MP3File object which should be inserted to table
		'''
		# Get current number of rows and insert new row
		rowCount = self.rowCount()
		self.insertRow(rowCount)

		# Create checkbox item and insert it
		checkBoxHeader = QtWidgets.QTableWidgetItem()
		checkBoxHeader.setFlags(Qt.Qt.ItemIsUserCheckable | Qt.Qt.ItemIsEnabled)
		checkBoxHeader.setCheckState(Qt.Qt.Unchecked)
		checkBoxHeader.setTextAlignment(Qt.Qt.AlignCenter)
		self.setItem(rowCount, 0, checkBoxHeader)

		# insert all other tags to table
		for idx, key in enumerate(mp3file.property_2_tag):
			if key != "cover":
				self.setItem(rowCount, idx + 1, mp3file.__getattribute__(key))

	def refreshTable(self, row):
		pass


class MP3Player(QtWidgets.QMainWindow):
	'''QMainWindow containing mp3 player

	Arguments:

		QtWidgets {QMainWindow} -- Base class

	Raises:

		TypeError -- [description]
		TypeError -- [description]
		FileExistsError -- [description]
		FileNotFoundError -- [description]
		FileNotFoundError -- [description]
		NameError -- [description]

	Returns:

		[type] -- [description]
	'''
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
		'''Initializer
		'''
		super(QtWidgets.QMainWindow, self).__init__()

		# Load UI
		uiFile = "ui/new_window.ui"
		with open(uiFile) as f:
			uic.loadUi(f, self)

		# Init all properties
		self.propertyInit()

		# Connect all signals to handlers
		self.setupHandlers()

		# Setup custom widgets
		self.setupCustomWidgets()

	def setupCustomWidgets(self):
		'''Setup custom widgets (linking parent object to them)
		'''
		self.tableWidget.setup(self)
		self.timeSlider.setup(self)
		self.volumeSlider.setup(self)
		self.tagDialog.setup(self)
		self.editWindow.setup(self)

	def propertyInit(self):
		'''Property initializer
		'''
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

		# Init sliders
		self.volume = 100
		self.previousVolume = 100
		self.currentSeconds = 0
		self.songLength = 0
		self.updateVolume(100)
		self.updateTimes(self.currentSeconds, self.songLength)

		# Dialogs and other managed windows
		self.tagDialog = TagDialog(self)
		self.editWindow = EditWindow(self)

	def setupHandlers(self):
		'''Setup handlers to the signals and shortcuts also
		'''
		self.openFileButton.clicked.connect(self.handleOpenFileButton)
		self.chooseImageButton.clicked.connect(self.handleChooseImageButton)
		self.removeFileButton.clicked.connect(self.handleRemoveFileButton)
		self.deleteCoverButton.clicked.connect(self.handleDeleteCoverButton)
		self.renameFileButton.clicked.connect(self.handleRenameFileButton)
		self.guessTagButton.clicked.connect(self.handleGuessTagButton)
		self.guessNameButton.clicked.connect(self.handleGuessNameButton)
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

	def isPlaying(self):
		'''If mp3 player should be playing

		Returns:

			bool -- True if playing, False if not
		'''
		return self.playState == self.PLAYING

	def isStopped(self):
		'''If mp3 player should be stopped

		Returns:

			bool -- True if stopped, False if not
		'''
		return self.playState == self.STOPPED

	def isPaused(self):
		'''If mp3 player should be paused

		Returns:

			bool -- True if paused, False if not
		'''
		return self.playState == self.PAUSED

	def isShuffleOn(self):
		'''If shuffle is turned on

		Returns:

			bool -- True if yes, False if no
		'''
		return self.shuffleState == self.SHUFFLE

	def isMuted(self):
		'''If volume is muted

		Returns:

			bool -- True if yes, False if no
		'''
		return self.muteState == self.MUTE

	def focusOut(self):
		'''Focus out (for example from line edits)
		'''
		self.setFocus(Qt.Qt.OtherFocusReason)

	def closeEvent(self, event):
		'''If the window is closing, just memorize it happend

		Arguments:

			event {[type]} -- [description]
		'''
		self.closed = True
		event.accept()

	def setEnabled(self, enabled):
		if not enabled and self.isPlaying():
			self.pause()
		super().setEnabled(enabled)

	def show(self, *args, **kwargs):
		'''Override show method for memorizing that self.closed
		'''
		# Window state
		self.closed = False
		self.updatingPlayerState()

		super().show(*args, **kwargs)

	def handleSelectAll(self):
		'''Handle select all
		'''
		self.tableWidget.checkAllRows()

	def handleUnSelectAll(self):
		'''Handle unselect all
		'''
		self.tableWidget.unCheckAllRows()

	def clearLineEdits(self):
		'''Clear line edits
		'''
		self.labelImage.hide()
		for key in MP3File.property_2_name:
			self.__getattribute__(key + "Line").setText("")

	def fillLineEdits(self, mp3file=None):
		'''Fill line edits from mp3 file

		Arguments:

			mp3file {MP3File} -- MP3File
		'''
		mp3file = self.mp3file if mp3file is None else mp3file
		if mp3file is not None:
			for key in mp3file.property_2_tag:
				self.__getattribute__(key + "Line").setText(mp3file.__getattribute__(key).text())

	def redrawCoverImage(self):
		'''Redraw cover image
		'''
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

	def setMediaFileFromRow(self, row):
		'''Set media file from row from tableWidget

		Arguments:

			row {int} -- Row index
		'''
		if row is None:
			self.mp3file = None
		else:
			self.mp3file = self.tableWidget.getMP3File(row)

		self.setMediaFileFromMP3File(self.mp3file)
		self.tableWidget.setRangeSelectionByRow(row)

	def setMediaFileFromMP3File(self, mp3file):
		'''Reload MP3File and if player should be playing, play

		Arguments:

			mp3file {MP3File} -- MP3File to be played
		'''
		if mp3file is not None:
			# Load media file to vlc media and if it should be playing and it is not, hit play
			self.media = self.vlcInstance.media_new(mp3file.path)
			self.vlcPlayer.set_media(self.media)
			if self.isPlaying() and not self.vlcPlayer.is_playing():
				self.vlcPlayer.play()

			# Update correct informations
			self.songBitRateLabel.setText(str(self.mp3file.songBitrate))
			self.updateTimes(currentSeconds=0, songLength=self.mp3file.songLength)

			# Fill the tags into the lineEdits and reload CoverImage
			self.fillLineEdits(self.mp3file)
			self.mp3file.loadCoverImageFromFile()
			self.redrawCoverImage()
		else:
			# If there's no file, we should definitely stop and clear media file
			self.stop()
			self.media = None

			# Remove informations and set times to zeros
			self.songBitRateLabel.setText("N/A")
			self.updateTimes(currentSeconds=0, songLength=0)

			# Clear tags and reload cover image (it will be empty)
			self.clearLineEdits()
			self.redrawCoverImage()

	def updatingPlayerState(self):
		'''Update mp3 player state periodically
		'''
		if self.isPlaying() or self.isPaused():
			songTime = int(self.vlcPlayer.get_time() * 0.001)
			self.updateTimes(currentSeconds=songTime)

		if self.isPlaying() and self.vlcPlayer.get_time() >= self.songLength * 1000:
			self.nextSong()

		if not self.closed:
			threading.Timer(0.2, self.updatingPlayerState).start()

	def handleChooseImageButton(self):
		'''Handle choose image button, select path and redraw cover image
		'''
		if self.mp3file is None:
			QtWidgets.QMessageBox.warning(self, "Není načtený soubor",
										  "Nebyl načten žádný hudební soubor, nelze vložit obrázek.")
		else:
			path = QtWidgets.QFileDialog.getOpenFileName(self, "Select image cover", filter="images ({})".format(" ".join(["*." + i for i in MP3File.coverExtensions])))[0]
			if path != "":
				self.coverLine.setText(path)
				with open(self.coverLine.text(), "rb") as coverFile:
					self.mp3file.loadCoverImageFromBytes(coverFile.read())
				self.redrawCoverImage()

	def handleOpenFileButton(self):
		'''Handle open file button, create mp3 file and add it to table
		'''
		paths = QtWidgets.QFileDialog.getOpenFileNames(self, "Select MP3 files", filter="mp3(*.mp3)")[0]
		for path in paths:
			mp3file = MP3File(path)
			self.tableWidget.addMP3(mp3file)

	def convertSecsToString(self, secs, hours_digits=0, long_format=False):
		'''Convert seconds to human readable format

		Arguments:

			secs {int} -- Seconds

		Keyword Arguments:

			hours_digits {int} -- How many hour digits to zfill (default: {0})
			long_format {bool} -- If long format is triggered (default: {False})

		Returns:

			str -- string time format
		'''
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

	def updateFilesCheckedLabel(self):
		'''Update how many files are checked
		'''
		self.filesPickedLabel.setText(str(self.tableWidget.checkedRowsCount()))

	def updateTimeFromSlider(self):
		'''Update current time progress of song from slider
		'''
		self.songTimeLabel.setText(self.convertSecsToString(self.timeSlider.maximum()))
		self.songCurrentTimeLabel.setText(self.convertSecsToString(self.timeSlider.sliderPosition()))
		self.songLengthStrLabel.setText(self.convertSecsToString(self.timeSlider.maximum(), long_format=True))
		self.updateTimes(int(self.timeSlider.sliderPosition()), int(self.timeSlider.maximum()), recurse=False)

	def updateTimes(self, currentSeconds=None, songLength=None, recurse=True):
		'''Update song times, it triggers changes of sliders if recurse is set to true

		Keyword Arguments:

			currentSeconds {int} -- Current seconds progress of song (default: {None})
			songLength {int} -- Song length (default: {None})
			recurse {bool} -- If it should trigger change of slider (default: {True})

		Raises:

			TypeError -- [description]
			TypeError -- [description]
		'''

		if currentSeconds is not None and not isinstance(currentSeconds, int):
			raise TypeError("currentSeconds must be integer")

		if songLength is not None and not isinstance(songLength, int):
			raise TypeError("songLength must be integer")

		if currentSeconds is not None and self.currentSeconds != currentSeconds:
			self.currentSeconds = currentSeconds

		if songLength is not None and self.songLength != songLength:
			self.songLength = songLength

		self.songCurrentTimeLabel.setText(self.convertSecsToString(self.currentSeconds))
		self.songTimeLabel.setText(self.convertSecsToString(self.songLength))
		self.songLengthStrLabel.setText(self.convertSecsToString(self.songLength, long_format=True))
		if recurse:
			self.timeSlider.setSliderPosition(self.currentSeconds)
			self.timeSlider.setMaximum(self.songLength)

		if int(self.vlcPlayer.get_time() * 0.001) != self.currentSeconds:
			self.vlcPlayer.set_time(self.currentSeconds * 1000)

	def updateVolumeFromSlider(self):
		'''Update volume from actual slider position
		'''
		self.updateVolume(int(self.volumeSlider.sliderPosition()), recurse=False)

	def updateVolume(self, volume, recurse=True):
		'''Update volume of the player

		Arguments:

			volume {int} -- Volume value

		Keyword Arguments:

			recurse {bool} -- If it should trigger change of slider (default: {True})
		'''

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
		'''Mute player
		'''
		self.previousVolume = self.volume
		self.volume = 0
		self.updateVolume(0)

	def unmute(self):
		'''Unmute player
		'''
		self.volume, self.previousVolume = self.previousVolume, self.volume
		self.updateVolume(self.volume)

	def togglePlayPause(self):
		'''Toggle play or pause
		'''
		if self.isPlaying():
			self.pause()
		else:
			self.play()

	def play(self):
		'''Play the song
		'''
		self.playState = self.PLAYING
		self.playButton.setIcon(QtGui.QIcon("ui/icon/pause.png"))
		self.playButton.setToolTip("Pause")

		self.vlcPlayer.play()

	def stop(self):
		'''Stop the song
		'''
		self.playState = self.STOPPED
		self.playButton.setIcon(QtGui.QIcon("ui/icon/play.png"))
		self.stopButton.setToolTip("Stop")

		self.updateTimes(currentSeconds=0)
		self.vlcPlayer.stop()

	def pause(self):
		'''Pause the song
		'''
		self.playState = self.PAUSED
		self.playButton.setIcon(QtGui.QIcon("ui/icon/play.png"))
		self.playButton.setToolTip("Play")

		self.vlcPlayer.pause()

	def nextSong(self):
		'''Play next song
		'''
		self.tableWidget.activateNextRow(self.shuffleState == self.UNSHUFFLE)

	def previousSong(self):
		'''Play previous song
		'''
		self.tableWidget.activatePreviousRow(self.shuffleState == self.UNSHUFFLE)

	def shuffle(self):
		'''Set shuffle on
		'''
		self.shuffleState = self.SHUFFLE
		self.shuffleButton.setIcon(QtGui.QIcon("ui/icon/unshuffle.png"))
		self.shuffleButton.setToolTip("Switch shuffle off")

	def unshuffle(self):
		'''Set shuffle off
		'''
		self.shuffleState = self.UNSHUFFLE
		self.shuffleButton.setIcon(QtGui.QIcon("ui/icon/shuffle.png"))
		self.shuffleButton.setToolTip("Switch shuffle on")

	def handleRemoveFileButton(self):
		'''Handle remove file button
		'''
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

		if self.tableWidget.rowCount() == 0 or self.isPlaying():
			self.stop()

	def saveTags(self):
		'''Save tags from lineEdits

		Raises:

			FileExistsError -- Cannot rename file
			FileNotFoundError -- Cover file wasn't found
			NameError -- Image is in wrong format
		'''
		# Check tricky parts
		if not self.mp3file.canRenameFilename(self.fileNameLine.text()):
			raise FileExistsError("Cannot rename file because file already exists!")
		if self.coverLine.text() != "" and not os.path.exists(self.coverLine.text()):
			raise FileNotFoundError("The album image doesnt exists!")
		if self.coverLine.text() != "" and self.coverLine.text().split(".")[-1] not in MP3File.coverExtensions:
			raise NameError("Image is in wrong format")

		# Rename file if needed
		self.mp3file.saveTagToFile("fileName", self.fileNameLine.text())

		# Set album name
		self.mp3file.saveTagToFile("cover", self.coverLine.text())

		# Save all other tags
		if self.mp3file is not None:
			for key, value in self.mp3file.property_2_tag.items():
				if value not in ["APIC", "PATH"]:
					self.mp3file.saveTagToFile(key, self.__getattribute__(key + "Line").text())

	def handleSaveChangesButton(self):
		'''Handle save changes button
		'''
		if self.mp3file is not None:
			try:
				self.saveTags()
				self.redrawCoverImage()
			except FileExistsError:
				QtWidgets.QMessageBox.warning(self, "NNelze přejmenovat soubor", "Nelze přejmenovat soubor, soubor již existuje, nebo byl zadán prázdný řetězec.")
			except FileNotFoundError:
				QtWidgets.QMessageBox.warning(self, "Obrázek alba nenalazen", "Obrázek alba neexistuje.")
			except NameError:
				QtWidgets.QMessageBox.warning(self, "Špatný formát obrázku", "Špatný formát vstupního obrázku alba.")
			except Exception:
				QtWidgets.QMessageBox.warning(self, "Nelze uložit data", "Vyskytla se chyba při ukládání")
			QtWidgets.QMessageBox.information(self, "Uložení proběhlo úspěšně", "Uloženi informací o souboru proběhlo úspěšně.")
		else:
			QtWidgets.QMessageBox.warning(self, "Není načtený soubor", "Nebyl načten žádný hudební soubor, nelze uložit změny.")

	def handleDeleteCoverButton(self):
		'''Handle delete cover album button
		'''
		if self.mp3file is not None and self.mp3file.image is not None:
			msg = "Opravdu chcete odstranit fotku alba?"
			reply = QtWidgets.QMessageBox.question(self, 'Message', msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)

			if reply == QtWidgets.QMessageBox.Yes:
				self.mp3file.removeCoverImageFromFile()
				self.coverLine.setText("")
				self.redrawCoverImage()
		else:
			QtWidgets.QMessageBox.warning(self, "Fotka alba neexistuje", "Fotku alba nelze odstranit, protože neexistuje.")

	def handleRenameFileButton(self):
		'''Handle rename file button
		'''
		if self.tableWidget.checkedRowsCount() > 0:
			self.editWindow.exec(self.tableWidget.getCheckedMP3Files(), "fileName", False, False)
		else:
			QtWidgets.QMessageBox.warning(self, "Nevybrané žádné soubory", "Nebyly vybrány žádné soubory pro přejmenování.")

	def handleGuessTagButton(self):
		'''Handle guess tags button
		'''
		if self.tableWidget.checkedRowsCount() > 0:
			self.editWindow.exec(self.tableWidget.getCheckedMP3Files(), None, True, False)
		else:
			QtWidgets.QMessageBox.warning(self, "Nevybrané žádné soubory", "Nebyly vybrány žádné soubory pro odhad tagů.")

	def handleGuessNameButton(self):
		'''Handle guess name button
		'''
		if self.tableWidget.checkedRowsCount() > 0:
			self.editWindow.exec(self.tableWidget.getCheckedMP3Files(), None, False, True)
		else:
			QtWidgets.QMessageBox.warning(self, "Nevybrané žádné soubory", "Nebyly vybrány žádné soubory pro odhad názvu souboru.")

	def handleGroupEditButton(self):
		'''Handle group edit button
		'''
		if self.tableWidget.checkedRowsCount() > 0:
			if self.tagDialog.exec() > 0:
				self.editWindow.exec(self.tableWidget.getCheckedMP3Files(), self.tagDialog.getChoosedProperty(), False)
		else:
			QtWidgets.QMessageBox.warning(self, "Nevybrané žádné soubory", "Nebyly vybrány žádné soubory pro hromadné úpravy.")

	def handlePlayButton(self):
		'''Handle play button
		'''
		if self.isPlaying():
			self.pause()

		elif self.isPaused() or self.isStopped():
			self.play()

	def handleStopButton(self):
		'''Handle stop button
		'''
		self.stop()

	def handleNextButton(self):
		'''Handle next song button
		'''
		self.nextSong()

	def handlePreviousButton(self):
		'''Handle previous song button
		'''
		self.previousSong()

	def handleShuffleButton(self):
		'''Handle shuffle button
		'''
		if self.isShuffleOn():
			self.unshuffle()

		elif not self.isShuffleOn():
			self.shuffle()

	def handleMuteButton(self):
		'''Handle mute button
		'''
		if self.isMuted():
			self.unmute()

		elif not self.isMuted():
			self.mute()
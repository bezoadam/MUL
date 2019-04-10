from typing import Dict, Set, List
from PyQt5 import QtWidgets, uic, Qt, QtGui

from mp3player.MP3Table import MP3Table, MP3File, MP3Tag

class EditWindow(QtWidgets.QMainWindow):
	COVER_EDIT = 0
	COMMON_EDIT = 1
	GUESS_TAG_EDIT = 2

	def __init__(self, *args):
		'''Initializer of SortTable
		'''
		'''Initializer
		'''
		super(QtWidgets.QMainWindow, self).__init__()

		# Load UI
		uiFile = "ui/group_edit.ui"
		with open(uiFile) as f:
			uic.loadUi(f, self)

	def setup(self, mainWindow):
		'''Setup function for connecting parent widgets with child widgets

		Arguments:

			mainWindow {QtWidgets.QMainWindow} -- Main window of whole application
		'''
		# Init
		self.mainWindow = mainWindow
		self.data = None
		self.property = None
		self.guess_tag = None
		self.editType = None
		self.image = None
		self.imagePath = None
		self.setWindowModality(Qt.Qt.ApplicationModal)
		self.tableWidget.setup(self)

		# Connect
		self.upButton.clicked.connect(self.tableWidget.moveRowUp)
		self.downButton.clicked.connect(self.tableWidget.moveRowDown)
		self.removeButton.clicked.connect(self.tableWidget.handleRemoveRow)
		self.finishButton.clicked.connect(self.handleFinishButton)
		self.cancelButton.clicked.connect(self.handleCancelButton)
		self.parseBox.currentIndexChanged.connect(self.handleParseBox)
		self.valueBox.currentIndexChanged.connect(self.handleValueBox)
		self.parseAbrBox.currentIndexChanged.connect(self.handleParseAbrBox)
		self.valueAbrBox.currentIndexChanged.connect(self.handleValueAbrBox)
		self.parseLine.textChanged.connect(self.parseChanged)
		self.valueLine.textChanged.connect(self.valueChanged)
		self.digitsSpinBox.valueChanged.connect(self.refreshDataInTable)
		self.startIndexSpinBox.valueChanged.connect(self.refreshDataInTable)
		self.chooseImageButton.clicked.connect(self.handleChooseImageButton)
		self.removeImageButton.clicked.connect(self.handleRemoveImageButton)

		# Widgets
		self.coverWidgets = [
			self.imageLabel,
			self.chooseImageButton,
			self.removeImageButton,
		]
		self.commonTagsWidgets = [
			self.valueLabel,
			self.valueBox,
			self.valueLine,
			self.valueAbrBox,
			self.parseLabel,
			self.parseBox,
			self.parseLine,
			self.parseAbrBox,
			self.groupBox,
			self.sideWidget,
			self.tableWidget,
		]
		self.guessTagsWidgets = [
			self.parseLabel,
			self.parseLine,
			self.parseAbrBox,
			self.sideWidget,
			self.tableWidget,
		]
		self.parseAbbreviations = [
			"\\al() - album name",
			"\\ar() - artist name",
			"\\sn() - song name",
			"\\tr() - track",
			"\\ye() - year",
			"\\ge() - genre",
			"\\co() - comment",
		]
		self.abbreviations = [
			"\%al - album name",
			"\%ar - artist name",
			"\%sn - song name",
			"\%tr - track",
			"\%ye - year",
			"\%ge - genre",
			"\%co - comment",
			"\%d - digits from right widget",
		]
		self.tags = [i for i in MP3File.property_2_name if i != "cover"]
		self.parseBox.addItems(self.tags)
		self.parseAbrBox.addItems(self.parseAbbreviations)
		self.valueAbrBox.addItems(self.abbreviations)

	def exec(self, data: List[MP3File], property=None, guess_tag=False):
		self.data = data
		self.property = property
		self.guess_tag = guess_tag

		self.setEditType(self.property, self.guess_tag)

		self.init()

		self.mainWindow.setEnabled(False)
		super().show()

	def setEditType(self, property, guess_tag):
		if guess_tag:
			self.editType = self.GUESS_TAG_EDIT
		elif property == "cover":
			self.editType = self.COVER_EDIT
		elif property in MP3File.property_2_name:
			self.editType = self.COMMON_EDIT

	def isGuessTagEdit(self):
		return self.editType == self.GUESS_TAG_EDIT

	def isCommonEdit(self):
		return self.editType == self.COMMON_EDIT

	def isCoverEdit(self):
		return self.editType == self.COVER_EDIT

	def initEditCoverWidgets(self):
		self.name = MP3File.property_2_name[self.property]
		self.tag = MP3File.property_2_tag[self.property]
		self.titleLabel.setText("Úprava položky: " + self.name)

		[i.setVisible(False) for i in self.commonTagsWidgets + self.guessTagsWidgets]
		[i.setVisible(True) for i in self.coverWidgets]

	def initEditGuessTagsWidgets(self):
		self.titleLabel.setText("Vytvoření tagů ze jména souboru")

		[i.setVisible(False) for i in self.commonTagsWidgets + self.coverWidgets]
		[i.setVisible(True) for i in self.guessTagsWidgets]

		self.parseLine.setEnabled(True)
		self.parseAbrBox.setEnabled(True)

	def initEditCommonTagsWidgets(self):
		self.name = MP3File.property_2_name[self.property]
		self.tag = MP3File.property_2_tag[self.property]
		self.titleLabel.setText("Úprava položky: " + self.name)

		[i.setVisible(False) for i in self.coverWidgets + self.guessTagsWidgets]
		[i.setVisible(True) for i in self.commonTagsWidgets]
		self.parseLine.setEnabled(False)
		self.parseAbrBox.setEnabled(False)
		self.valueLine.setEnabled(False)
		self.valueAbrBox.setEnabled(False)

	def init(self):
		self.upButton.setEnabled(False)
		self.downButton.setEnabled(False)
		self.removeButton.setEnabled(False)
		self.finishButton.setEnabled(False)

		if self.isCoverEdit():
			self.initEditCoverWidgets()
		elif self.isCommonEdit():
			self.initEditCommonTagsWidgets()
		elif self.isGuessTagEdit():
			self.initEditGuessTagsWidgets()
		else:
			raise ValueError("Wrong property type")

		# Fill data to table
		self.image = None
		self.tableWidget.setRowCount(0)
		self.createHeaders()
		self.fillRows(self.data)
		self.refreshDataInTable()

		# Setup input widgets
		self.parseBox.setCurrentIndex(-1)
		self.valueBox.setCurrentIndex(0)
		self.parseAbrBox.setCurrentIndex(-1)
		self.valueAbrBox.setCurrentIndex(-1)
		self.valueLine.setText("")
		self.parseLine.setText("")

	def parseChanged(self, text):
		self.refreshDataInTable()

	def valueChanged(self, text):
		self.refreshDataInTable()

	def handleParseBox(self, index):
		if index >= 0:
			self.parseLine.setEnabled(True)
			self.parseAbrBox.setEnabled(True)
		self.refreshDataInTable()

	def handleValueBox(self, index):
		if index == 4:
			self.valueLine.setEnabled(True)
			self.valueAbrBox.setEnabled(True)
		else:
			self.valueLine.setText("")
			self.valueLine.setEnabled(False)
			self.valueAbrBox.setEnabled(False)
		self.refreshDataInTable()

	def handleParseAbrBox(self, index):
		if index >= 0:
			self.parseAbrBox.setCurrentIndex(-1)
			self.parseLine.setText(self.parseLine.text() + self.parseAbbreviations[index].split(" ")[0])

	def handleValueAbrBox(self, index):
		if index >= 0:
			self.valueAbrBox.setCurrentIndex(-1)
			self.valueLine.setText(self.valueLine.text() + self.abbreviations[index].split(" ")[0])

	def createHeaders(self):
		if self.isGuessTagEdit():
			header_labels = [j for (i, j) in MP3File.property_2_name.items() if i != "cover"]
			self.tableWidget.horizontalHeader().setMinimumSectionSize(70)
			self.tableWidget.horizontalHeader().setDefaultSectionSize(70)
			[self.tableWidget.setColumnWidth(i, 70) for i in range(len(header_labels))]
		else:
			header_labels = ["Originální", "Nový"]
			self.tableWidget.horizontalHeader().setMinimumSectionSize(200)
			self.tableWidget.horizontalHeader().setDefaultSectionSize(200)
			[self.tableWidget.setColumnWidth(i, 200) for i in range(len(header_labels))]
		self.tableWidget.createHeaders(header_labels)

	def fillRows(self, data):
		for mp3file in self.data:
			self.addRow(mp3file)

	def addRow(self, mp3file):
		# Get current number of rows and insert new row
		rowCount = self.tableWidget.rowCount()
		self.tableWidget.insertRow(rowCount)

		if self.isGuessTagEdit():
			# insert all other tags to table
			for idx, key in enumerate(mp3file.property_2_tag):
				if key == "fileName":
					mp3file.tmpProperties[key] = MP3Tag(mp3file, key, mp3file.fileName)
					self.tableWidget.setItem(rowCount, idx, mp3file.tmpProperties[key])
				elif key != "cover":
					mp3file.tmpProperties[key] = MP3Tag(mp3file, key, "")
					self.tableWidget.setItem(rowCount, idx, mp3file.tmpProperties[key])
		else:
			self.tableWidget.setItem(rowCount, 0, MP3Tag(mp3file, self.property, mp3file.__getattribute__(self.property).text()))
			mp3file.tmpProperties[self.property] = MP3Tag(mp3file, self.property, "Test")
			self.tableWidget.setItem(rowCount, 1, mp3file.tmpProperties[self.property])

	def removeRow(self, row):
		self.data.pop(row)
		self.refreshDataInTable()

	def switchRows(self, row1, row2):
		tmp = self.data[row1]
		self.data[row1] = self.data[row2]
		self.data[row2] = tmp

		self.refreshDataInTable()

	def refreshDataInTable(self):
		if self.data is None:
			return
		for idx, mp3file in enumerate(self.data):
			if self.isGuessTagEdit():
				print("Parsing the parseLine: {}".format(self.parseLine.text()))
				# TODO: Set correctly the values
				for key in mp3file.tmpProperties:
					mp3file.tmpProperties[key].setText("Tags")
			else:
				if self.valueBox.currentIndex() == 0:
					mp3file.tmpProperties[self.property].setText(mp3file.__getattribute__(self.property).text())
				elif self.valueBox.currentIndex() == 1:
					mp3file.tmpProperties[self.property].setText(mp3file.__getattribute__(self.property).text().lower())
				elif self.valueBox.currentIndex() == 2:
					mp3file.tmpProperties[self.property].setText(mp3file.__getattribute__(self.property).text().upper())
				elif self.valueBox.currentIndex() == 3:
					mp3file.tmpProperties[self.property].setText(mp3file.__getattribute__(self.property).text().capitalize())
				elif self.valueBox.currentIndex() == 4:
					# TODO process value
					value = self.valueLine.text()

					value = value.replace("%d", str(self.startIndexSpinBox.value() + idx).zfill(self.digitsSpinBox.value()))
					mp3file.tmpProperties[self.property].setText(value)

		if self.tableWidget.rowCount() > 0:
			self.finishButton.setEnabled(True)
		else:
			self.finishButton.setEnabled(False)

	def validateChanges(self):
		# TODO validate it
		return True

	def saveChanges(self):
		if not self.validateChanges():
			# TODO Show warning messagebox if errors occured
			return
		for mp3file in self.data:
			mp3file.saveTagToFile(self.property, mp3file.tmpProperties[self.property].text())

	def loadCoverImageFromBytes(self, bytes=None):
		'''Method is loading cover image (QPixmap) from bytes

		Arguments:

			bytes {BytesIO} -- Bytes containing image (loaded from file or from tags data, or whatever)
		'''
		if bytes is not None:
			self.image = QtGui.QPixmap.fromImage(QtGui.QImage.fromData(bytes))
			img = self.image
			if (img.width() / img.height()) > (self.imageLabel.width() / self.imageLabel.height()):
				img = img.scaledToWidth(self.imageLabel.width())
			else:
				img = img.scaledToHeight(self.imageLabel.height())
			self.imageLabel.setPixmap(img)
			self.imageLabel.show()
		else:
			self.image = None
			self.imagePath = None
			for mp3file in self.data:
				mp3file.tmpProperties[self.property].setText("")
			self.imageLabel.hide()

	def handleChooseImageButton(self):
		'''Handle choose image button, select path and redraw cover image
		'''
		path = QtWidgets.QFileDialog.getOpenFileName(self, "Select image cover", filter="images ({})".format(" ".join(["*." + i for i in MP3File.coverExtensions])))[0]
		if path != "":
			self.imagePath = path
			with open(self.imagePath, "rb") as coverFile:
				self.loadCoverImageFromBytes(coverFile.read())
			for mp3file in self.data:
				mp3file.tmpProperties[self.property].setText(self.imagePath)

	def handleRemoveImageButton(self):
		'''Handle delete cover album button
		'''
		if self.image is not None:
			msg = "Opravdu chcete odstranit fotku alba?"
			reply = QtWidgets.QMessageBox.question(self, 'Message', msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)

			if reply == QtWidgets.QMessageBox.Yes:
				self.loadCoverImageFromBytes()
		else:
			QtWidgets.QMessageBox.warning(self, "Fotka alba neexistuje", "Fotku alba nelze odstranit, protože neexistuje.")

	def closeEvent(self, event):
		'''If the window is closing, just memorize it happend

		Arguments:

			event {[type]} -- [description]
		'''
		self.closed = True
		self.mainWindow.setEnabled(True)
		event.accept()

	def handleFinishButton(self):
		self.saveChanges()
		self.mainWindow.redrawCoverImage()
		self.mainWindow.fillLineEdits()
		self.close()

	def handleCancelButton(self):
		self.close()
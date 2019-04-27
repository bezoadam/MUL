from typing import Dict, Set, List
from PyQt5 import QtWidgets, uic, Qt, QtGui
from collections import OrderedDict
import os
import re

import mp3player

__all__ = ["TagDialog", "SortTable", "EditWindow"]


class TagDialog(QtWidgets.QDialog):
	def __init__(self, *args):
		"""Initializer
		"""
		super(QtWidgets.QDialog, self).__init__(*args)

		# Load UI
		uiFile = "ui/tag_dialog.ui"
		with open(uiFile) as f:
			uic.loadUi(f, self)

	def clear(self):
		"""Clear selection
		"""
		self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
		self.comboBox.setCurrentIndex(-1)

	def handleCurrentIndexChanged(self, index):
		"""Handle change of index at combo box selection

		Arguments:

			index {int} -- Index of selected value in combo box
		"""
		if index < 0:
			self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
		else:
			self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)

	def exec(self, *args, **kwargs):
		"""Run Tag dialog (empty)
		"""
		self.clear()
		return super().exec(*args, **kwargs)

	def setup(self, mainWindow, property_2_name, property_2_tag):
		"""Setup tag dialog

		Arguments:

			mainWindow {QtWidgets.QMainWindow} -- parent object
		"""
		self.mainWindow = mainWindow
		self.comboBox.currentIndexChanged.connect(self.handleCurrentIndexChanged)

		# Sort tags and names accordingly
		self.properties = [i for (i, j) in property_2_name.items()]
		self.tags = [property_2_tag[i] for i in self.properties]
		self.items = [property_2_name[i] for i in self.properties]

		indices = sorted(range(len(self.items)), key=lambda x: self.items[x])

		self.properties = [self.properties[i] for i in indices]
		self.tags = [self.tags[i] for i in indices]
		self.items = [self.items[i] for i in indices]

		# Add sorted items to ComboBox
		self.comboBox.addItems(self.items)

	def getChoosedProperty(self):
		"""Returns selected property

		Returns:
			str -- selected property from TagDialog
		"""
		if self.comboBox.currentIndex() >= 0:
			return self.properties[self.comboBox.currentIndex()]

	def getChoosedTag(self):
		"""Returns selected tag

		Returns:
			str -- selected tag from TagDialog
		"""
		if self.comboBox.currentIndex() >= 0:
			return self.tags[self.comboBox.currentIndex()]

	def getChoosedItem(self):
		"""Returns selected item

		Returns:
			str -- selected item from TagDialog
		"""
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
		"""Setup SortTable

		Arguments:
			editWindow {QtWidgets.QMainWindow} -- parent window
		"""
		self.editWindow = editWindow

	def setupHandlers(self):
		"""Setup handlers for SortTable
		"""
		self.itemSelectionChanged.connect(self.handleRowSelection)

	def handleRowSelection(self):
		"""Handle if a row is selected
		"""
		row = self.getSelectedRowFromRanges()
		# If row selected, enable/disable accordingly
		if row is not None:
			# Disable clicking up button
			if row == 0:
				self.editWindow.upButton.setEnabled(False)
				self.editWindow.downButton.setEnabled(True)
			# Disable clikcing down button
			elif row == self.rowCount() - 1:
				self.editWindow.upButton.setEnabled(True)
				self.editWindow.downButton.setEnabled(False)
			# Enable clicking anything
			else:
				self.editWindow.upButton.setEnabled(True)
				self.editWindow.downButton.setEnabled(True)
			self.editWindow.removeButton.setEnabled(True)
		# Ig no row selected, disable all buttons
		else:
			self.editWindow.upButton.setEnabled(False)
			self.editWindow.downButton.setEnabled(False)
			self.editWindow.removeButton.setEnabled(False)

	def isEmpty(self):
		"""If the SortTable is empty

		Returns:
			int -- count of rows
		"""
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
		"""Switch rows in SortTable

		Arguments:
			row1 {int} -- first row index
			row2 {int} -- second row index
		"""
		for i in range(self.columnCount()):
			item1 = self.takeItem(row1, i)
			item2 = self.takeItem(row2, i)
			self.setItem(row2, i, item1)
			self.setItem(row1, i, item2)

	def moveRowUp(self):
		"""Move row up in SortTable
		"""
		row = self.getSelectedRowFromRanges()
		if row is not None:
			self.switchRows(row, row - 1)
			self.editWindow.switchRows(row, row - 1)
			self.setRangeSelectionByRow(row - 1)

	def moveRowDown(self):
		"""Move row down in SortTable
		"""
		row = self.getSelectedRowFromRanges()
		if row is not None:
			self.switchRows(row, row + 1)
			self.editWindow.switchRows(row, row + 1)
			self.setRangeSelectionByRow(row + 1)

	def handleRemoveRow(self):
		"""Handle removing currently selected row
		"""
		row = self.getSelectedRowFromRanges()
		if row is not None:
			self.removeRow(row)
			self.editWindow.removeRow(row)

	def createHeaders(self, header_labels):
		"""Create headers of the table

		Arguments:
			header_labels {List[str]} -- list of header names
		"""
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


class EditWindow(QtWidgets.QMainWindow):
	COVER_EDIT = 0
	COMMON_EDIT = 1
	GUESS_TAG_EDIT = 2
	GUESS_NAME_EDIT = 3

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

	def setup(self, mainWindow, property_2_name, property_2_tag, coverExtensions):
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
		self.parseAbrBox.currentIndexChanged.connect(self.handleParseAbrBoxPicked)
		self.valueAbrBox.currentIndexChanged.connect(self.handleValueAbrBoxPicked)
		self.parseLine.textChanged.connect(self.parseChanged)
		self.valueLine.textChanged.connect(self.valueChanged)
		self.digitsSpinBox.valueChanged.connect(self.refreshDataInTable)
		self.startIndexSpinBox.valueChanged.connect(self.refreshDataInTable)
		self.chooseImageButton.clicked.connect(self.handleChooseImageButton)
		self.removeImageButton.clicked.connect(self.handleRemoveImageButton)

		# Widgets for switching visibility
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
		self.abbreviations = OrderedDict({
			"fi": "Jméno souboru",
			"al": "Album",
			"ar": "Umělec",
			"sn": "Skladba",
			"tr": "Stopa",
			"ye": "Rok",
			"ge": "Žánr",
			"co": "Komentář",
			"d": "Číslice z widgetu",
		})
		self.abbrevationsDict: OrderedDict = OrderedDict({
			"fi": "fileName",
			"sn": "songName",
			"ar": "artist",
			"al": "album",
			"tr": "track",
			"ye": "year",
			"ge": "genre",
			"co": "comment",
		})
		self.property_2_name = property_2_name
		self.property_2_tag = property_2_tag
		self.coverExtensions = coverExtensions
		self.tags = [i for i in self.property_2_name if i != "cover"]
		self.parseBox.addItems(self.tags)
		self.parseAbrBox.addItems(["\\k" + key + "() - " + val for key, val in self.abbreviations.items()][:-1])
		self.valueAbrBox.addItems(["\\k" + key + " - " + val for key, val in self.abbreviations.items()])

	def exec(self, data: List, property=None, guess_tag=False, guess_name=False):
		self.data = data
		self.property = property
		self.guess_tag = guess_tag
		self.guess_name = guess_name
		self.setEditType(self.property, self.guess_tag, self.guess_name)

		self.init()

		self.mainWindow.setEnabled(False)
		super().show()

	def setEditType(self, property, guess_tag, guess_name):
		if guess_tag:
			self.editType = self.GUESS_TAG_EDIT
		elif guess_name:
			self.editType = self.GUESS_NAME_EDIT
		elif property == "cover":
			self.editType = self.COVER_EDIT
		elif property in self.property_2_name:
			self.editType = self.COMMON_EDIT

	def isGuessTagEdit(self):
		return self.editType == self.GUESS_TAG_EDIT

	def isGuessNameEdit(self):
		return self.editType == self.GUESS_NAME_EDIT

	def isCommonEdit(self):
		return self.editType == self.COMMON_EDIT

	def isCoverEdit(self):
		return self.editType == self.COVER_EDIT

	def initEditCoverWidgets(self):
		self.name = self.property_2_name[self.property]
		self.tag = self.property_2_tag[self.property]
		self.titleLabel.setText("Úprava položky: " + self.name)

		[i.setVisible(False) for i in self.commonTagsWidgets + self.guessTagsWidgets]
		[i.setVisible(True) for i in self.coverWidgets]

	def initEditGuessTagsWidgets(self):
		self.titleLabel.setText("Vytvoření tagů ze jména souboru")

		[i.setVisible(False) for i in self.commonTagsWidgets + self.coverWidgets]
		[i.setVisible(True) for i in self.guessTagsWidgets]

		self.parseLine.setEnabled(True)
		self.parseAbrBox.setEnabled(True)

	def initEditGuessNameWidgets(self):
		self.titleLabel.setText("Vytvoření jména souboru z tagů")

		[i.setVisible(False) for i in self.commonTagsWidgets + self.coverWidgets]
		[i.setVisible(True) for i in self.guessTagsWidgets]

		self.parseLine.setEnabled(True)
		self.parseAbrBox.setEnabled(True)

	def initEditCommonTagsWidgets(self):
		self.name = self.property_2_name[self.property]
		self.tag = self.property_2_tag[self.property]
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
		elif self.isGuessNameEdit():
			self.initEditGuessNameWidgets()
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

	def handleParseAbrBoxPicked(self, index):
		if index >= 0:
			self.parseAbrBox.setCurrentIndex(-1)
			if self.isGuessNameEdit():
				self.parseLine.setText(self.parseLine.text() + "\\k" + list(self.abbreviations.items())[index][0])
			else:
				self.parseLine.setText(self.parseLine.text() + "\\k" + list(self.abbreviations.items())[index][0] + "(.+?)")

	def handleValueAbrBoxPicked(self, index):
		if index >= 0:
			self.valueAbrBox.setCurrentIndex(-1)
			self.valueLine.setText(self.valueLine.text() + "\\k" + list(self.abbreviations.items())[index][0])

	def createHeaders(self):
		if self.isGuessTagEdit() or self.isGuessNameEdit():
			header_labels = [j for (i, j) in self.property_2_name.items() if i != "cover"]
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
					mp3file.tmpProperties[key] = mp3player.mp3window.MP3Tag(mp3file, key, mp3file.fileName)
					self.tableWidget.setItem(rowCount, idx, mp3file.tmpProperties[key])
				elif key != "cover":
					mp3file.tmpProperties[key] = mp3player.mp3window.MP3Tag(mp3file, key, "")
					self.tableWidget.setItem(rowCount, idx, mp3file.tmpProperties[key])
		elif self.isGuessNameEdit():
			# insert all other tags to table
			for idx, key in enumerate(mp3file.property_2_tag):
				if key == "fileName":
					mp3file.tmpProperties[key] = mp3player.mp3window.MP3Tag(mp3file, key, mp3file.fileName)
					self.tableWidget.setItem(rowCount, idx, mp3file.tmpProperties[key])
				elif key != "cover":
					mp3file.tmpProperties[key] = mp3player.mp3window.MP3Tag(mp3file, key, mp3file.__getattribute__(key).text())
					self.tableWidget.setItem(rowCount, idx, mp3file.tmpProperties[key])
		else:
			self.tableWidget.setItem(rowCount, 0, mp3player.mp3window.MP3Tag(mp3file, self.property, mp3file.__getattribute__(self.property).text()))
			mp3file.tmpProperties[self.property] = mp3player.mp3window.MP3Tag(mp3file, self.property, "Test")
			self.tableWidget.setItem(rowCount, 1, mp3file.tmpProperties[self.property])

	def removeRow(self, row):
		self.data.pop(row)
		self.refreshDataInTable()

	def switchRows(self, row1, row2):
		tmp = self.data[row1]
		self.data[row1] = self.data[row2]
		self.data[row2] = tmp

		self.refreshDataInTable()

	def searchString(self, pattern, inputString):
		for key in self.abbrevationsDict:
			prefix = re.escape("\\k{}(".format(key))
			suffix = re.escape(")")
			pattern = re.sub("{}(.*?){}".format(prefix, suffix), r"(?P<{}>\1)".format(key), pattern)
		return re.search(pattern, inputString)

	def subString(self, mp3file, inputString, group=None, idx=None):
		for key in self.abbrevationsDict:
			prefix = re.escape("\\k{}".format(key))
			inputString = re.sub(prefix, mp3file.getProperty(self.abbrevationsDict[key]), inputString)

		if idx is not None and isinstance(idx, int):
			inputString = re.sub(re.escape("\\kd"), str(self.startIndexSpinBox.value() + idx).zfill(self.digitsSpinBox.value()), inputString)
		return inputString

	def refreshDataInTable(self):
		if self.data is None:
			return

		for idx, mp3file in enumerate(self.data):
			if self.isGuessTagEdit():
				found = None
				try:
					found = self.searchString(self.parseLine.text(), mp3file.baseName)
				except Exception:
					pass
				for key in self.abbrevationsDict:
					if self.abbrevationsDict[key] != "fileName":
						try:
							mp3file.tmpProperties[self.abbrevationsDict[key]].setText(found.group(key))
						except (IndexError, AttributeError):
							mp3file.tmpProperties[self.abbrevationsDict[key]].setText("")
			elif self.isGuessNameEdit():
				try:
					fileName = self.subString(mp3file, self.parseLine.text(), idx=idx)
					mp3file.tmpProperties["fileName"].setText(fileName)
				except Exception:
					mp3file.tmpProperties["fileName"].setText("")
			else:
				if self.valueBox.currentIndex() == 0:
					mp3file.tmpProperties[self.property].setText(mp3file.getProperty(self.property))
				elif self.valueBox.currentIndex() == 1:
					mp3file.tmpProperties[self.property].setText(mp3file.getProperty(self.property).lower())
				elif self.valueBox.currentIndex() == 2:
					mp3file.tmpProperties[self.property].setText(mp3file.getProperty(self.property).upper())
				elif self.valueBox.currentIndex() == 3:
					mp3file.tmpProperties[self.property].setText(mp3file.getProperty(self.property).capitalize())
				elif self.valueBox.currentIndex() == 4:
					try:
						propertyValue = self.subString(mp3file, self.valueLine.text(), idx=idx)
						mp3file.tmpProperties[self.property].setText(propertyValue)
					except Exception:
						mp3file.tmpProperties[self.property].setText("")

		if self.tableWidget.rowCount() > 0:
			self.finishButton.setEnabled(True)
		else:
			self.finishButton.setEnabled(False)

	def validateChanges(self, fileNamesRelPath, fileNamesAbsPath):
		if self.property == "fileName" or self.isGuessNameEdit():
			for idx, mp3file in enumerate(self.data):
				if not mp3file.canRenameFilename(fileNamesRelPath[idx]) or fileNamesAbsPath.count(fileNamesAbsPath[idx]) > 1:
					QtWidgets.QMessageBox.warning(self, "NNelze přejmenovat soubory", "Nelze přejmenovat soubory, soubor \"{}\" již existuje, nebo by přejmenováním bylo vytvořeno více souborů se stejným názvem.".format(fileNamesRelPath[idx]))
					return False
		return True

	def saveChanges(self):
		if self.isGuessTagEdit():
			for idx, mp3file in enumerate(self.data):
				for property in mp3file.tmpProperties:
					value = mp3file.tmpProperties[property].text()
					if value != "":
						mp3file.saveTagToFile(property, value)
		elif self.isGuessNameEdit():
			# Rename file if needed
			fileNamesRelPath = [mp3file.tmpProperties[self.property].text() for mp3file in self.data]
			fileNamesAbsPath = [os.path.join(mp3file.baseDir, mp3file.tmpProperties[self.property].text()) for mp3file in self.data]
			if not self.validateChanges(fileNamesRelPath, fileNamesAbsPath):
				return False

			for mp3file in self.data:
				value = mp3file.tmpProperties["fileName"].text()
				if value != "":
					mp3file.saveTagToFile("fileName", value)
		else:
			fileNamesRelPath = [mp3file.tmpProperties[self.property].text() for mp3file in self.data]
			fileNamesAbsPath = [os.path.join(mp3file.baseDir, mp3file.tmpProperties[self.property].text()) for mp3file in self.data]
			if not self.validateChanges(fileNamesRelPath, fileNamesAbsPath):
				return False
			for mp3file in self.data:
				mp3file.saveTagToFile(self.property, mp3file.tmpProperties[self.property].text())
		return True

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
		path = QtWidgets.QFileDialog.getOpenFileName(self, "Select image cover", filter="images ({})".format(" ".join(["*." + i for i in self.coverExtensions])))[0]
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
		if self.saveChanges():
			self.mainWindow.redrawCoverImage()
			self.mainWindow.fillLineEdits()
			self.close()

	def handleCancelButton(self):
		self.close()
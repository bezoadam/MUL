import os
from collections import OrderedDict, defaultdict
from typing import Dict, Set, List
import random

import mutagen
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TPE1, TIT2, TRCK, TALB, APIC, TDRC, TCON, COMM
from PyQt5 import QtWidgets, uic, Qt, QtGui

class MP3Tag(QtWidgets.QTableWidgetItem):
	'''Custom QTableWidgetItem class for containing tag information

	Arguments:

		QtWidgets {QTableWidgetItem} -- Base class for MP3Tag
	'''

	def __init__(self, mp3file, tagIdentifier, text):
		'''Initializer for MP3Tag class

		It saves the parent class (MP3File class)

		Arguments:

			mp3file {MP3File} -- Wrapper class for wrapping all tags of MP3File
			tagIdentifier {str} -- Tag identifier (from mutagen library)
			text {str} -- Value of the widget item
		'''
		super(QtWidgets.QTableWidgetItem, self).__init__(text)
		self.mp3file = mp3file

	def getMP3File(self):
		'''Getter for mp3file

		Returns:

			MP3File -- parent MP3 file
		'''
		return self.mp3file


class MP3File(object):
	'''Wrapper class for wrapping all tags of MP3File and handling savings and loading (it's abstract for a row in TableWidget)

	Arguments:

		object {object} -- Base class
	'''
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
	property_2_tag: OrderedDict = OrderedDict({
		"fileName": "PATH",  # Not tag, just for general usage
		"songName": "TIT2",
		"artist": "TPE1",
		"album": "TALB",
		"track": "TRCK",
		"year": "TDRC",
		"genre": "TCON",
		"comment": "COMM",
		"cover": "APIC",
	})
	tag_2_property: OrderedDict = OrderedDict({
		"PATH": "fileName",  # Not tag, just for general usage
		"TIT2": "songName",
		"TPE1": "artist",
		"TALB": "album",
		"TRCK": "track",
		"TDRC": "year",
		"TCON": "genre",
		"COMM": "comment",
		"APIC": "cover",
	})
	coverExtensions = ["jpg", "jpeg", "gif", "png"]

	def __init__(self, path):
		'''Initializer for MP3File class

		Arguments:

			path {str} -- path to MP3 file
		'''
		super(object, self).__init__()

		self.path = path
		self.baseDir = os.path.dirname(self.path)
		self.baseName = os.path.basename(self.path)

		# Create tags and set empty strings as its value
		self.initProperties()

		# Load Tags from file
		self.fillTagsFromFile()

	def loadCoverImageFromFile(self):
		'''Method is loading cover image (QPixmap) to `image` property from file (by path)
		'''
		# Remove image
		self.image = None

		# Reload image from file
		audio = MP3(self.path, ID3=ID3)
		for key in audio.keys():
			for tag in self.tag_2_property:
				if tag in key:
					if tag == "APIC":
						self.loadCoverImageFromBytes(audio.tags.get(key).data)

	def loadCoverImageFromBytes(self, bytes):
		'''Method is loading cover image (QPixmap) from bytes

		Arguments:

			bytes {BytesIO} -- Bytes containing image (loaded from file or from tags data, or whatever)
		'''
		self.imageBytes = bytes
		self.image = QtGui.QPixmap.fromImage(QtGui.QImage.fromData(self.imageBytes))

	def removeCoverImageFromFile(self):
		'''Removes cover image from mp3file
		'''
		audio = MP3(self.path, ID3=ID3)
		keys = list(audio.keys())
		for key in keys:
			if "APIC" in key:
				audio.pop(key, None)
		audio.save(v2_version=4)
		del audio
		self.imageBytes = None
		self.image = None

	def fillTagsFromFile(self):
		'''Fill tags from file

		It's loading tags from mutagen library and saving it to MP3Tag class (which are this class properties accessed by __getattribute__)
		'''
		# Set correct filename (individual because it's not a tag)
		self.fileName.setText(self.baseName)

		# Load whole file
		audio = MP3(self.path, ID3=ID3)

		# Set correctly all tags
		for key in audio.keys():
			for tag in self.tag_2_property:
				if tag in key:
					if tag == "APIC":
						self.loadCoverImageFromBytes(audio.tags.get(key).data)
					else:
						self.__getattribute__(self.tag_2_property[tag]).setText(str(audio.tags[key].text[0]))

		# Set other informations which are not editable using this editor
		self.songLength = int(audio.info.length)
		self.songBitrate = audio.info.bitrate

		del audio

	def canBeSavedToFile(self, propertyName, propertyValue):
		# TODO
		pass

	def saveTagToFile(self, propertyName, propertyValue):
		'''Save individual tag to file using property name and property value

		Arguments:

			propertyName {[type]} -- [description]
			propertyValue {[type]} -- [description]
		'''
		# TODO add validation (And proper raising)
		# If it's fileName, process it differently
		if propertyName == "fileName":
			self.rename(propertyValue)
		# If it's cover image, process it also differently
		elif propertyName == "cover":
			self.saveCover(propertyValue)
		# Other tags can be processed commonly
		else:
			audio = MP3(self.path, ID3=ID3)
			tag = self.property_2_tag[propertyName]

			# If the tag is empty, remove existing tag or don't create an empty tag
			if propertyValue == "":
				if tag in audio:
					audio.pop(tag)
			else:
				audio[tag] = getattr(mutagen.id3, tag)(encoding=3, text=propertyValue)

			# Save it
			audio.save(v2_version=4)
			del audio

		# Finally make sure that the change is also fastforwarded to Text
		self.__getattribute__(propertyName).setText(str(propertyValue))

	def initProperties(self):
		'''Initialization of all tags and images
		'''
		self.imageBytes = None
		self.image = None
		for key in self.property_2_tag:
			self.__setattr__(key, MP3Tag(self, key, ""))
		self.tmpProperties: Dict = defaultdict(str)

	def canRenameFilename(self, newPath):
		'''Check if the new name of the file can be set (check existing files and empty strings)

		Arguments:

			newPath {str} -- New base name of a file

		Returns:

			bool -- True if can be renamed and False if can not
		'''
		return (not os.path.exists(os.path.join(self.baseDir, newPath)) or newPath == self.baseName) and newPath != ""

	def rename(self, newPath):
		'''Rename mp3 file

		Arguments:

			newPath {str} -- New base name of a file
		'''
		if newPath != self.baseName:
			os.renames(os.path.join(self.baseDir, self.baseName), os.path.join(self.baseDir, newPath))
			self.baseName = newPath
			self.path = os.path.join(self.baseDir, self.baseName)

	def hasCover(self):
		'''Method checks if file has a cover

		Returns:

			bool -- True if file has a cover, False if doesn't
		'''
		audio = MP3(self.path, ID3=ID3)
		for key in audio.keys():
			if "APIC" in key:
				return True
		return False

	def saveCover(self, coverPath):
		'''Save cover image to file

		Arguments:

			coverPath {str} -- Path to cover image
		'''
		# Init audio
		audio = MP3(self.path, ID3=ID3)

		# Remove cover images (do not remove cover if there's cover and coverPath is not set properly)
		if coverPath != "" or not self.hasCover():
			keys = list(audio.keys())
			for key in reversed(keys):
				if "APIC" in key:
					audio.pop(key, None)

		# Change mime type and load and save image
		if coverPath != "":
			extension = coverPath.split(".")[-1].lower()
			if extension == "jpg":
				extension = "jpeg"
			mime = "image/" + extension

			with open(coverPath, "rb") as coverFile:
				img = coverFile.read()
				audio['APIC'] = APIC(
					encoding=3,
					mime=mime,
					type=3,
					data=img
				)
				self.loadCoverImageFromBytes(img)
		audio.save(v2_version=4)
		del audio


class MP3Table(QtWidgets.QTableWidget):
	'''Custom QTableWidget wrapping mp3 file

	Arguments:

		QtWidgets {QTableWidget} -- Base class

	Returns:

		MP3Table -- instance of MP3Table
	'''
	HEADER_CHECK_EMPTY = "[_]"
	HEADER_CHECK_CHECKED = "[X]"

	def __init__(self, *args):
		'''Initializer of MP3Table
		'''
		super(QtWidgets.QTableWidget, self).__init__(*args)

	def setup(self, mainWindow):
		'''Setup function for connecting parent widgets with child widgets

		Arguments:

			mainWindow {QtWidgets.QMainWindow} -- Main window of whole application
		'''
		# Init
		self.mainWindow = mainWindow
		self.createHeaders()

		# Handlers
		self.horizontalHeader().sectionClicked.connect(self.handleHeaderClicked)
		self.cellClicked.connect(self.handleCellClick)

		# Properties
		self.lastSelectedRow = None
		self.lastOrderedColumn = None
		self.lastOrder = None
		self.checkedRows: List = list()

	def isEmpty(self):
		'''Checks if table is empty

		Returns:

			bool -- True if empty, False if not
		'''
		return self.rowCount() == 0

	def checkedRowsCount(self):
		'''Number of checked rows in this table

		Returns:

			int -- Number of checked rows
		'''
		return len(self.checkedRows)

	def getMP3File(self, row):
		'''Get mp3 file wrapper from this table

		Arguments:

			row {int} -- Row to get a mp3 file

		Returns:

			MP3File -- MP3File
		'''
		return self.item(row, 1).mp3file

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

	def activateRow(self, row):
		'''Activate row of MP3Player

		Arguments:

			row {int} -- Row which should be activated
		'''
		self.lastSelectedRow = row
		self.mainWindow.setMediaFileFromRow(self.lastSelectedRow)

	def handleCellClick(self, row, col):
		'''Handle cell click in the QTableWidget

		Arguments:

			row {int} -- Row of the clicked cell
			col {int} -- Column of the clicked cell
		'''
		# If tag was clicked
		if col > 0:
			selectedRow = self.getSelectedRowFromRanges()
			if selectedRow is not None:
				self.activateRow(selectedRow)
		# If checkbox was clicked
		if col == 0:
			self.toggleRowCheckBox(row)

	def setRangeSelectionByRow(self, row=None):
		'''Set RangeSelected according to the single row given (if not given set it by actual selected row)

		Keyword Arguments:

			row {int} -- Row index which range should be selected (default: {None})
		'''
		row = self.lastSelectedRow if row is None else row
		self.setRangeSelected(QtWidgets.QTableWidgetSelectionRange(0, 0, self.rowCount() - 1, self.columnCount() - 1), False)
		if row is not None:
			self.setRangeSelected(QtWidgets.QTableWidgetSelectionRange(row, 0, row, self.columnCount() - 1), True)

	def activateNextRow(self, deterministic=True):
		'''Activate next row (mp3file)

		Keyword Arguments:

			deterministic {bool} -- Whether to shuffle or not (default: {True})
		'''
		# If MP3 player is not empty
		if not self.isEmpty():
			if self.lastSelectedRow is None:
				self.lastSelectedRow = 0 if deterministic else random.randint(0, self.rowCount() - 1)
			else:
				self.lastSelectedRow = (self.lastSelectedRow + 1) % self.rowCount() if deterministic else (self.lastSelectedRow + random.randint(0, self.rowCount() - 1)) % self.rowCount()

			self.mainWindow.setMediaFileFromRow(self.lastSelectedRow)

	def activatePreviousRow(self, deterministic=True):
		'''Activate previous row (mp3file)

		Keyword Arguments:

			deterministic {bool} -- Whether to shuffle or not (default: {True})
		'''
		# If MP3 player is not empty
		if not self.isEmpty():
			if self.lastSelectedRow is None:
				self.lastSelectedRow = 0 if deterministic else random.randint(0, self.rowCount() - 1)
			else:
				self.lastSelectedRow = (self.lastSelectedRow - 1) % self.rowCount() if deterministic else (self.lastSelectedRow + random.randint(0, self.rowCount() - 1)) % self.rowCount()

			self.mainWindow.setMediaFileFromRow(self.lastSelectedRow)

	def getCheckBox(self, row):
		'''Get Checkbox by row

		Arguments:

			row {int} -- Checkbox's row which we should get

		Returns:

			QtWidgets.QTableWidgetItem -- Checkbox
		'''
		return self.item(row, 0)

	def unCheckRow(self, row):
		'''Uncheck row

		Arguments:

			row {int} -- Which row should be unchecked
		'''
		item = self.getCheckBox(row)
		if item in self.checkedRows:
			self.checkedRows.remove(item)
		item.setCheckState(Qt.Qt.Unchecked)

		self.updateCheckHeader()
		self.mainWindow.updateFilesCheckedLabel()

	def checkRow(self, row):
		'''Check row

		Arguments:

			row {int} -- Which row should be checked
		'''
		item = self.getCheckBox(row)
		if item not in self.checkedRows:
			self.checkedRows.append(item)
		item.setCheckState(Qt.Qt.Checked)

		self.updateCheckHeader()
		self.mainWindow.updateFilesCheckedLabel()

	def toggleRowCheckBox(self, row):
		'''Toggle check on the item specified by row

		Arguments:

			row {int} -- Checkbox's row
		'''
		item = self.getCheckBox(row)
		if item not in self.checkedRows:
			self.checkRow(row)
		else:
			self.unCheckRow(row)

	def checkAllRows(self):
		'''Check all rows
		'''
		for i in range(self.rowCount()):
			self.checkRow(i)

	def unCheckAllRows(self):
		'''Uncheck all rowy
		'''
		for i in range(self.rowCount()):
			self.unCheckRow(i)

	def getCheckedMP3Files(self):
		'''Get all checked mp3 files

		Returns:

			List[MP3File] -- List of MP3File
		'''
		mp3files = [self.getMP3File(i.row()) for i in self.checkedRows]
		return mp3files

	def removeCheckedMP3Files(self):
		'''Remove checked mp3 files (checked rows)
		'''
		for item in sorted(self.checkedRows, key=lambda x: x.row(), reverse=True):
			self.removeMP3(item.row())

	def removeMP3(self, row):
		'''Remove mp3 file (row from table)

		Arguments:

			row {int} -- Row index
		'''
		# Check if the row is in the table
		if row < self.rowCount():
			self.unCheckRow(row)
			self.removeRow(row)

			# If the table will be empty
			if self.isEmpty():
				self.lastSelectedRow = None
				self.mainWindow.setMediaFileFromRow(self.lastSelectedRow)

			# If removed row was before selected row decrease index
			elif self.lastSelectedRow is not None and self.lastSelectedRow > row:
				self.lastSelectedRow -= 1

			# If removed row was selected row decrease index and reload media file
			elif self.lastSelectedRow is not None and self.lastSelectedRow == row:
				self.lastSelectedRow -= 1
				self.mainWindow.setMediaFileFromRow(self.lastSelectedRow)

	def updateCheckHeader(self):
		'''Update checkbox header
		'''
		if self.checkedRowsCount() == self.rowCount():
			self.horizontalHeaderItem(0).setText(self.HEADER_CHECK_CHECKED)
		else:
			self.horizontalHeaderItem(0).setText(self.HEADER_CHECK_EMPTY)

	def createHeaders(self):
		'''Create headers of table
		'''
		header_labels = [self.HEADER_CHECK_EMPTY] + [j for (i, j) in MP3File.property_2_name.items() if i != "cover"]
		self.setColumnCount(len(header_labels))
		self.setHorizontalHeaderLabels(header_labels)
		self.setFocusPolicy(Qt.Qt.NoFocus)
		self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
		self.setColumnWidth(0, 20)

	def addMP3(self, mp3file):
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

	def reorderItemsByLastOrder(self):
		'''Reorder items in the table again by using last order
		'''
		if self.lastOrderedColumn is None or self.lastOrder is None:
			self.horizontalHeader().setSortIndicatorShown(False)
		else:
			self.horizontalHeader().setSortIndicatorShown(True)
			self.horizontalHeader().setSortIndicator(self.lastOrderedColumn, self.lastOrder)
			self.sortItems(self.lastOrderedColumn, order=self.lastOrder)

	def sortItems(self, column, order=Qt.Qt.AscendingOrder):
		'''Overriden method of sortItems for saving last ordered column and order type, also for managing select range and index of actual media

		Arguments:

			column {int} -- Column by which it should be order

		Keyword Arguments:

			order {Qt.Qt.QOrder} -- Order type (default: {Qt.Qt.AscendingOrder})
		'''
		self.lastOrderedColumn = column
		self.lastOrder = order

		super().sortItems(column, order=order)

		row = self.getSelectedRowFromRanges()
		if row is not None:
			self.lastSelectedRow = row

	def handleHeaderClicked(self, column):
		'''Handle header clicked (checkbox vs. sorting)

		Arguments:

			column {int} -- Header index clicked
		'''
		# If checkbox is clicked
		if column == 0:
			if self.checkedRowsCount() == self.rowCount():
				self.unCheckAllRows()
			else:
				self.checkAllRows()
			self.reorderItemsByLastOrder()
		else:
			self.horizontalHeader().setSortIndicatorShown(True)
			if self.horizontalHeader().sortIndicatorOrder() == Qt.Qt.AscendingOrder:
				self.horizontalHeader().setSortIndicator(column, Qt.Qt.AscendingOrder)
				self.sortItems(column, order=Qt.Qt.AscendingOrder)
			else:
				self.horizontalHeader().setSortIndicator(column, Qt.Qt.DescendingOrder)
				self.sortItems(column, order=Qt.Qt.DescendingOrder)